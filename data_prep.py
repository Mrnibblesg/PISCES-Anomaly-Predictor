import pandas as pd

df = pd.read_csv('datafolder/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv')

# Print all column names
print("Column names in your CSV:")
print(df.columns.tolist())

# Also display the first few rows to see the data
print("\nFirst few rows:")
print(df.head())



# Parse the timestamp (assuming format is DD/MM/YY HH:MM)
df['Timestamp'] = pd.to_datetime(df[' Timestamp'])

# Sort by timestamp
df = df.sort_values('Timestamp')

print(df.head())



# Select only the columns we want
#selected_cols = ['Timestamp', ' Flow Duration', ' Total Fwd Packets', ' Total Backward Packets', 'Total Length of Fwd Packets', ' Total Length of Bwd Packets']
selected_cols = ['Timestamp', ' Flow Duration']
df_filtered = df[selected_cols]

print(df_filtered.head())
#print(df_filtered)