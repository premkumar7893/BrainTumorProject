import pandas as pd
import numpy as np
import time
from models import load_object

def simulate_traffic():
    """
    Simulates real-time network traffic by reading samples from 
    the simulation_traffic.csv file and predicting their nature.
    """
    print("\n" + "*"*40)
    print("   NETWORK TRAFFIC SIMULATOR (REAL-TIME)")
    print("*"*40)

    # Load resources
    model = load_object("network_rf_model.pkl")
    scaler = load_object("network_scaler.pkl")
    data = pd.read_csv("simulation_traffic.csv")
    
    if model is None or scaler is None or data is None:
        print("Error: Model or Data files not found. Please run main.py first.")
        return

    target = data['target']
    features = data.drop(columns=['target'])

    print(f"\nMonitoring Traffic... [Press Ctrl+C to Stop]\n")
    print("-" * 60)
    print(f"{'Packet ID':<12} | {'Actual Status':<15} | {'AI Prediction':<15}")
    print("-" * 60)

    try:
        for i in range(15): # Simulate 15 packets for demonstration
            # Select a random packet
            idx = np.random.randint(0, len(features))
            sample = features.iloc[[idx]]
            actual = "ATTACK" if target.iloc[idx] == 1 else "NORMAL"
            
            # AI Inference
            pred_numeric = model.predict(sample.values)[0]
            prediction = "ATTACK" if pred_numeric == 1 else "NORMAL"
            
            # Display results
            status_tag = "[ALERT]" if prediction == "ATTACK" else "[SAFE]"
            print(f"PKT_{1000+i:<8} | {actual:<15} | {status_tag} {prediction:<15}")
            
            # Simulate real-time delay
            time.sleep(1.0)
            
        print("-" * 60)
        print("\nSimulation Session Completed.")
        
    except KeyboardInterrupt:
        print("\nSimulator Stopped by User.")

if __name__ == "__main__":
    simulate_traffic()
