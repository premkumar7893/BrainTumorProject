import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import pandas as pd
import numpy as np

def evaluate_performance(y_true, y_pred, model_name):
    """Prints evaluation metrics for a model."""
    print(f"\n--- {model_name} Performance Report ---")
    
    # Isolation Forest predicts -1 for anomalies and 1 for normal.
    # Our target y_true is 0 for normal and 1 for attack.
    # Convert y_pred if it's from Isolation Forest
    if model_name == "Isolation Forest":
        # IF: 1 -> normal(0), -1 -> attack(1)
        y_pred = np.where(y_pred == 1, 0, 1)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    
    return {"acc": acc, "prec": prec, "rec": rec, "f1": f1}, y_pred

def plot_cm(y_true, y_pred, model_name):
    """Generates and saves a confusion matrix plot."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', 
                xticklabels=['Normal', 'Attack'], 
                yticklabels=['Normal', 'Attack'])
    plt.title(f'Confusion Matrix: {model_name}')
    plt.ylabel('Ground Truth')
    plt.xlabel('Predicted Label')
    filename = f"{model_name.replace(' ', '_').lower()}_cm.png"
    plt.savefig(filename)
    print(f"Visualization saved: {filename}")
    plt.close()

def plot_importance(model, feature_names):
    """Plots top 10 feature importances from Random Forest."""
    if not hasattr(model, 'feature_importances_'):
        print("Model does not support feature importance.")
        return
        
    importances = model.feature_importances_
    indices = np.argsort(importances)[-10:]
    
    plt.figure(figsize=(10,6))
    plt.title('Top 10 Discriminative Features (Random Forest)')
    plt.barh(range(len(indices)), importances[indices], color='teal', align='center')
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel('Relative Importance Density')
    filename = "feature_importance.png"
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Visualization saved: {filename}")
    plt.close()

def plot_comparison(results_dict):
    """Plots a bar chart comparing models across metrics."""
    df = pd.DataFrame(results_dict).T
    df.plot(kind='bar', figsize=(10,6), colormap='plasma')
    plt.title('Model Comparison: Supervised vs Unsupervised')
    plt.ylabel('Score (0.0 to 1.0)')
    plt.xticks(rotation=0)
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    filename = "model_comparison.png"
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Visualization saved: {filename}")
    plt.close()
