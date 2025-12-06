from orion.data import load_signal
from orion.data import load_anomalies
from orion import Orion
import pandas as pd

# load_test_data('multivariate/S-1')
def run_model():
    features = [" Source IP",
                " Destination IP",
                " Timestamp",
                " Flow Duration",
                " Total Fwd Packets",
                " Total Backward Packets",
                " Fwd Packet Length Mean",
                " Bwd Packet Length Mean"]

    # Things were never meant to be this way
    # We don't have access to OpenSearch anymore so our data isn't as high quality
    data = load_csv('./data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv', features)
    data = data.rename(columns={' Timestamp': 'Original_Timestamp'})
    data['Minute_Floor'] = data['Original_Timestamp'].dt.floor('min')

    def apply_synthetic_timestamp(group):
        N = len(group)

        time_step = pd.Timedelta(60 / N, unit='s')

        start_time = group['Minute_Floor'].iloc[0]
        new_timestamps = [start_time + i * time_step for i in range(N)]

        group['New_Timestamp'] = new_timestamps
        return group

    # Give seconds to each group of minutes
    data_redistributed = data.groupby('Minute_Floor', group_keys=False).apply(apply_synthetic_timestamp)
    data_redistributed = data_redistributed.drop(columns=['Original_Timestamp', 'Minute_Floor'])
    data_redistributed = data_redistributed.rename(columns={'New_Timestamp': 'Timestamp'})

    print(data_redistributed.head())
    #USE IMPUTER
    hyperparameters = {
        "mlstars.custom.timeseries_preprocessing.rolling_window_sequences#1": {
            'window_size': 150,
            'target_column': 0
        },
        'orion.primitives.tadgan.TadGAN#1': {
            'epochs': 3,
            'verbose': True,
            'input_shape': [150, features.size]
        }
    }

    orion = Orion(
        pipeline='tadgan',
        hyperparameters=hyperparameters
    )

    orion.fit(data)
    new_data = load_signal('multivariate/S-1')
    anomalies = orion.detect(new_data)
    ground_truth = load_anomalies('S-1')
    scores = orion.evaluate(new_data, ground_truth)
    print(anomalies)
    print(scores)


def load_test_data(name):
    return load_signal(name)


def load_csv(path, features):
    return pd.read_csv(path, header=0, usecols=features,
                       parse_dates=[" Timestamp"])


if __name__ == "__main__":
    run_model()
