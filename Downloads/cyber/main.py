import numpy as np
import pandas as pd
from preprocess import load_and_preprocess_data
from models import train_supervised, train_unsupervised, save_object
from evaluate import evaluate_performance, plot_cm, plot_importance, plot_comparison
import os

def run_project():
    print("="*50)
    print("AI-BASED NETWORK THREAT IDENTIFICATION SYSTEM")
    print("="*50)

    # 1. Data Loading and Preprocessing
    X_train, X_test, y_train, y_test, feature_names, scaler, encoders = load_and_preprocess_data()
    
    # 2. Model Development
    # Supervised: Random Forest
    rf_model = train_supervised(X_train, y_train)
    
    # Unsupervised: Isolation Forest
    if_model = train_unsupervised(X_train)

    # 3. Model Evaluation
    # Evaluate Random Forest
    rf_preds = rf_model.predict(X_test)
    rf_metrics, _ = evaluate_performance(y_test, rf_preds, "Random Forest")
    
    # Evaluate Isolation Forest
    if_raw_preds = if_model.predict(X_test)
    if_metrics, if_preds = evaluate_performance(y_test, if_raw_preds, "Isolation Forest")

    # 4. Visualization & Reporting
    print("\nStep 5: Generating Visualization Reports...")
    plot_cm(y_test, rf_preds, "Random Forest")
    plot_cm(y_test, if_preds, "Isolation Forest")
    plot_importance(rf_model, feature_names)
    
    results = {
        "Random Forest": rf_metrics,
        "Isolation Forest": if_metrics
    }
    plot_comparison(results)

    # 5. Saving Artifacts for Simulation
    print("\nStep 6: Saving Models for Real-Time Simulation...")
    save_object(rf_model, "network_rf_model.pkl")
    save_object(scaler, "network_scaler.pkl")
    save_object(feature_names, "feature_names.pkl")
    
    # Saving a sample of data for the simulator to play with
    test_sample = pd.DataFrame(X_test, columns=feature_names)
    test_sample['target'] = y_test
    test_sample.to_csv("simulation_traffic.csv", index=False)
    
    print("\n" + "="*50)
    print("Project Execution Completed Successfully.")
    print("="*50)

if __name__ == "__main__":
    run_project()
