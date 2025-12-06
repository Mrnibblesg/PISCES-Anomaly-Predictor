import pandas as pd
import numpy as np
from orion import Orion
import matplotlib.pyplot as plt

df = pd.read_csv('datafolder/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv')

# Print all column names
print("Column names in your CSV:")
print(df.columns.tolist())

# Also display the first few rows to see the data
print("\nFirst few rows:")
print(df.head())

#df.columns = df.columns.str.strip()
df['Timestamp'] = pd.to_datetime(df[' Timestamp'])
df = df.sort_values('Timestamp')

# ===== STEP 2: Create Time Series =====
# Count flows per minute
time_series = df.groupby(pd.Grouper(key='Timestamp', freq='1min')).size().reset_index()
time_series.columns = ['timestamp', 'Flow Duration']
time_series = time_series.set_index('timestamp').asfreq('1min', fill_value=0).reset_index()

print(f"Time series created: {len(time_series)} data points")

# ===== STEP 3: Split Data =====
split_point = int(len(time_series) * 0.7)
train_data = time_series[:split_point]
test_data = time_series[split_point:]

# ===== STEP 4: Configure TadGAN =====
hyperparameters = {
    'orion.primitives.tadgan.TadGAN#1': {
        'epochs': 50,
        'window_size': 100,
        'batch_size': 64,
        'verbose': True
    }
}

# ===== STEP 5: Train =====
orion = Orion(pipeline='tadgan', hyperparameters=hyperparameters)
print("Training TadGAN...")
orion.fit(train_data)

# ===== STEP 6: Detect =====
print("Detecting anomalies...")
anomalies = orion.detect(test_data)
print(f"\nAnomalies detected: {len(anomalies)}")
print(anomalies)

# ===== STEP 7: Visualize =====
plt.figure(figsize=(15, 6))
plt.plot(test_data['timestamp'], test_data['value'], label='Traffic', alpha=0.7)

for idx, row in anomalies.iterrows():
    start = pd.to_datetime(row['start'], unit='s')
    end = pd.to_datetime(row['end'], unit='s')
    plt.axvspan(start, end, alpha=0.3, color='red', 
               label='Anomaly' if idx == 0 else '')

plt.xlabel('Time')
plt.ylabel('Flow Count')
plt.title('Network Anomaly Detection')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()