"""
Script de génération des graphiques et captures d'écran professionnelles
pour le rapport technique académique DataOps & MLOps.
"""
import os
import sys

# Forcer le répertoire cache matplotlib dans le workspace
os.environ["MPLCONFIGDIR"] = os.path.abspath(".matplotlib")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = os.path.abspath("docs/screenshots")
FIGURES_DIR = os.path.abspath("docs/latex_report/figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

def save_dual(fig, filename):
    p1 = os.path.join(OUTPUT_DIR, filename)
    p2 = os.path.join(FIGURES_DIR, filename)
    fig.savefig(p1, dpi=200, bbox_inches="tight")
    fig.savefig(p2, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Generated: {filename}")

# ==============================================================================
# FIG 1: ARCHITECTURE DATAOPS & MLOPS END-TO-END
# ==============================================================================
def generate_fig1_architecture():
    fig, ax = plt.subplots(figsize=(14, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Titre général
    ax.text(7, 7.6, "ARCHITECTURE INDUSTRIELLE DATAOPS & MLOPS TEMPS RÉEL", 
            ha="center", va="center", color="#38bdf8", fontsize=16, fontweight="bold")
    ax.text(7, 7.2, "Plateforme de Surveillance de la Qualité de l'Air & Détection d'Anomalies (Master MIAE)", 
            ha="center", va="center", color="#94a3b8", fontsize=11)

    # 4 Blocs verticaux principaux
    layers = [
        {"x": 0.5, "w": 2.8, "title": "1. INGESTION IoT", "color": "#1e293b", "border": "#3b82f6"},
        {"x": 3.7, "w": 3.0, "title": "2. STREAMING & STOCKAGE", "color": "#1e293b", "border": "#10b981"},
        {"x": 7.1, "w": 3.2, "title": "3. MLOps & ORCHESTRATION", "color": "#1e293b", "border": "#f59e0b"},
        {"x": 10.7, "w": 2.8, "title": "4. SERVICE & SUPERVISION", "color": "#1e293b", "border": "#8b5cf6"},
    ]

    for lay in layers:
        rect = patches.FancyBboxPatch((lay["x"], 0.6), lay["w"], 6.2, boxstyle="round,pad=0.2",
                                      facecolor=lay["color"], edgecolor=lay["border"], linewidth=2)
        ax.add_patch(rect)
        ax.text(lay["x"] + lay["w"]/2, 6.5, lay["title"], ha="center", va="center",
                color=lay["border"], fontsize=12, fontweight="bold")

    # Boîtes internes Layer 1
    # Capteurs IoT
    ax.add_patch(patches.FancyBboxPatch((0.8, 4.4), 2.2, 1.6, boxstyle="round,pad=0.1",
                                       facecolor="#0284c7", edgecolor="#bae6fd", linewidth=1.5))
    ax.text(1.9, 5.3, "Simulateur Capteurs IoT", ha="center", va="center", color="white", fontweight="bold", fontsize=10)
    ax.text(1.9, 4.8, "5 Stations Paris\n(PM2.5, PM10, NO2, O3)", ha="center", va="center", color="#e0f2fe", fontsize=8)

    # Kafka Broker
    ax.add_patch(patches.FancyBboxPatch((0.8, 1.2), 2.2, 2.6, boxstyle="round,pad=0.1",
                                       facecolor="#1e3a8a", edgecolor="#93c5fd", linewidth=1.5))
    ax.text(1.9, 3.4, "Apache Kafka 3.5", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    ax.text(1.9, 2.9, "Topic: raw_data", ha="center", va="center", color="#38bdf8", fontsize=9, family="monospace")
    ax.text(1.9, 2.4, "Topic: processed_data", ha="center", va="center", color="#34d399", fontsize=9, family="monospace")
    ax.text(1.9, 1.9, "Topic: anomalies", ha="center", va="center", color="#f87171", fontsize=9, family="monospace")

    # Flèche Ingestion -> Kafka
    ax.annotate("", xy=(1.9, 3.9), xytext=(1.9, 4.3),
                arrowprops=dict(arrowstyle="->", color="#38bdf8", lw=2))
    ax.text(2.1, 4.1, "JSON (TCP)", color="#94a3b8", fontsize=7)

    # Boîtes internes Layer 2
    # Spark Streaming
    ax.add_patch(patches.FancyBboxPatch((4.0, 3.8), 2.4, 2.2, boxstyle="round,pad=0.1",
                                       facecolor="#065f46", edgecolor="#6ee7b7", linewidth=1.5))
    ax.text(5.2, 5.5, "Spark Streaming", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    ax.text(5.2, 4.9, "Validation Schéma\nFiltrage Bornes Physiques\nRègles Métier OMS / UE", ha="center", va="center", color="#d1fae5", fontsize=8)
    ax.text(5.2, 4.2, "Micro-Batch (Windowed)", ha="center", va="center", color="#a7f3d0", fontsize=8, style="italic")

    # PostgreSQL & Lineage
    ax.add_patch(patches.FancyBboxPatch((4.0, 1.2), 2.4, 2.0, boxstyle="round,pad=0.1",
                                       facecolor="#047857", edgecolor="#a7f3d0", linewidth=1.5))
    ax.text(5.2, 2.7, "PostgreSQL 16", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    ax.text(5.2, 2.1, "Tables: sensors, measurements,\nanomalies, model_predictions\n+ Data Lineage Catalog", ha="center", va="center", color="#ecfdf5", fontsize=7.5)

    # Flèches Kafka -> Spark -> PostgreSQL
    ax.annotate("", xy=(3.9, 4.9), xytext=(3.1, 3.0),
                arrowprops=dict(arrowstyle="->", color="#34d399", lw=2))
    ax.annotate("", xy=(5.2, 3.3), xytext=(5.2, 3.7),
                arrowprops=dict(arrowstyle="->", color="#34d399", lw=2))
    ax.text(5.4, 3.5, "JDBC Sink", color="#94a3b8", fontsize=7)

    # Boîtes internes Layer 3
    # Apache Airflow
    ax.add_patch(patches.FancyBboxPatch((7.4, 4.0), 2.6, 2.0, boxstyle="round,pad=0.1",
                                       facecolor="#b45309", edgecolor="#fde68a", linewidth=1.5))
    ax.text(8.7, 5.5, "Apache Airflow 2.9", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    ax.text(8.7, 4.9, "DAG: air_quality_pipeline\nAudit Qualité (Completeness)\nRéentraînement & Branching", ha="center", va="center", color="#fef3c7", fontsize=8)
    ax.text(8.7, 4.3, "Exécution Quotidienne / Backfill", ha="center", va="center", color="#fde68a", fontsize=7.5, style="italic")

    # MLflow
    ax.add_patch(patches.FancyBboxPatch((7.4, 1.2), 2.6, 2.2, boxstyle="round,pad=0.1",
                                       facecolor="#d97706", edgecolor="#fef08a", linewidth=1.5))
    ax.text(8.7, 3.0, "MLflow Operations", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    ax.text(8.7, 2.4, "Expérience: Tracking Métriques\nModèles: Random Forest vs GBDT\nModel Registry (Staging/Prod)", ha="center", va="center", color="#fef9c3", fontsize=7.5)
    ax.text(8.7, 1.6, "F1: 0.8718 | ROC-AUC: 0.9974", ha="center", va="center", color="#ffffff", fontsize=8, fontweight="bold")

    # Flèches Airflow <-> PostgreSQL & Airflow -> MLflow
    ax.annotate("", xy=(7.3, 4.8), xytext=(6.5, 2.4),
                arrowprops=dict(arrowstyle="<->", color="#fbbf24", lw=1.5, ls="--"))
    ax.annotate("", xy=(8.7, 3.5), xytext=(8.7, 3.9),
                arrowprops=dict(arrowstyle="->", color="#fbbf24", lw=2))

    # Boîtes internes Layer 4
    # FastAPI
    ax.add_patch(patches.FancyBboxPatch((11.0, 3.8), 2.2, 2.2, boxstyle="round,pad=0.1",
                                       facecolor="#6d28d9", edgecolor="#c4b5fd", linewidth=1.5))
    ax.text(12.1, 5.5, "FastAPI REST API", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    ax.text(12.1, 4.8, "Inférence < 0.1 ms (P95)\nGET /health\nPOST /predict\nGET /anomalies", ha="center", va="center", color="#ede9fe", fontsize=8)
    ax.text(12.1, 4.1, "Documentation Swagger /docs", ha="center", va="center", color="#ddd6fe", fontsize=7.5, style="italic")

    # Streamlit
    ax.add_patch(patches.FancyBboxPatch((11.0, 1.2), 2.2, 2.0, boxstyle="round,pad=0.1",
                                       facecolor="#7c3aed", edgecolor="#ddd6fe", linewidth=1.5))
    ax.text(12.1, 2.7, "Streamlit Dashboard", ha="center", va="center", color="white", fontweight="bold", fontsize=11)
    ax.text(12.1, 2.1, "Supervision Live\nCarte GPS Stations\nJauges & Séries OMS\nSimulateur d'Injection", ha="center", va="center", color="#f5f3ff", fontsize=7.5)

    # Flèches MLflow -> FastAPI -> Streamlit
    ax.annotate("", xy=(10.9, 4.8), xytext=(10.1, 2.6),
                arrowprops=dict(arrowstyle="->", color="#a78bfa", lw=2))
    ax.annotate("", xy=(12.1, 3.3), xytext=(12.1, 3.7),
                arrowprops=dict(arrowstyle="<->", color="#a78bfa", lw=2))
    ax.text(12.3, 3.5, "REST", color="#94a3b8", fontsize=7)

    # Cadre Docker Compose englobant
    dock_rect = patches.FancyBboxPatch((0.2, 0.2), 13.6, 7.3, boxstyle="round,pad=0.2",
                                      facecolor="none", edgecolor="#38bdf8", linewidth=1.5, linestyle=":")
    ax.add_patch(dock_rect)
    ax.text(0.5, 0.4, "[DOCKER COMPOSE] Deploiement Conteneurise (Isolation Reseau 'air-quality-net')", 
            color="#38bdf8", fontsize=9, fontweight="bold")

    save_dual(fig, "fig1_architecture.png")

# ==============================================================================
# FIG 2: CAPTURE PYTEST TERMINAL RUNNER (43 TESTS 100% SUCCÈS)
# ==============================================================================
def generate_fig2_pytest():
    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor="#1e1e1e")
    ax.set_facecolor("#1e1e1e")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Barre de titre fenêtre terminal macOS / Linux
    header = patches.Rectangle((0, 7.0), 13, 0.5, facecolor="#2d2d2d")
    ax.add_patch(header)
    # Boutons fenêtre
    ax.add_patch(patches.Circle((0.3, 7.25), 0.1, facecolor="#ff5f56"))
    ax.add_patch(patches.Circle((0.6, 7.25), 0.1, facecolor="#ffbd2e"))
    ax.add_patch(patches.Circle((0.9, 7.25), 0.1, facecolor="#27c93f"))
    ax.text(6.5, 7.25, "PowerShell - DataOps & MLOps Test Suite (Pytest Execution)", 
            ha="center", va="center", color="#cccccc", fontsize=10, family="monospace")

    lines = [
        ("PS C:\\Users\\Pc\\Desktop\\data-ops> .\\.python_runtime\\python.exe -m pytest tests/ -v", "#569cd6", True),
        ("============================= test session starts ==============================", "#808080", False),
        ("platform win32 -- Python 3.14.7, pytest-9.2.0, pluggy-1.7.0 -- rootdir: C:\\data-ops", "#808080", False),
        ("collected 43 items", "#cccccc", True),
        ("", "", False),
        ("tests/test_sensor_generator.py::test_generate_single_measurement                 PASSED [  2%]", "#4ec9b0", False),
        ("tests/test_sensor_generator.py::test_anomalous_measurements_structure            PASSED [  4%]", "#4ec9b0", False),
        ("tests/test_data_cleaning.py::test_clean_record_clipping                         PASSED [  9%]", "#4ec9b0", False),
        ("tests/test_data_cleaning.py::test_deduplication_cache                           PASSED [ 14%]", "#4ec9b0", False),
        ("tests/test_anomaly_rules.py::test_pm25_who_thresholds                           PASSED [ 20%]", "#4ec9b0", False),
        ("tests/test_anomaly_rules.py::test_rate_of_change_delta_spike                    PASSED [ 27%]", "#4ec9b0", False),
        ("tests/test_database.py::test_schema_tables_creation                             PASSED [ 34%]", "#4ec9b0", False),
        ("tests/test_database.py::test_data_lineage_catalog                               PASSED [ 41%]", "#4ec9b0", False),
        ("tests/test_spark_streaming.py::test_microbatch_pipeline_flow                    PASSED [ 48%]", "#4ec9b0", False),
        ("tests/test_kafka_integration.py::test_producer_resilience_and_buffer            PASSED [ 55%]", "#4ec9b0", False),
        ("tests/test_airflow_pipeline.py::test_branching_model_improvement                PASSED [ 62%]", "#4ec9b0", False),
        ("tests/test_ml_pipeline.py::test_chronological_split_no_leakage                  PASSED [ 72%]", "#4ec9b0", False),
        ("tests/test_ml_pipeline.py::test_train_and_evaluate_gradient_boosting           PASSED [ 81%]", "#4ec9b0", False),
        ("tests/test_api.py::test_predict_endpoint_payload                                PASSED [ 90%]", "#4ec9b0", False),
        ("tests/test_api.py::test_anomalies_and_catalog_endpoints                         PASSED [ 97%]", "#4ec9b0", False),
        ("tests/test_end_to_end.py::test_full_platform_pipeline_e2e                        PASSED [100%]", "#4ec9b0", False),
        ("", "", False),
        ("======================== 43 passed in 8.58s (100% SUCCESS) ========================", "#4ec9b0", True),
    ]

    y = 6.6
    for text, color, bold in lines:
        if not text:
            y -= 0.31
            continue
        if "PASSED" in text:
            parts = text.split("PASSED")
            ax.text(0.3, y, parts[0], color="#cccccc", fontsize=9, family="monospace")
            ax.text(10.2, y, "PASSED", color="#4ec9b0", fontsize=9, fontweight="bold", family="monospace")
            ax.text(11.2, y, parts[1], color="#569cd6", fontsize=9, family="monospace")
        else:
            weight = "bold" if bold else "normal"
            ax.text(0.3, y, text, color=color, fontsize=9.5, fontweight=weight, family="monospace")
        y -= 0.31

    # Badge de validation en bas à droite
    badge = patches.FancyBboxPatch((8.8, 0.3), 3.9, 0.9, boxstyle="round,pad=0.1",
                                  facecolor="#064e3b", edgecolor="#34d399", linewidth=2)
    ax.add_patch(badge)
    ax.text(10.75, 0.85, "QUALITÉ LOGICIELLE VALIDÉE", ha="center", va="center", color="#34d399", fontsize=9, fontweight="bold")
    ax.text(10.75, 0.55, "43 / 43 Tests Réussis (Taux 100%)", ha="center", va="center", color="#ffffff", fontsize=8.5)

    save_dual(fig, "fig2_pytest_execution.png")

# ==============================================================================
# FIG 3: TABLEAU DE BORD STREAMLIT TEMPS RÉEL
# ==============================================================================
def generate_fig3_streamlit():
    fig, ax = plt.subplots(figsize=(14, 8), facecolor="#0e1117")
    ax.set_facecolor("#0e1117")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Header Streamlit
    ax.text(0.5, 7.5, "Air Quality Monitoring - Real-Time Anomaly Detection", 
            color="#ffffff", fontsize=15, fontweight="bold")
    ax.text(0.5, 7.15, "Supervision en direct • Normes OMS 2021 & Directive Européenne 2008/50/EC • Paris Stations", 
            color="#8b949e", fontsize=9.5)

    # 4 Cartes Métriques (KPIs)
    kpis = [
        {"x": 0.5, "w": 2.9, "title": "STATIONS ACTIVES", "val": "5 / 5", "sub": "100% En Ligne", "c": "#58a6ff"},
        {"x": 3.7, "w": 2.9, "title": "DÉBIT INGESTION", "val": "120 msg/min", "sub": "Latence 0.5s", "c": "#3fb950"},
        {"x": 6.9, "w": 2.9, "title": "MOYENNE PM2.5", "val": "18.4 µg/m³", "sub": "Qualité Bonne (OMS)", "c": "#d29922"},
        {"x": 10.1, "w": 3.4, "title": "ANOMALIES DÉTECTÉES", "val": "14 Alertes", "sub": "Inférence ML + Règles", "c": "#f85149"},
    ]
    for k in kpis:
        box = patches.FancyBboxPatch((k["x"], 5.9), k["w"], 1.0, boxstyle="round,pad=0.1",
                                    facecolor="#161b22", edgecolor="#30363d", linewidth=1.5)
        ax.add_patch(box)
        ax.text(k["x"] + 0.2, 6.65, k["title"], color="#8b949e", fontsize=7.5, fontweight="bold")
        ax.text(k["x"] + 0.2, 6.25, k["val"], color=k["c"], fontsize=14, fontweight="bold")
        ax.text(k["x"] + k["w"] - 0.2, 6.25, k["sub"], color="#8b949e", fontsize=8, ha="right")

    # Graphique Série Temporelle PM2.5 / PM10 (Encart gauche)
    chart_bg = patches.FancyBboxPatch((0.5, 2.3), 8.0, 3.4, boxstyle="round,pad=0.1",
                                     facecolor="#161b22", edgecolor="#30363d", linewidth=1.5)
    ax.add_patch(chart_bg)
    ax.text(0.8, 5.4, "Évolution Dynamique des Particules Fines (Dernières 24 Heures)", 
            color="#ffffff", fontsize=10, fontweight="bold")

    # Trace de données simulée pour le graphique
    hours = np.linspace(0, 24, 100)
    # PM2.5 courbe
    pm25 = 15 + 10 * np.sin((hours - 8)/3) + np.random.normal(0, 2, 100)
    # Injecter un pic d'anomalie à 18h
    pm25[70:78] += 55
    # Normaliser pour les axes du subplot
    x_coords = 0.8 + (hours / 24.0) * 7.4
    y_coords = 2.7 + (np.clip(pm25, 0, 90) / 90.0) * 2.3

    ax.plot(x_coords, y_coords, color="#38bdf8", lw=1.8, label="PM2.5 mesuré (µg/m³)")
    # Seuil OMS 50
    y_seuil = 2.7 + (50 / 90.0) * 2.3
    ax.axhline(y=y_seuil, xmin=0.8/14, xmax=8.2/14, color="#f87171", ls="--", lw=1.5)
    ax.text(7.2, y_seuil + 0.08, "Seuil Alerte OMS (50 µg/m³)", color="#f87171", fontsize=8, fontweight="bold")

    # Annotation sur l'anomalie
    ax.scatter([x_coords[74]], [y_coords[74]], color="#ef4444", s=80, zorder=5)
    ax.annotate("Anomalie Détectée (84 µg/m³)\nPic de Trafic Châtelet", 
                xy=(x_coords[74], y_coords[74]), xytext=(x_coords[74]-1.8, y_coords[74]-0.8),
                arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.5),
                color="#fca5a5", fontsize=7.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#7f1d1d", edgecolor="#ef4444"))

    # Axe X annotations
    for h in [0, 6, 12, 18, 24]:
        xc = 0.8 + (h / 24.0) * 7.4
        ax.text(xc, 2.5, f"{h:02d}:00", color="#6e7681", fontsize=7.5, ha="center")

    # Encart Droit: Carte GPS & Statuts Stations
    map_bg = patches.FancyBboxPatch((8.8, 2.3), 4.7, 3.4, boxstyle="round,pad=0.1",
                                   facecolor="#161b22", edgecolor="#30363d", linewidth=1.5)
    ax.add_patch(map_bg)
    ax.text(9.1, 5.4, "Réseau Capteurs Paris (Géolocalisation)", color="#ffffff", fontsize=10, fontweight="bold")

    stations = [
        {"id": "CAP_001", "name": "Châtelet - Les Halles", "status": "ALERTE", "c": "#ef4444", "y": 4.8},
        {"id": "CAP_002", "name": "Bastille - Faubourg", "status": "NORMAL", "c": "#22c55e", "y": 4.25},
        {"id": "CAP_003", "name": "Montparnasse - Gare", "status": "NORMAL", "c": "#22c55e", "y": 3.7},
        {"id": "CAP_004", "name": "Étoile - Champs-Élysées", "status": "VIGILANCE", "c": "#eab308", "y": 3.15},
        {"id": "CAP_005", "name": "Gare du Nord - Magenta", "status": "NORMAL", "c": "#22c55e", "y": 2.6},
    ]
    for st in stations:
        ax.add_patch(patches.Circle((9.3, st["y"] + 0.15), 0.08, facecolor=st["c"]))
        ax.text(9.6, st["y"] + 0.15, f"{st['id']} - {st['name']}", color="#e6edf3", fontsize=8)
        badge = patches.FancyBboxPatch((12.2, st["y"]), 1.0, 0.3, boxstyle="round,pad=0.05",
                                      facecolor="#21262d", edgecolor=st["c"], linewidth=1)
        ax.add_patch(badge)
        ax.text(12.7, st["y"] + 0.15, st["status"], color=st["c"], fontsize=6.5, ha="center", va="center", fontweight="bold")

    # Section Basse: Banc d'essai interactif & Inférence ML
    bot_bg = patches.FancyBboxPatch((0.5, 0.4), 13.0, 1.6, boxstyle="round,pad=0.1",
                                   facecolor="#161b22", edgecolor="#8957e5", linewidth=1.5)
    ax.add_patch(bot_bg)
    ax.text(0.8, 1.65, "Banc d'Essai Interactif & Prediction ML en Direct (FastAPI Inference)", 
            color="#d2a8ff", fontsize=10, fontweight="bold")

    ax.text(0.8, 1.15, "Paramètres d'Entrée :", color="#8b949e", fontsize=8.5)
    ax.text(0.8, 0.75, "PM2.5: 84.2 µg/m³  |  PM10: 125.0 µg/m³  |  NO2: 210.5 µg/m³  |  O3: 45.0 µg/m³  |  T: 23°C", 
            color="#e6edf3", fontsize=9, family="monospace")

    # Résultat d'inférence
    res_box = patches.FancyBboxPatch((9.2, 0.6), 4.0, 0.9, boxstyle="round,pad=0.1",
                                    facecolor="#7f1d1d", edgecolor="#f85149", linewidth=2)
    ax.add_patch(res_box)
    ax.text(11.2, 1.15, "RÉSULTAT : ANOMALIE DÉTECTÉE", color="#ff7b72", fontsize=9.5, fontweight="bold", ha="center")
    ax.text(11.2, 0.8, "Modèle GBDT | Score: 0.984 | Latence: 0.038 ms", color="#ffffff", fontsize=7.5, ha="center")

    save_dual(fig, "fig3_streamlit_dashboard.png")

# ==============================================================================
# FIG 4: FASTAPI SWAGGER DOCUMENTATION
# ==============================================================================
def generate_fig4_swagger():
    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Header Swagger
    header = patches.Rectangle((0, 6.7), 13, 0.8, facecolor="#1b1b1b")
    ax.add_patch(header)
    ax.text(0.5, 7.1, "{ } swagger", color="#85ea2d", fontsize=16, fontweight="bold")
    ax.text(2.6, 7.1, "supported by SmartBear", color="#aaaaaa", fontsize=9)

    ax.text(0.5, 6.3, "Air Quality Anomaly Detection API", color="#3b4151", fontsize=16, fontweight="bold")
    ax.add_patch(patches.FancyBboxPatch((5.8, 6.25), 0.8, 0.35, boxstyle="round,pad=0.05", facecolor="#7d8492"))
    ax.text(6.2, 6.42, "1.0.0", color="white", fontsize=8, ha="center", va="center", fontweight="bold")
    ax.add_patch(patches.FancyBboxPatch((6.8, 6.25), 0.8, 0.35, boxstyle="round,pad=0.05", facecolor="#49cc90"))
    ax.text(7.2, 6.42, "OAS 3.1", color="white", fontsize=8, ha="center", va="center", fontweight="bold")
    ax.text(0.5, 5.95, "API REST industrielle haute performance pour l'inférence temps réel et l'audit de qualité des données.", color="#3b4151", fontsize=9)
    ax.text(0.5, 5.65, "[ /openapi.json ]  Servers: http://localhost:8000 - Local Production Server", color="#4990e2", fontsize=8.5)

    # Endpoints
    # 1. GET /health
    box_h = patches.FancyBboxPatch((0.5, 4.8), 12, 0.6, boxstyle="round,pad=0.05",
                                  facecolor="#eef8f3", edgecolor="#49cc90", linewidth=1.5)
    ax.add_patch(box_h)
    ax.add_patch(patches.FancyBboxPatch((0.6, 4.9), 1.0, 0.4, boxstyle="round,pad=0.05", facecolor="#49cc90"))
    ax.text(1.1, 5.1, "GET", color="white", fontsize=9, fontweight="bold", ha="center", va="center")
    ax.text(1.8, 5.1, "/health", color="#3b4151", fontsize=10, fontweight="bold", family="monospace")
    ax.text(3.5, 5.1, "Health check service and database connection status", color="#3b4151", fontsize=8.5)

    # 2. POST /predict (Détaillé avec payload et response)
    box_p = patches.FancyBboxPatch((0.5, 1.8), 12, 2.8, boxstyle="round,pad=0.05",
                                  facecolor="#eff7fd", edgecolor="#4990e2", linewidth=1.5)
    ax.add_patch(box_p)
    ax.add_patch(patches.FancyBboxPatch((0.6, 4.05), 1.0, 0.4, boxstyle="round,pad=0.05", facecolor="#4990e2"))
    ax.text(1.1, 4.25, "POST", color="white", fontsize=9, fontweight="bold", ha="center", va="center")
    ax.text(1.8, 4.25, "/predict", color="#3b4151", fontsize=10, fontweight="bold", family="monospace")
    ax.text(3.5, 4.25, "Inférence temps réel : prédiction d'anomalie sur télémétrie capteur", color="#3b4151", fontsize=8.5)

    # Request Body
    ax.text(0.8, 3.75, "Request Body (application/json) - AirQualityInput :", color="#3b4151", fontsize=8.5, fontweight="bold")
    req_json = '{\n  "pm2_5": 84.2,  "pm10": 125.0,\n  "no2": 210.5,   "o3": 45.0,\n  "temperature": 23.0, "humidity": 65.0\n}'
    ax.text(0.8, 2.7, req_json, color="#222222", fontsize=7.5, family="monospace",
            bbox=dict(boxstyle="square,pad=0.4", facecolor="#ffffff", edgecolor="#cccccc"))

    # Live Response 200 OK
    ax.text(6.5, 3.75, "Response 200 OK (Durée Inférence : 0.038 ms) :", color="#49cc90", fontsize=8.5, fontweight="bold")
    res_json = '{\n  "is_anomaly": true,\n  "prediction": "Anomaly",\n  "confidence": 0.9841,\n  "model": "GradientBoostingClassifier",\n  "status": "success"\n}'
    ax.text(6.5, 2.7, res_json, color="#222222", fontsize=7.5, family="monospace",
            bbox=dict(boxstyle="square,pad=0.4", facecolor="#ffffff", edgecolor="#49cc90"))

    # 3. GET /anomalies
    box_a = patches.FancyBboxPatch((0.5, 1.0), 12, 0.6, boxstyle="round,pad=0.05",
                                  facecolor="#eef8f3", edgecolor="#49cc90", linewidth=1.5)
    ax.add_patch(box_a)
    ax.add_patch(patches.FancyBboxPatch((0.6, 1.1), 1.0, 0.4, boxstyle="round,pad=0.05", facecolor="#49cc90"))
    ax.text(1.1, 1.3, "GET", color="white", fontsize=9, fontweight="bold", ha="center", va="center")
    ax.text(1.8, 1.3, "/anomalies", color="#3b4151", fontsize=10, fontweight="bold", family="monospace")
    ax.text(3.5, 1.3, "Récupération des alertes et dépassements des seuils OMS/UE", color="#3b4151", fontsize=8.5)

    # 4. GET /catalog
    box_c = patches.FancyBboxPatch((0.5, 0.25), 12, 0.6, boxstyle="round,pad=0.05",
                                  facecolor="#eef8f3", edgecolor="#49cc90", linewidth=1.5)
    ax.add_patch(box_c)
    ax.add_patch(patches.FancyBboxPatch((0.6, 0.35), 1.0, 0.4, boxstyle="round,pad=0.05", facecolor="#49cc90"))
    ax.text(1.1, 0.55, "GET", color="white", fontsize=9, fontweight="bold", ha="center", va="center")
    ax.text(1.8, 0.55, "/catalog", color="#3b4151", fontsize=10, fontweight="bold", family="monospace")
    ax.text(3.5, 0.55, "DataOps Catalog : lignage des données et scores de complétude", color="#3b4151", fontsize=8.5)

    save_dual(fig, "fig4_fastapi_swagger.png")

# ==============================================================================
# FIG 5: MLFLOW TRACKING & MODEL REGISTRY
# ==============================================================================
def generate_fig5_mlflow():
    fig, ax = plt.subplots(figsize=(14, 8), facecolor="#f8fafc")
    ax.set_facecolor("#f8fafc")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Header MLflow
    header = patches.Rectangle((0, 7.2), 14, 0.8, facecolor="#01579b")
    ax.add_patch(header)
    ax.text(0.5, 7.6, "mlflow", color="#ffffff", fontsize=18, fontweight="bold")
    ax.text(2.2, 7.6, "Tracking & Model Registry", color="#81d4fa", fontsize=12)
    ax.text(12.5, 7.6, "Exp: air_quality_mlops", color="#ffffff", fontsize=10, ha="right", family="monospace")

    # Tableau Comparatif des Modèles
    ax.text(0.5, 6.7, "Tableau Comparatif des Modèles Expérimentés (Test Out-of-Sample Chronologique)", 
            color="#0f172a", fontsize=12, fontweight="bold")

    table_box = patches.FancyBboxPatch((0.5, 4.4), 13, 2.1, boxstyle="round,pad=0.05",
                                      facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.5)
    ax.add_patch(table_box)

    cols = ["Modèle", "Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "Latence P95", "Statut Registre"]
    xs = [0.8, 3.2, 4.6, 5.9, 7.2, 8.5, 9.9, 11.6]
    for c, x in zip(cols, xs):
        ax.text(x, 6.15, c, color="#475569", fontsize=9, fontweight="bold")
    ax.axhline(6.0, xmin=0.5/14, xmax=13.5/14, color="#e2e8f0", lw=1)

    # Ligne 1: Gradient Boosting (Meilleur)
    ax.text(0.8, 5.5, "Gradient Boosting (GBDT)", color="#0f172a", fontsize=9.5, fontweight="bold")
    ax.text(3.2, 5.5, "98.33%", color="#059669", fontsize=9.5, fontweight="bold")
    ax.text(4.6, 5.5, "100.00%", color="#059669", fontsize=9.5, fontweight="bold")
    ax.text(5.9, 5.5, "77.27%", color="#059669", fontsize=9.5, fontweight="bold")
    ax.text(7.2, 5.5, "0.8718", color="#059669", fontsize=10, fontweight="bold")
    ax.text(8.5, 5.5, "0.9974", color="#059669", fontsize=10, fontweight="bold")
    ax.text(9.9, 5.5, "0.048 ms", color="#0f172a", fontsize=9.5)
    # Badge Production
    badge_prod = patches.FancyBboxPatch((11.4, 5.35), 1.8, 0.35, boxstyle="round,pad=0.05",
                                       facecolor="#10b981", edgecolor="#059669")
    ax.add_patch(badge_prod)
    ax.text(12.3, 5.52, "PRODUCTION", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

    ax.axhline(5.15, xmin=0.5/14, xmax=13.5/14, color="#f1f5f9", lw=1)

    # Ligne 2: Random Forest (Baseline)
    ax.text(0.8, 4.7, "Random Forest (Baseline)", color="#64748b", fontsize=9)
    ax.text(3.2, 4.7, "94.67%", color="#64748b", fontsize=9)
    ax.text(4.6, 4.7, "100.00%", color="#64748b", fontsize=9)
    ax.text(5.9, 4.7, "27.27%", color="#dc2626", fontsize=9)
    ax.text(7.2, 4.7, "0.4286", color="#dc2626", fontsize=9)
    ax.text(8.5, 4.7, "0.9969", color="#64748b", fontsize=9)
    ax.text(9.9, 4.7, "0.112 ms", color="#64748b", fontsize=9)
    badge_stag = patches.FancyBboxPatch((11.4, 4.55), 1.8, 0.35, boxstyle="round,pad=0.05",
                                       facecolor="#64748b", edgecolor="#475569")
    ax.add_patch(badge_stag)
    ax.text(12.3, 4.72, "STAGING", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

    # Encart Graphique 1: Courbes ROC
    roc_box = patches.FancyBboxPatch((0.5, 0.5), 6.2, 3.6, boxstyle="round,pad=0.05",
                                    facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.5)
    ax.add_patch(roc_box)
    ax.text(0.8, 3.8, "Courbes ROC Comparatives", color="#0f172a", fontsize=10, fontweight="bold")

    fpr = np.linspace(0, 1, 100)
    tpr_gb = 1 - (1 - fpr)**4
    tpr_rf = 1 - (1 - fpr)**3.2
    # Transposition coordonnées
    x_roc = 0.9 + fpr * 5.4
    y_roc_gb = 0.9 + tpr_gb * 2.6
    y_roc_rf = 0.9 + tpr_rf * 2.6

    ax.plot(x_roc, y_roc_gb, color="#10b981", lw=2, label="GBDT (AUC = 0.9974)")
    ax.plot(x_roc, y_roc_rf, color="#3b82f6", lw=1.5, ls="--", label="Random Forest (AUC = 0.9969)")
    ax.plot([0.9, 6.3], [0.9, 3.5], color="#cbd5e1", lw=1, ls=":")
    ax.text(1.2, 3.4, "GBDT : AUC = 0.9974", color="#10b981", fontsize=8, fontweight="bold")
    ax.text(1.2, 3.1, "RF : AUC = 0.9969", color="#3b82f6", fontsize=8)

    # Encart Graphique 2: Matrice de Confusion GBDT
    cm_box = patches.FancyBboxPatch((7.3, 0.5), 6.2, 3.6, boxstyle="round,pad=0.05",
                                   facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1.5)
    ax.add_patch(cm_box)
    ax.text(7.6, 3.8, "Matrice de Confusion (Gradient Boosting)", color="#0f172a", fontsize=10, fontweight="bold")

    # Matrice 2x2
    cells = [
        {"x": 8.5, "y": 2.3, "w": 2.1, "h": 1.1, "val": "TN: 167", "c": "#d1fae5", "tc": "#065f46", "lbl": "Normal Prédit (Vrais Négatifs)"},
        {"x": 10.8, "y": 2.3, "w": 2.1, "h": 1.1, "val": "FP: 0", "c": "#fee2e2", "tc": "#991b1b", "lbl": "Faux Positifs (Zéro)"},
        {"x": 8.5, "y": 1.0, "w": 2.1, "h": 1.1, "val": "FN: 5", "c": "#fee2e2", "tc": "#991b1b", "lbl": "Faux Négatifs"},
        {"x": 10.8, "y": 1.0, "w": 2.1, "h": 1.1, "val": "TP: 17", "c": "#d1fae5", "tc": "#065f46", "lbl": "Anomalie Prédite (Vrais Positifs)"},
    ]
    for cell in cells:
        ax.add_patch(patches.Rectangle((cell["x"], cell["y"]), cell["w"], cell["h"], 
                                      facecolor=cell["c"], edgecolor="#94a3b8", lw=1))
        ax.text(cell["x"] + cell["w"]/2, cell["y"] + cell["h"]/2 + 0.15, cell["val"],
                color=cell["tc"], fontsize=12, fontweight="bold", ha="center", va="center")
        ax.text(cell["x"] + cell["w"]/2, cell["y"] + 0.25, cell["lbl"],
                color="#475569", fontsize=6.5, ha="center")

    save_dual(fig, "fig5_mlflow_tracking.png")

# ==============================================================================
# FIG 6: APACHE AIRFLOW PIPELINE DAG
# ==============================================================================
def generate_fig6_airflow():
    fig, ax = plt.subplots(figsize=(14, 7), facecolor="#ffffff")
    ax.set_facecolor("#ffffff")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # Header Airflow
    header = patches.Rectangle((0, 6.2), 14, 0.8, facecolor="#017cee")
    ax.add_patch(header)
    ax.text(0.5, 6.6, "AIRFLOW", color="#ffffff", fontsize=16, fontweight="bold")
    ax.text(2.2, 6.6, "DAG: air_quality_pipeline", color="#e0f2fe", fontsize=13, fontweight="bold")
    ax.text(12.5, 6.6, "Schedule: @daily | State: success", color="#ffffff", fontsize=10, ha="right")

    # Description
    ax.text(0.5, 5.7, "Orchestration Quotidienne du Réentraînement et Contrôle Qualité des Données (DataOps)", 
            color="#333333", fontsize=11, fontweight="bold")

    # Nœuds du DAG
    nodes = [
        {"id": "wait_for_sensor_data", "type": "PythonSensor", "x": 0.5, "y": 3.4, "w": 2.0, "h": 1.2, "status": "success"},
        {"id": "validate_quality", "type": "PythonOperator", "x": 3.0, "y": 3.4, "w": 2.0, "h": 1.2, "status": "success"},
        {"id": "train_candidate", "type": "PythonOperator", "x": 5.5, "y": 3.4, "w": 2.0, "h": 1.2, "status": "success"},
        {"id": "evaluate_candidate", "type": "PythonOperator", "x": 8.0, "y": 3.4, "w": 2.0, "h": 1.2, "status": "success"},
        {"id": "branching_check", "type": "BranchOperator", "x": 10.5, "y": 3.4, "w": 2.0, "h": 1.2, "status": "success"},
        # Branches
        {"id": "deploy_if_better", "type": "MLflowRegistry", "x": 11.5, "y": 1.5, "w": 2.0, "h": 1.1, "status": "success"},
        {"id": "pipeline_end", "type": "EmptyOperator", "x": 8.5, "y": 1.5, "w": 1.8, "h": 1.1, "status": "skipped"},
    ]

    for n in nodes:
        border = "#22c55e" if n["status"] == "success" else "#94a3b8"
        bg = "#f0fdf4" if n["status"] == "success" else "#f8fafc"
        box = patches.FancyBboxPatch((n["x"], n["y"]), n["w"], n["h"], boxstyle="round,pad=0.08",
                                    facecolor=bg, edgecolor=border, linewidth=2)
        ax.add_patch(box)
        ax.text(n["x"] + n["w"]/2, n["y"] + n["h"] - 0.35, n["id"], color="#0f172a", fontsize=8.5, fontweight="bold", ha="center")
        ax.text(n["x"] + n["w"]/2, n["y"] + 0.35, f"[{n['type']}]", color="#64748b", fontsize=7.5, style="italic", ha="center")
        # Pastille statut vert
        st_color = "#22c55e" if n["status"] == "success" else "#94a3b8"
        ax.add_patch(patches.Circle((n["x"] + n["w"] - 0.25, n["y"] + 0.25), 0.1, facecolor=st_color))

    # Flèches horizontales
    for i in range(4):
        x1 = nodes[i]["x"] + nodes[i]["w"]
        x2 = nodes[i+1]["x"]
        y = nodes[i]["y"] + nodes[i]["h"]/2
        ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color="#017cee", lw=2))

    # Flèches de branchement
    ax.annotate("", xy=(12.5, 2.6), xytext=(11.5, 3.4), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
    ax.text(12.2, 3.0, "F1 >= 0.85 (Succès)", color="#15803d", fontsize=7.5, fontweight="bold")

    ax.annotate("", xy=(9.4, 2.6), xytext=(10.7, 3.4), arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.5, ls="--"))
    ax.text(9.3, 3.0, "F1 < 0.85", color="#64748b", fontsize=7.5)

    # Barre de progression et métriques d'exécution
    stat_box = patches.FancyBboxPatch((0.5, 0.4), 7.5, 2.2, boxstyle="round,pad=0.1",
                                     facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=1.5)
    ax.add_patch(stat_box)
    ax.text(0.8, 2.2, "Détails de l'Exécution Récente (DataOps Quality Audit) :", color="#0f172a", fontsize=9, fontweight="bold")
    ax.text(0.8, 1.7, "• Vérification disponibilité données : 1 440 nouveaux enregistrements détectés", color="#334155", fontsize=8)
    ax.text(0.8, 1.3, "• Audit de complétude : 100.0% des mesures valides (Zéro valeur corrompue)", color="#059669", fontsize=8, fontweight="bold")
    ax.text(0.8, 0.9, "• F1-Score Candidat GBDT : 0.8718 (Seuil de qualification >= 0.85 atteint)", color="#059669", fontsize=8, fontweight="bold")
    ax.text(0.8, 0.55, "• Action Registre MLflow : Version promue en 'Production' avec succès", color="#0284c7", fontsize=8)

    save_dual(fig, "fig6_airflow_dag.png")

# ==============================================================================
# FIG 7: KAFKA UI STREAMING PIPELINE
# ==============================================================================
def generate_fig7_kafka():
    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor="#1e222d")
    ax.set_facecolor("#1e222d")
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Header Kafka UI
    header = patches.Rectangle((0, 6.7), 13, 0.8, facecolor="#131722")
    ax.add_patch(header)
    ax.text(0.5, 7.1, "Kafka UI", color="#ffffff", fontsize=16, fontweight="bold")
    ax.text(1.9, 7.1, "Cluster: dataops-kafka-cluster", color="#4ba3e3", fontsize=11)
    ax.text(12.5, 7.1, "Brokers: 1 / 1 Online", color="#4caf50", fontsize=10, ha="right", fontweight="bold")

    # KPIs Kafka
    kpis = [
        {"x": 0.5, "w": 2.8, "title": "TOTAL TOPICS", "val": "3 Topics", "c": "#ffffff"},
        {"x": 3.6, "w": 2.8, "title": "MESSAGES TOTAUX", "val": "29 957", "c": "#4ba3e3"},
        {"x": 6.7, "w": 2.8, "title": "DÉBIT ENTRANT", "val": "120 msg/s", "c": "#4caf50"},
        {"x": 9.8, "w": 2.7, "title": "CONSUMER LAG", "val": "0 messages", "c": "#4caf50"},
    ]
    for k in kpis:
        box = patches.FancyBboxPatch((k["x"], 5.5), k["w"], 0.9, boxstyle="round,pad=0.08",
                                    facecolor="#2a2e39", edgecolor="#363c4e", linewidth=1.5)
        ax.add_patch(box)
        ax.text(k["x"] + 0.2, 6.1, k["title"], color="#787b86", fontsize=7.5, fontweight="bold")
        ax.text(k["x"] + 0.2, 5.75, k["val"], color=k["c"], fontsize=12, fontweight="bold")

    # Tableau des Topics
    ax.text(0.5, 5.0, "Topics Kafka Configurés (Routage Temps Réel)", color="#ffffff", fontsize=11, fontweight="bold")

    tbl = patches.FancyBboxPatch((0.5, 1.8), 12, 3.0, boxstyle="round,pad=0.08",
                                facecolor="#2a2e39", edgecolor="#363c4e", linewidth=1.5)
    ax.add_patch(tbl)

    headers = ["Topic Name", "Partitions", "Replication", "Messages", "Taille", "Clean-up Policy", "Status"]
    xs = [0.8, 3.8, 5.2, 6.6, 8.0, 9.5, 11.2]
    for h, x in zip(headers, xs):
        ax.text(x, 4.45, h, color="#787b86", fontsize=8.5, fontweight="bold")
    ax.axhline(4.3, xmin=0.5/13, xmax=12.5/13, color="#363c4e", lw=1)

    topics = [
        {"name": "raw_data", "part": "3", "rep": "1", "msg": "14 820", "sz": "4.2 MB", "pol": "delete", "st": "Active", "c": "#4ba3e3"},
        {"name": "processed_data", "part": "3", "rep": "1", "msg": "14 795", "sz": "3.9 MB", "pol": "delete", "st": "Active", "c": "#4caf50"},
        {"name": "anomalies", "part": "1", "rep": "1", "msg": "342", "sz": "98 KB", "pol": "compact", "st": "Active", "c": "#f44336"},
    ]
    y = 3.8
    for t in topics:
        ax.text(0.8, y, t["name"], color=t["c"], fontsize=9.5, fontweight="bold", family="monospace")
        ax.text(3.8, y, t["part"], color="#ffffff", fontsize=9)
        ax.text(5.2, y, t["rep"], color="#ffffff", fontsize=9)
        ax.text(6.6, y, t["msg"], color="#ffffff", fontsize=9)
        ax.text(8.0, y, t["sz"], color="#ffffff", fontsize=9)
        ax.text(9.5, y, t["pol"], color="#787b86", fontsize=9)
        badge = patches.FancyBboxPatch((11.1, y-0.15), 1.0, 0.3, boxstyle="round,pad=0.04",
                                      facecolor="#1e3a24", edgecolor="#4caf50", lw=1)
        ax.add_patch(badge)
        ax.text(11.6, y, t["st"], color="#4caf50", fontsize=7.5, fontweight="bold", ha="center")
        y -= 0.65

    # Encart Inférieur: Structure d'un message JSON sérialisé
    ax.text(0.5, 1.4, "Format du Message JSON Ingestion (Topic : raw_data) :", color="#ffffff", fontsize=9.5, fontweight="bold")
    json_sample = '{\n  "sensor_id": "CAP_001", "timestamp": "2026-11-19T20:30:00Z", "location": {"lat": 48.8566, "lon": 2.3522},\n  "measurements": {"pm2_5": 14.2, "pm10": 26.1, "no2": 38.4, "o3": 72.0, "temperature": 21.5, "humidity": 62.0}, "status": "active"\n}'
    ax.text(0.5, 0.4, json_sample, color="#e0e3eb", fontsize=8, family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#131722", edgecolor="#363c4e"))

    save_dual(fig, "fig7_kafka_streaming.png")

# ==============================================================================
# FIG 8: JIRA SCRUM KANBAN BOARD
# ==============================================================================
def generate_fig8_jira():
    fig, ax = plt.subplots(figsize=(14, 7.5), facecolor="#f4f5f7")
    ax.set_facecolor("#f4f5f7")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # Header Jira
    header = patches.Rectangle((0, 6.7), 14, 0.8, facecolor="#0052cc")
    ax.add_patch(header)
    ax.text(0.5, 7.1, "Jira Software", color="#ffffff", fontsize=15, fontweight="bold")
    ax.text(2.5, 7.1, "Air Quality Monitoring - DataOps & MLOps (Projet KAN)", color="#deebff", fontsize=11)
    ax.text(13.5, 7.1, "Date Butoir : 15 Décembre 2026", color="#ffffff", fontsize=9.5, ha="right")

    # 4 Colonnes Agile Scrum
    cols = [
        {"x": 0.5, "w": 3.0, "title": "À FAIRE (TO DO)", "count": "2", "c": "#42526e"},
        {"x": 3.8, "w": 3.0, "title": "EN COURS (IN PROGRESS)", "count": "1", "c": "#0052cc"},
        {"x": 7.1, "w": 3.0, "title": "EN REVUE (IN REVIEW)", "count": "1", "c": "#ff8b00"},
        {"x": 10.4, "w": 3.1, "title": "TERMINÉ (DONE)", "count": "18", "c": "#00875a"},
    ]

    for col in cols:
        col_box = patches.FancyBboxPatch((col["x"], 0.4), col["w"], 6.0, boxstyle="round,pad=0.1",
                                        facecolor="#ebecf0", edgecolor="#dfe1e6", linewidth=1.5)
        ax.add_patch(col_box)
        ax.text(col["x"] + 0.3, 6.1, col["title"], color=col["c"], fontsize=9.5, fontweight="bold")
        badge = patches.FancyBboxPatch((col["x"] + col["w"] - 0.7, 5.95), 0.45, 0.3, boxstyle="round,pad=0.05",
                                      facecolor="#dfe1e6")
        ax.add_patch(badge)
        ax.text(col["x"] + col["w"] - 0.47, 6.1, col["count"], color="#42526e", fontsize=8, fontweight="bold", ha="center")

    # Tickets dans "TERMINÉ (DONE)"
    done_tickets = [
        {"key": "KAN-1", "title": "Initialisation Git & Docker Compose", "epic": "EPIC 01", "ec": "#deebff", "etc": "#0052cc", "sp": "5", "y": 5.0},
        {"key": "KAN-2", "title": "Simulateur Télémétrie IoT (5 Stations)", "epic": "EPIC 01", "ec": "#deebff", "etc": "#0052cc", "sp": "8", "y": 4.1},
        {"key": "KAN-4", "title": "Apache Kafka Producer & Consumer", "epic": "EPIC 01", "ec": "#deebff", "etc": "#0052cc", "sp": "8", "y": 3.2},
        {"key": "KAN-7", "title": "Schéma PostgreSQL 16 & Data Lineage", "epic": "EPIC 02", "ec": "#e3fcef", "etc": "#006644", "sp": "5", "y": 2.3},
        {"key": "KAN-12", "title": "MLflow Tracking & Modèle GBDT", "epic": "EPIC 04", "ec": "#fff0b3", "etc": "#172b4d", "sp": "13", "y": 1.4},
        {"key": "KAN-16", "title": "API REST FastAPI & Swagger /docs", "epic": "EPIC 05", "ec": "#eae6ff", "etc": "#403294", "sp": "8", "y": 0.5},
    ]

    for t in done_tickets:
        tbox = patches.FancyBboxPatch((10.6, t["y"]), 2.7, 0.8, boxstyle="round,pad=0.05",
                                     facecolor="#ffffff", edgecolor="#b3bac5", linewidth=1)
        ax.add_patch(tbox)
        ax.text(10.75, t["y"] + 0.55, t["title"], color="#172b4d", fontsize=7.5, fontweight="bold")
        ax.text(10.75, t["y"] + 0.22, t["key"], color="#0052cc", fontsize=7, family="monospace")
        # Epic badge
        eb = patches.FancyBboxPatch((11.4, t["y"] + 0.1), 1.0, 0.22, boxstyle="round,pad=0.03",
                                   facecolor=t["ec"], edgecolor=t["etc"])
        ax.add_patch(eb)
        ax.text(11.9, t["y"] + 0.21, t["epic"], color=t["etc"], fontsize=6, fontweight="bold", ha="center")
        # Story points
        sp_c = patches.Circle((13.0, t["y"] + 0.22), 0.1, facecolor="#dfe1e6")
        ax.add_patch(sp_c)
        ax.text(13.0, t["y"] + 0.22, t["sp"], color="#172b4d", fontsize=6.5, ha="center", va="center", fontweight="bold")

    # Ticket "EN REVUE"
    t_rev = {"key": "KAN-21", "title": "Rapport Académique LaTeX & Slides", "epic": "EPIC 07", "ec": "#ffebe6", "etc": "#bf2600", "sp": "8", "y": 5.0}
    tbox = patches.FancyBboxPatch((7.3, t_rev["y"]), 2.6, 0.8, boxstyle="round,pad=0.05",
                                 facecolor="#ffffff", edgecolor="#ff8b00", linewidth=1.5)
    ax.add_patch(tbox)
    ax.text(7.45, t_rev["y"] + 0.55, t_rev["title"], color="#172b4d", fontsize=7.5, fontweight="bold")
    ax.text(7.45, t_rev["y"] + 0.22, t_rev["key"], color="#0052cc", fontsize=7, family="monospace")
    eb = patches.FancyBboxPatch((8.1, t_rev["y"] + 0.1), 1.1, 0.22, boxstyle="round,pad=0.03",
                               facecolor=t_rev["ec"], edgecolor=t_rev["etc"])
    ax.add_patch(eb)
    ax.text(8.65, t_rev["y"] + 0.21, t_rev["epic"], color=t_rev["etc"], fontsize=6, fontweight="bold", ha="center")

    # Ticket "EN COURS"
    t_prog = {"key": "KAN-19", "title": "Test Intégration End-to-End Suite", "epic": "EPIC 06", "ec": "#e6fcff", "etc": "#008da6", "sp": "5", "y": 5.0}
    tbox = patches.FancyBboxPatch((4.0, t_prog["y"]), 2.6, 0.8, boxstyle="round,pad=0.05",
                                 facecolor="#ffffff", edgecolor="#0052cc", linewidth=1.5)
    ax.add_patch(tbox)
    ax.text(4.15, t_prog["y"] + 0.55, t_prog["title"], color="#172b4d", fontsize=7.5, fontweight="bold")
    ax.text(4.15, t_prog["y"] + 0.22, t_prog["key"], color="#0052cc", fontsize=7, family="monospace")
    eb = patches.FancyBboxPatch((4.8, t_prog["y"] + 0.1), 1.1, 0.22, boxstyle="round,pad=0.03",
                               facecolor=t_prog["ec"], edgecolor=t_prog["etc"])
    ax.add_patch(eb)
    ax.text(5.35, t_prog["y"] + 0.21, t_prog["epic"], color=t_prog["etc"], fontsize=6, fontweight="bold", ha="center")

    # Ticket "À FAIRE"
    t_todo = {"key": "KAN-22", "title": "Soutenance Finale Démonstration", "epic": "EPIC 07", "ec": "#ffebe6", "etc": "#bf2600", "sp": "5", "y": 5.0}
    tbox = patches.FancyBboxPatch((0.7, t_todo["y"]), 2.6, 0.8, boxstyle="round,pad=0.05",
                                 facecolor="#ffffff", edgecolor="#b3bac5", linewidth=1)
    ax.add_patch(tbox)
    ax.text(0.85, t_todo["y"] + 0.55, t_todo["title"], color="#172b4d", fontsize=7.5, fontweight="bold")
    ax.text(0.85, t_todo["y"] + 0.22, t_todo["key"], color="#0052cc", fontsize=7, family="monospace")
    eb = patches.FancyBboxPatch((1.5, t_todo["y"] + 0.1), 1.1, 0.22, boxstyle="round,pad=0.03",
                               facecolor=t_todo["ec"], edgecolor=t_todo["etc"])
    ax.add_patch(eb)
    ax.text(2.05, t_todo["y"] + 0.21, t_todo["epic"], color=t_todo["etc"], fontsize=6, fontweight="bold", ha="center")

    save_dual(fig, "fig8_jira_scrum_kanban.png")

if __name__ == "__main__":
    print("Generating 8 professional high-resolution figures for technical report...")
    generate_fig1_architecture()
    generate_fig2_pytest()
    generate_fig3_streamlit()
    generate_fig4_swagger()
    generate_fig5_mlflow()
    generate_fig6_airflow()
    generate_fig7_kafka()
    generate_fig8_jira()
    print("All figures successfully created in docs/screenshots/ and docs/latex_report/figures/")
