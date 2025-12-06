from orion.data import load_signal
from orion.data import load_anomalies
from orion import Orion
import pandas as pd

def run_model():
    features = [" Timestamp",
                " Flow Duration",
                " Total Fwd Packets",
                " Total Backward Packets",
                " Fwd Packet Length Mean",
                " Bwd Packet Length Mean"]

    # Things were never meant to be this way
    # We don't have access to OpenSearch anymore so our data isn't as high quality
    data = load_csv('./data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv', features)

    # Give seconds to each group of minutes
    #data_redistributed = data.groupby('Minute_Floor', group_keys=False).apply(apply_synthetic_timestamp)
    #data_redistributed = data_redistributed.drop(columns=['Original_Timestamp', 'Minute_Floor'])
    #data_redistributed = data_redistributed.rename(columns={'New_Timestamp': 'timestamp'})
    
    print(data.head())
    print(data.dtypes)
    epoch = pd.Timestamp("1970-01-01 00:00:00")
    data[" Timestamp"] = (data[" Timestamp"] - epoch).dt.total_seconds()
    new_columns = ["timestamp"]
    new_columns.extend(features[1:])
    print(new_columns)
    data.columns = ['timestamp', '0', '1', '2', '3', '4']
    print(data.head())

    #data_redistributed['timestamp'] = (['timestamp'].astype(int) / 10**9).astype(int)

    hyperparameters = {
        'orion.primitives.tadgan.TadGAN#1': {
            'epochs': 3,
            'verbose': True,
            'input_shape': (150, 5),
            'target_shape': (150, 1)
        }
    }

    orion = Orion(
        pipeline='tadgan',
        hyperparameters=hyperparameters
    )
    #print(data.iloc[:300,:].shape)
    print(type(data))
    print(type(S1))
    print(data.head())
    print("S1: ", S1.head())
    print(S1.columns)
    orion.fit(data[:300])
    new_data = load_signal('multivariate/S-1')
    anomalies = orion.detect(new_data)
    ground_truth = load_anomalies('S-1')
    scores = orion.evaluate(new_data, ground_truth)
    print(anomalies)
    print(scores)


def load_test_data(name):
    return load_signal(name)


S1 = load_test_data('multivariate/S-1')
def load_csv(path, features):
    return pd.read_csv(path, header=0, usecols=features,
                       parse_dates=[" Timestamp"])


if __name__ == "__main__":
    run_model()
