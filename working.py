from orion import Orion
import pandas as pd
import numpy as np

def load_csv(path, features):
    """Load CSV with specified features and parse timestamp"""
    df = pd.read_csv(
        path, 
        header=0, 
        usecols=features,
        parse_dates=[" Timestamp"],
        date_format="%m/%d/%Y %H:%M"
    )
    return df

def run_model():
    # Define features to extract from CSV
    features = [
        " Timestamp",
        " Flow Duration",
        " Total Fwd Packets",
        " Total Backward Packets",
        " Fwd Packet Length Mean",
        " Bwd Packet Length Mean"
    ]
    
    # Load data
    data = load_csv('datafolder/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv', features)
    
    print("Original data shape:", data.shape)
    print("Original data head:")
    print(data.head())
    print("\nData types:")
    print(data.dtypes)
    
    # Convert timestamp to Unix epoch seconds
    epoch = pd.Timestamp("1970-01-01 00:00:00")
    data[" Timestamp"] = (data[" Timestamp"] - epoch).dt.total_seconds()
    
    # Rename columns to match Orion's expected format
    # Orion expects: 'timestamp' column + value columns
    data.columns = ['timestamp', 'value_0', 'value_1', 'value_2', 'value_3', 'value_4']
    
    # Sort by timestamp to ensure temporal order
    data = data.sort_values('timestamp').reset_index(drop=True)
    
    print("\nProcessed data head:")
    print(data.head())
    print("Processed data shape:", data.shape)
    
    # TadGAN hyperparameters for multivariate data
    hyperparameters = {
        # Time aggregation primitive - makes signal equi-spaced
        "mlstars.custom.timeseries_preprocessing.time_segments_aggregate#1": {
            "time_column": "timestamp",
            "interval": 1,  # 1 second intervals (adjust based on your data)
            "method": "mean"
        },
        # MinMaxScaler - scale values between -1 and 1
        'sklearn.preprocessing.MinMaxScaler#1': {
            'feature_range': (-1, 1)
        },
        # Rolling window primitive - creates sequences
        'mlstars.custom.timeseries_preprocessing.rolling_window_sequences#1': {
            'target_column': 0,  # Which column to use as target
            'window_size': 100   # Size of sliding window
        },
        # TadGAN model configuration
        'orion.primitives.tadgan.TadGAN#1': {
            'epochs': 5,  # Start with 5 for testing, increase to 35-50 for production
            'verbose': True,
            'batch_size': 64,
            'learning_rate': 0.005,
            'latent_dim': 20,
            'iterations_critic': 5
        },
        # Anomaly scoring primitive
        'orion.primitives.tadgan.score_anomalies#1': {
            'rec_error_type': 'point',  # or 'dtw' for dynamic time warping
            'comb': 'mult',  # multiplication combination of errors
            'lambda_rec': 0.5
        }
    }
    
    # Initialize Orion with TadGAN pipeline
    orion = Orion(
        pipeline='tadgan',
        hyperparameters=hyperparameters
    )
    
    # Check data size
    min_rows = 10000
    if len(data) < min_rows:
        print(f"\nWarning: Dataset has {len(data)} rows")
        print(f"TadGAN works best with at least {min_rows} rows")
        print(f"Results may not be optimal with limited data")
    
    # Train the model
    print(f"\nTraining TadGAN on {len(data)} rows...")
    print("This may take several minutes...")
    orion.fit(data)
    
    # Detect anomalies
    print("\nDetecting anomalies...")
    anomalies = orion.detect(data)
    
    print("\nDetected anomalies:")
    print(anomalies)
    print(f"\nTotal anomaly intervals detected: {len(anomalies)}")
    
    # Save the model (optional)
    # orion.save('tadgan_model.pkl')
    
    return orion, anomalies, data

if __name__ == "__main__":
    orion_model, detected_anomalies, processed_data = run_model()
    
    # Optional: Visualize results 
    try:
        import matplotlib.pyplot as plt
        
        # Plot the first feature with anomalies
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # Plot Feature 0
        axes[0].plot(processed_data['timestamp'], processed_data['value_0'], 
                     label='Flow Duration', linewidth=0.5)
        for idx, row in detected_anomalies.iterrows():
            axes[0].axvspan(row['start'], row['end'], color='red', alpha=0.3)
        axes[0].set_ylabel('Flow Duration')
        axes[0].set_title('Time Series with Detected Anomalies (Red regions)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot Feature 1
        axes[1].plot(processed_data['timestamp'], processed_data['value_1'], 
                     label='Total Fwd Packets', linewidth=0.5)
        for idx, row in detected_anomalies.iterrows():
            axes[1].axvspan(row['start'], row['end'], color='red', alpha=0.3)
        axes[1].set_xlabel('Timestamp')
        axes[1].set_ylabel('Total Fwd Packets')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('anomalies_plot.png', dpi=150)
        print("\nPlot saved as 'anomalies_plot.png'")
        plt.close()
        
    except ImportError:
        print("\nMatplotlib not available for visualization")
    except Exception as e:
        print(f"\nCould not create plot: {e}")