from orion.data import load_signal
train_data = load_signal('S-1-train')
print(train_data.size)
print(train_data.ndim)
print(train_data.head())

from orion import Orion
orion = Orion()
hyperparameters = {
    'keras.Sequential.LSTMTimeSeriesRegressor#1': {
        'epochs': 5
    }
}
orion = Orion(
    pipeline='lstm_dynamic_threshold',
    hyperparameters=hyperparameters
)
orion.fit(train_data)

# Load data to compare against ground-truth
new_data = load_signal('S-1-new')
anomalies = orion.detect(new_data)

from orion.data import load_anomalies
ground_truth = load_anomalies('S-1')

scores = orion.evaluate(new_data, ground_truth)

print(anomalies)
print(scores)
