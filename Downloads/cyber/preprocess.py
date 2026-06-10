import pandas as pd
import numpy as np
from sklearn.datasets import fetch_kddcup99
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os

def load_and_preprocess_data():
    """
    Fetches KDD Cup 99 dataset and performs preprocessing:
    1. Labeling 'normal' as 0 and all attacks as 1.
    2. Encoding categorical features.
    3. Handling missing values (if any).
    4. Feature scaling.
    """
    print("Step 1: Fetching KDD Cup 99 dataset (10% subset for demo)...")
    # Fetching the 10% subset which is standard for research/demos
    data = fetch_kddcup99(subset=None, percent10=True, random_state=42)
    
    X = pd.DataFrame(data.data)
    y = data.target
    
    # Features in KDD Cup 99
    feature_names = [
        "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes",
        "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in",
        "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations",
        "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login",
        "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate",
        "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate",
        "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count",
        "dst_host_same_srv_rate", "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
        "dst_host_srv_diff_host_rate", "dst_host_serror_rate", "dst_host_srv_serror_rate",
        "dst_host_rerror_rate", "dst_host_srv_rerror_rate"
    ]
    X.columns = feature_names

    # Convert bytes to strings if necessary
    for col in X.columns:
        if isinstance(X[col].iloc[0], bytes):
            X[col] = X[col].str.decode('utf-8')
            
    # Step 2: Handle Categorical Encoding
    print("Step 2: Encoding categorical features...")
    categorical_cols = ['protocol_type', 'service', 'flag']
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        label_encoders[col] = le

    # Step 3: Target Label Processing
    print("Step 3: Processing target labels (Normal vs Attack)...")
    y = np.array([val.decode('utf-8') if isinstance(val, bytes) else val for val in y])
    y_binary = np.where(y == 'normal.', 0, 1) # 0: Normal, 1: Attack

    # Step 4: Split and Scale
    print("Step 4: Splitting and scaling data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y_binary, test_size=0.3, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, feature_names, scaler, label_encoders

if __name__ == "__main__":
    X_train, X_test, y_train, y_test, names, scaler, encoders = load_and_preprocess_data()
    print(f"Preprocessing complete.")
    print(f"Training set size: {X_train.shape}")
    print(f"Testing set size: {X_test.shape}")
    print(f"Target classes: {np.unique(y_train)} (0: Normal, 1: Attack)")
