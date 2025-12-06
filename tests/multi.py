from orion.data import load_signal
from orion.data import load_anomalies

signal_path = 'multivariate/S-1'

data = load_signal(signal_path)
print(data.head())

from orion import Orion

hyperparameters = {
    "mlstars.custom.timeseries_preprocessing.rolling_window_sequences#1": {
        'window_size': 150,
        'target_column': 0
    },
    'orion.primitives.tadgan.TadGAN#1': {
        'epochs': 1,
        'verbose': True,
        'input_shape': [150, 25]
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
