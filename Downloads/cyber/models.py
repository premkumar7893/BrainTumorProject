from sklearn.ensemble import RandomForestClassifier, IsolationForest
import pickle
import os

def train_supervised(X_train, y_train):
    """
    Trains a Random Forest classifier.
    Chosen for supervised learning because it handles high-dimensional network data 
    well and provides robust feature importance metrics.
    """
    print("\n[Supervised] Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    return rf

def train_unsupervised(X_train):
    """
    Trains an Isolation Forest.
    Chosen for unsupervised learning because it isolates anomalies (attacks) 
    by randomly selecting a feature and then randomly selecting a split value.
    In network security, this is useful when attack labels are missing.
    """
    print("\n[Unsupervised] Training Isolation Forest...")
    # 'auto' contamination allows the model to estimate the fraction of anomalies
    iso_forest = IsolationForest(contamination='auto', random_state=42, n_jobs=-1)
    iso_forest.fit(X_train)
    return iso_forest

def save_object(obj, filename):
    """Saves any object (model, scaler, etc.) to a file."""
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
    print(f"Saved: {filename}")

def load_object(filename):
    """Loads an object from a file."""
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as f:
        return pickle.load(f)
