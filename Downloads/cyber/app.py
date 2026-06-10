"""
CyberGuard AI - Flask Backend
AI-Based Network Threat Identification System
Serves the frontend dashboard and exposes REST API endpoints.
Run with: python app.py
"""

from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import socket
from models import load_object
from evaluate import evaluate_performance

# ── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder='frontend/static', template_folder='frontend')
CORS(app)  # Allow cross-origin requests from any device on the LAN

# ── Global State ───────────────────────────────────────────────────────────────
MODEL        = None
SCALER       = None
DATA         = None
FEATURE_NAMES = None
METRICS      = {}

# ── Resource Loader ────────────────────────────────────────────────────────────
def load_resources():
    """Load trained models, scaler, feature names, and simulation data at startup."""
    global MODEL, SCALER, DATA, FEATURE_NAMES, METRICS

    print("\n[CyberGuard] Loading models and data...")

    MODEL         = load_object("network_rf_model.pkl")
    SCALER        = load_object("network_scaler.pkl")
    FEATURE_NAMES = load_object("feature_names.pkl")

    if MODEL:
        print("[CyberGuard] ✓ Random Forest model loaded.")
    else:
        print("[CyberGuard] ✗ Model not found. Run main.py first.")

    if os.path.exists("simulation_traffic.csv"):
        DATA = pd.read_csv("simulation_traffic.csv")
        print(f"[CyberGuard] ✓ Traffic data loaded  ({len(DATA):,} rows).")

        if MODEL is not None:
            features    = DATA.drop(columns=['target'])
            target      = DATA['target']
            preds       = MODEL.predict(features.values)
            METRICS, _  = evaluate_performance(target, preds, "Random Forest Dashboard")
            print(f"[CyberGuard] ✓ Metrics computed: Accuracy={METRICS.get('acc', 0):.4f}")
    else:
        print("[CyberGuard] ✗ simulation_traffic.csv not found. Run main.py first.")

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Serve the main dashboard HTML."""
    return render_template('index.html')


@app.route('/api/metrics')
def get_metrics():
    """Return model performance metrics as JSON."""
    return jsonify(METRICS)


@app.route('/api/simulate/batch')
def simulate_batch():
    """
    Pick 5 random packets from simulation_traffic.csv,
    run them through the Random Forest model, and return predictions.
    """
    if DATA is None or MODEL is None:
        return jsonify({"error": "Resources not loaded. Run main.py first."}), 500

    results = []
    indices = np.random.randint(0, len(DATA), 5)

    for idx in indices:
        sample = DATA.drop(columns=['target']).iloc[[idx]]
        actual = int(DATA['target'].iloc[idx])
        pred   = int(MODEL.predict(sample.values)[0])

        results.append({
            "packet_id":  f"PKT-{np.random.randint(10000, 99999)}",
            "actual":     "ATTACK" if actual == 1 else "NORMAL",
            "prediction": "ATTACK" if pred   == 1 else "NORMAL",
            "status":     "ALERT"  if pred   == 1 else "SAFE",
        })

    return jsonify(results)


@app.route('/api/status')
def status():
    """Health-check endpoint: returns system status."""
    return jsonify({
        "status":       "online",
        "model_loaded": MODEL is not None,
        "data_loaded":  DATA  is not None,
        "data_rows":    len(DATA) if DATA is not None else 0,
        "features":     len(FEATURE_NAMES) if FEATURE_NAMES else 0,
    })


@app.route('/visuals/<filename>')
def get_visual(filename):
    """Serve plot images (PNG) from the project root directory."""
    return send_from_directory('.', filename)


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    load_resources()

    # Determine local network IP for display
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    print("\n" + "="*52)
    print("  CyberGuard AI  |  Network Threat Dashboard ")
    print("="*52)
    print(f"  Local:   http://127.0.0.1:5000")
    print(f"  Network: http://{local_ip}:5000")
    print("="*52)
    print("  Press CTRL+C to stop the server.")
    print("="*52 + "\n")

    # host='0.0.0.0' makes the server accessible to ALL devices on the LAN
    app.run(host='0.0.0.0', port=5000, debug=False)
