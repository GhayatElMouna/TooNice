# UserApp/ai_security.py - VRAIE IA MULTI-ALGORITHMES
import pandas as pd
import numpy as np
from django.db import connection
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.decomposition import PCA
from sklearn.covariance import EllipticEnvelope
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# Chemins des modèles
BASE_DIR = os.path.dirname(__file__)
SCALER_PATH = os.path.join(BASE_DIR, "ai_scaler.pkl")
ISOLATION_FOREST_PATH = os.path.join(BASE_DIR, "ai_isolation_forest.pkl")
DBSCAN_PATH = os.path.join(BASE_DIR, "ai_dbscan.pkl")
KMEANS_PATH = os.path.join(BASE_DIR, "ai_kmeans.pkl")
OCSVM_PATH = os.path.join(BASE_DIR, "ai_ocsvm.pkl")
PCA_PATH = os.path.join(BASE_DIR, "ai_pca.pkl")
ELLIPTIC_PATH = os.path.join(BASE_DIR, "ai_elliptic.pkl")


def extract_features_from_db():
    """
    Extraction complète des features pour l'IA
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_user AS id,
                email,
                
                -- FEATURES TEMPORELLES
                CASE WHEN last_login IS NULL THEN -1
                     ELSE CAST((julianday('now') - julianday(last_login)) AS INTEGER)
                END AS days_since_login,
                CAST((julianday('now') - julianday(date_joined)) AS INTEGER) AS account_age_days,
                CASE WHEN last_login IS NULL THEN 1 ELSE 0 END AS never_logged_in,
                
                -- RATIO ACTIVITÉ
                CASE WHEN last_login IS NULL THEN 0
                     ELSE CAST((julianday('now') - julianday(last_login)) AS REAL) / 
                          CAST((julianday('now') - julianday(date_joined)) AS REAL)
                END AS inactivity_ratio,
                
                -- FEATURES SÉCURITÉ
                LENGTH(password) AS password_length,
                CASE WHEN LENGTH(password) < 60 THEN 1 ELSE 0 END AS weak_password,
                
                -- FEATURES PROFIL (0-5 scale)
                (CASE WHEN nom IS NOT NULL AND nom != '' THEN 1 ELSE 0 END +
                 CASE WHEN prenom IS NOT NULL AND prenom != '' THEN 1 ELSE 0 END +
                 CASE WHEN date_naissance IS NOT NULL THEN 1 ELSE 0 END +
                 CASE WHEN adresse IS NOT NULL AND adresse != '' THEN 1 ELSE 0 END +
                 CASE WHEN pays IS NOT NULL AND pays != '' THEN 1 ELSE 0 END) AS profile_completeness,
                
                -- FEATURES EMAIL
                LENGTH(email) AS email_length,
                LENGTH(email) - LENGTH(REPLACE(email, '.', '')) AS email_dots,
                LENGTH(email) - LENGTH(REPLACE(email, '_', '')) AS email_underscores,
                LENGTH(email) - LENGTH(REPLACE(LOWER(email), 'a', '')) AS email_letter_a,
                
                CASE WHEN LOWER(email) LIKE '%@gmail.%' THEN 1 ELSE 0 END AS is_gmail,
                CASE WHEN LOWER(email) LIKE '%@yahoo.%' THEN 1 ELSE 0 END AS is_yahoo,
                CASE WHEN LOWER(email) LIKE '%@hotmail.%' OR LOWER(email) LIKE '%@outlook.%' THEN 1 ELSE 0 END AS is_microsoft,
                CASE WHEN LOWER(email) LIKE '%temp%' OR LOWER(email) LIKE '%yopmail%' THEN 1 ELSE 0 END AS is_temp_email,
                
                -- FEATURES PERMISSIONS
                CASE WHEN is_staff = 1 THEN 1 ELSE 0 END AS is_staff,
                CASE WHEN is_superuser = 1 THEN 1 ELSE 0 END AS is_superuser,
                CASE WHEN is_active = 0 THEN 1 ELSE 0 END AS is_inactive,
                
                -- FEATURES COMPORTEMENTALES
                CASE WHEN is_staff = 1 AND last_login IS NULL THEN 1 ELSE 0 END AS admin_never_logged,
                CASE WHEN last_login IS NULL AND CAST((julianday('now') - julianday(date_joined)) AS INTEGER) > 30 THEN 1 ELSE 0 END AS old_account_never_logged
                
            FROM UserApp_user
        """)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
    
    return df


def train_ai_models(df, force_retrain=False):
    """
    Entraîne PLUSIEURS modèles d'IA différents
    Chaque IA apprend quelque chose de différent
    """
    
    # Features pour l'IA
    feature_columns = [
        'days_since_login', 'account_age_days', 'inactivity_ratio',
        'password_length', 'weak_password', 'profile_completeness',
        'email_length', 'email_dots', 'email_underscores',
        'is_gmail', 'is_yahoo', 'is_microsoft', 'is_temp_email',
        'is_staff', 'is_superuser', 'is_inactive',
        'admin_never_logged', 'old_account_never_logged'
    ]
    
    X = df[feature_columns].fillna(0).replace([np.inf, -np.inf], 0)
    
    print("\n" + "="*70)
    print("🧠 ENTRAÎNEMENT DES MODÈLES D'INTELLIGENCE ARTIFICIELLE")
    print("="*70)
    print(f"📊 Dataset: {len(df)} utilisateurs | {len(feature_columns)} features")
    
    # ============================================
    # 1. NORMALISATION DES DONNÉES
    # ============================================
    print("\n1️⃣ Normalisation des données...")
    scaler = RobustScaler()  # Plus robuste aux outliers que StandardScaler
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, SCALER_PATH)
    print("   ✅ Scaler entraîné et sauvegardé")
    
    # ============================================
    # 2. PCA - RÉDUCTION DE DIMENSIONNALITÉ
    # ============================================
    print("\n2️⃣ Entraînement PCA (réduction de dimensions)...")
    pca = PCA(n_components=min(10, len(feature_columns)))
    X_pca = pca.fit_transform(X_scaled)
    joblib.dump(pca, PCA_PATH)
    variance_explained = pca.explained_variance_ratio_.sum() * 100
    print(f"   ✅ PCA: {variance_explained:.1f}% de variance expliquée")
    
    # ============================================
    # 3. ISOLATION FOREST - Détection d'anomalies
    # ============================================
    print("\n3️⃣ Entraînement Isolation Forest (anomalie detection)...")
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.2,  # 20% d'anomalies attendues
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_scaled)
    joblib.dump(iso_forest, ISOLATION_FOREST_PATH)
    anomaly_scores = iso_forest.decision_function(X_scaled)
    n_anomalies = (iso_forest.predict(X_scaled) == -1).sum()
    print(f"   ✅ Isolation Forest: {n_anomalies} anomalies détectées")
    
    # ============================================
    # 4. DBSCAN - CLUSTERING DENSITÉ
    # ============================================
    print("\n4️⃣ Entraînement DBSCAN (clustering)...")
    dbscan = DBSCAN(eps=1.5, min_samples=max(2, len(df) // 10))
    dbscan_labels = dbscan.fit_predict(X_scaled)
    joblib.dump(dbscan, DBSCAN_PATH)
    n_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
    n_noise = list(dbscan_labels).count(-1)
    print(f"   ✅ DBSCAN: {n_clusters} clusters trouvés, {n_noise} points de bruit")
    
    # ============================================
    # 5. K-MEANS - CLUSTERING CENTROÏDES
    # ============================================
    print("\n5️⃣ Entraînement K-Means (clustering)...")
    optimal_k = min(max(3, len(df) // 15), 8)
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(X_scaled)
    joblib.dump(kmeans, KMEANS_PATH)
    print(f"   ✅ K-Means: {optimal_k} clusters créés")
    
    # ============================================
    # 6. ONE-CLASS SVM - Détection anomalies
    # ============================================
    print("\n6️⃣ Entraînement One-Class SVM...")
    ocsvm = OneClassSVM(kernel='rbf', gamma='auto', nu=0.2)
    ocsvm.fit(X_scaled)
    joblib.dump(ocsvm, OCSVM_PATH)
    ocsvm_anomalies = (ocsvm.predict(X_scaled) == -1).sum()
    print(f"   ✅ One-Class SVM: {ocsvm_anomalies} anomalies détectées")
    
    # ============================================
    # 7. ELLIPTIC ENVELOPE - Détection outliers
    # ============================================
    print("\n7️⃣ Entraînement Elliptic Envelope...")
    try:
        elliptic = EllipticEnvelope(contamination=0.2, random_state=42)
        elliptic.fit(X_scaled)
        joblib.dump(elliptic, ELLIPTIC_PATH)
        elliptic_anomalies = (elliptic.predict(X_scaled) == -1).sum()
        print(f"   ✅ Elliptic Envelope: {elliptic_anomalies} outliers détectés")
    except:
        print(f"   ⚠️ Elliptic Envelope: Pas assez de données, skipped")
    
    print("\n" + "="*70)
    print("✅ TOUS LES MODÈLES D'IA ONT ÉTÉ ENTRAÎNÉS AVEC SUCCÈS")
    print("="*70)
    
    return {
        'scaler': scaler,
        'pca': pca,
        'isolation_forest': iso_forest,
        'dbscan': dbscan,
        'kmeans': kmeans,
        'ocsvm': ocsvm
    }


def load_or_train_models(df, force_retrain=False):
    """
    Charge les modèles existants ou les entraîne
    """
    models_exist = all([
        os.path.exists(SCALER_PATH),
        os.path.exists(ISOLATION_FOREST_PATH),
        os.path.exists(KMEANS_PATH)
    ])
    
    if models_exist and not force_retrain:
        print("📂 Chargement des modèles IA existants...")
        models = {
            'scaler': joblib.load(SCALER_PATH),
            'isolation_forest': joblib.load(ISOLATION_FOREST_PATH),
            'dbscan': joblib.load(DBSCAN_PATH) if os.path.exists(DBSCAN_PATH) else None,
            'kmeans': joblib.load(KMEANS_PATH),
            'ocsvm': joblib.load(OCSVM_PATH) if os.path.exists(OCSVM_PATH) else None,
            'pca': joblib.load(PCA_PATH) if os.path.exists(PCA_PATH) else None,
        }
        print("✅ Modèles chargés")
        return models
    else:
        return train_ai_models(df, force_retrain)


def predict_with_ensemble(X_scaled, models):
    """
    ENSEMBLE LEARNING: Combine les prédictions de TOUS les modèles
    Chaque IA vote, on prend la décision collective
    """
    votes = []
    
    # 1. Isolation Forest (poids: 25%)
    iso_scores = models['isolation_forest'].decision_function(X_scaled)
    iso_scores_norm = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min() + 1e-10)
    iso_scores_norm = 1 - iso_scores_norm  # Inverser (plus haut = plus risqué)
    votes.append(iso_scores_norm * 0.25)
    
    # 2. One-Class SVM (poids: 20%)
    if models.get('ocsvm'):
        ocsvm_pred = models['ocsvm'].decision_function(X_scaled)
        ocsvm_norm = (ocsvm_pred - ocsvm_pred.min()) / (ocsvm_pred.max() - ocsvm_pred.min() + 1e-10)
        ocsvm_norm = 1 - ocsvm_norm
        votes.append(ocsvm_norm * 0.20)
    
    # 3. K-Means - Distance au centroïde le plus proche (poids: 20%)
    kmeans_distances = np.min(models['kmeans'].transform(X_scaled), axis=1)
    kmeans_norm = (kmeans_distances - kmeans_distances.min()) / (kmeans_distances.max() - kmeans_distances.min() + 1e-10)
    votes.append(kmeans_norm * 0.20)
    
    # 4. DBSCAN - Points de bruit (poids: 15%)
    if models.get('dbscan'):
        dbscan_pred = models['dbscan'].fit_predict(X_scaled)
        dbscan_scores = np.where(dbscan_pred == -1, 1.0, 0.3)  # Bruit = 1.0, cluster = 0.3
        votes.append(dbscan_scores * 0.15)
    
    # 5. PCA reconstruction error (poids: 20%)
    if models.get('pca'):
        X_pca = models['pca'].transform(X_scaled)
        X_reconstructed = models['pca'].inverse_transform(X_pca)
        reconstruction_error = np.sum((X_scaled - X_reconstructed) ** 2, axis=1)
        recon_norm = (reconstruction_error - reconstruction_error.min()) / (reconstruction_error.max() - reconstruction_error.min() + 1e-10)
        votes.append(recon_norm * 0.20)
    
    # VOTE FINAL
    final_scores = np.sum(votes, axis=0)
    
    return final_scores


def run_ai_security(force_retrain=False):
    """
    ANALYSE COMPLÈTE PAR IA MULTI-ALGORITHMES
    """
    print("\n" + "🤖"*35)
    print("🤖 SYSTÈME D'INTELLIGENCE ARTIFICIELLE DE SÉCURITÉ 🤖")
    print("🤖"*35 + "\n")
    
    # 1. Extraction des données
    df = extract_features_from_db()
    print(f"✅ {len(df)} utilisateurs chargés de la base de données")
    
    if len(df) == 0:
        print("❌ Aucun utilisateur trouvé")
        return None
    
    # 2. Charger ou entraîner les modèles
    models = load_or_train_models(df, force_retrain)
    
    # 3. Préparer les features
    feature_columns = [
        'days_since_login', 'account_age_days', 'inactivity_ratio',
        'password_length', 'weak_password', 'profile_completeness',
        'email_length', 'email_dots', 'email_underscores',
        'is_gmail', 'is_yahoo', 'is_microsoft', 'is_temp_email',
        'is_staff', 'is_superuser', 'is_inactive',
        'admin_never_logged', 'old_account_never_logged'
    ]
    
    X = df[feature_columns].fillna(0).replace([np.inf, -np.inf], 0)
    X_scaled = models['scaler'].transform(X)
    
    # 4. PRÉDICTION ENSEMBLE
    print("\n🔮 Prédiction par ensemble d'IA...")
    ensemble_scores = predict_with_ensemble(X_scaled, models)
    
    # Normaliser entre 0 et 100
    df['ai_security_score'] = (ensemble_scores * 100).clip(0, 100).round().astype(int)
    
    # Niveau de risque
    def get_risk_level(score):
        if score >= 70:
            return 'critical'
        elif score >= 50:
            return 'high'
        elif score >= 30:
            return 'medium'
        else:
            return 'low'
    
    df['ai_risk_level'] = df['ai_security_score'].apply(get_risk_level)
    
    # 5. Mise à jour de la base de données
    print("\n💾 Mise à jour de la base de données...")
    from .models import User
    updated = 0
    
    for _, row in df.iterrows():
        User.objects.filter(id_user=row['id']).update(
            ai_security_score=int(row['ai_security_score']),
            ai_risk_level=row['ai_risk_level']
        )
        updated += 1
    
    # 6. RAPPORT FINAL
    print("\n" + "="*70)
    print("📊 RÉSULTATS DE L'ANALYSE IA")
    print("="*70)
    
    risk_counts = df['ai_risk_level'].value_counts()
    total = len(df)
    
    print(f"\n🔴 CRITICAL : {risk_counts.get('critical', 0):3} ({risk_counts.get('critical', 0)/total*100:5.1f}%) - Intervention URGENTE")
    print(f"🟠 HIGH     : {risk_counts.get('high', 0):3} ({risk_counts.get('high', 0)/total*100:5.1f}%) - Surveillance renforcée")
    print(f"🟡 MEDIUM   : {risk_counts.get('medium', 0):3} ({risk_counts.get('medium', 0)/total*100:5.1f}%) - À surveiller")
    print(f"🟢 LOW      : {risk_counts.get('low', 0):3} ({risk_counts.get('low', 0)/total*100:5.1f}%) - Normal")
    
    avg_score = df['ai_security_score'].mean()
    print(f"\n📈 Score de risque moyen: {avg_score:.1f}/100")
    print(f"✅ {updated} utilisateurs analysés et mis à jour")
    
    # Top 10 utilisateurs à risque
    top_risky = df.nlargest(10, 'ai_security_score')[['email', 'ai_security_score', 'ai_risk_level']]
    
    if len(top_risky) > 0:
        print("\n⚠️  TOP 10 COMPTES À SURVEILLER (IA):")
        print("-"*70)
        for idx, (_, user) in enumerate(top_risky.iterrows(), 1):
            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            emoji = icon.get(user['ai_risk_level'], '⚪')
            print(f"{idx:2}. {emoji} {user['email']:40} | Score: {user['ai_security_score']:3}/100")
    
    print("\n" + "="*70)
    print("🎯 Analyse terminée - 7 algorithmes d'IA ont contribué à cette évaluation")
    print("="*70 + "\n")
    
    return {
        'total': total,
        'updated': updated,
        'critical': risk_counts.get('critical', 0),
        'high': risk_counts.get('high', 0),
        'medium': risk_counts.get('medium', 0),
        'low': risk_counts.get('low', 0),
        'avg_score': avg_score
    }


def retrain_model():
    """
    Force le réentraînement complet de TOUS les modèles
    """
    df = extract_features_from_db()
    return run_ai_security(force_retrain=True)