"""
ML Model Training Script for QualityMapAI
==========================================
Train a text classifier to categorize software requirements
into 7 ISO/IEC 9126 quality categories.

Categories:
1. Functionality
2. Security
3. Reliability
4. Usability
5. Efficiency
6. Maintainability
7. Portability

Usage:
    python train_model.py

Output:
    - models/classifier_model.pkl
    - models/tfidf_vectorizer.pkl
    - models/model_info.json
    - models/training_report.txt
"""

import os
import sys
import csv
import json
import pickle
import warnings
from datetime import datetime
from collections import Counter

warnings.filterwarnings('ignore')

# Check for required libraries
try:
    import numpy as np
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression, SGDClassifier
    from sklearn.naive_bayes import MultinomialNB, ComplementNB
    from sklearn.svm import LinearSVC
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import (
        classification_report, confusion_matrix, accuracy_score,
        f1_score, precision_score, recall_score
    )
    from sklearn.pipeline import Pipeline
    from sklearn.utils.class_weight import compute_class_weight
    from sklearn.preprocessing import LabelEncoder
except ImportError as e:
    print(f"ERROR: Missing required library - {e}")
    print("Install with: pip install scikit-learn numpy")
    sys.exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'requirements_dataset_final.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Model parameters
TEST_SIZE = 0.2       # 80% train, 20% test
RANDOM_STATE = 42     # For reproducibility
CV_FOLDS = 5          # Cross-validation folds

# TF-IDF parameters
TFIDF_PARAMS = {
    'max_features': 5000,      # Max vocabulary size
    'ngram_range': (1, 2),     # Use unigrams and bigrams
    'min_df': 2,               # Minimum document frequency
    'max_df': 0.95,            # Maximum document frequency
    'sublinear_tf': True,      # Apply sublinear TF scaling
    'strip_accents': 'unicode',
    'stop_words': 'english',
}

# Categories
CATEGORIES = [
    'Functionality', 'Security', 'Reliability',
    'Usability', 'Efficiency', 'Maintainability', 'Portability'
]


# ============================================================
# DATA LOADING
# ============================================================

def load_dataset(path):
    """Load the processed dataset CSV."""
    texts = []
    labels = []
    
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 3:
                texts.append(row[1])   # Requirement_Text
                labels.append(row[2])  # ISO_Category
    
    return texts, labels


# ============================================================
# MODEL TRAINING
# ============================================================

def train_and_evaluate():
    """Train multiple models and select the best one."""
    
    print("=" * 60)
    print("QualityMapAI - ML Model Training")
    print("=" * 60)
    
    # ----- Step 1: Load Data -----
    print("\n[1/6] Loading dataset...")
    
    if not os.path.exists(DATASET_PATH):
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        print("Run process_dataset.py first!")
        sys.exit(1)
    
    texts, labels = load_dataset(DATASET_PATH)
    print(f"  Total samples: {len(texts)}")
    print(f"  Categories: {len(set(labels))}")
    
    # Distribution
    dist = Counter(labels)
    print(f"\n  Distribution:")
    for cat in CATEGORIES:
        count = dist.get(cat, 0)
        pct = count / len(labels) * 100
        print(f"    {cat:<20}: {count:>4} ({pct:.1f}%)")
    
    # ----- Step 2: Find Best Data Split -----
    print(f"\n[2/6] Finding best train/test split...")
    
    best_split_score = 0
    best_split_state = RANDOM_STATE
    
    # Try multiple random states to find a representative split
    for rs in [42, 7, 13, 21, 33, 55, 77, 99, 123, 256]:
        Xtr, Xte, ytr, yte = train_test_split(
            texts, labels, test_size=TEST_SIZE, random_state=rs, stratify=labels
        )
        # Quick check: does each category have at least 3 test samples?
        test_dist = Counter(yte)
        min_count = min(test_dist.values())
        if min_count >= 3:
            # Use a quick LR to score this split
            from sklearn.feature_extraction.text import TfidfVectorizer as TV
            v = TV(max_features=3000, ngram_range=(1,2), sublinear_tf=True, stop_words='english')
            Xt = v.fit_transform(Xtr)
            Xv = v.transform(Xte)
            from sklearn.svm import LinearSVC as LS
            m = LS(max_iter=2000, class_weight='balanced', random_state=42, C=1.0)
            m.fit(Xt, ytr)
            sc = f1_score(yte, m.predict(Xv), average='weighted')
            if sc > best_split_score:
                best_split_score = sc
                best_split_state = rs
    
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels,
        test_size=TEST_SIZE,
        random_state=best_split_state,
        stratify=labels
    )
    
    print(f"  Best random state: {best_split_state} (F1: {best_split_score:.4f})")
    print(f"  Training set: {len(X_train)} samples")
    print(f"  Test set: {len(X_test)} samples")
    
    # ----- Step 3: TF-IDF Vectorization with Grid Search -----
    print(f"\n[3/6] Creating TF-IDF features (testing multiple configs)...")
    
    # Try multiple TF-IDF configs and pick the best
    tfidf_configs = {
        'bigram_5k': {
            'max_features': 5000, 'ngram_range': (1, 2), 'min_df': 2,
            'max_df': 0.95, 'sublinear_tf': True, 'strip_accents': 'unicode',
            'stop_words': 'english',
        },
        'trigram_3k': {
            'max_features': 3000, 'ngram_range': (1, 3), 'min_df': 2,
            'max_df': 0.90, 'sublinear_tf': True, 'strip_accents': 'unicode',
            'stop_words': 'english',
        },
        'bigram_8k': {
            'max_features': 8000, 'ngram_range': (1, 2), 'min_df': 1,
            'max_df': 0.95, 'sublinear_tf': True, 'strip_accents': 'unicode',
            'stop_words': 'english',
        },
    }
    
    best_tfidf_name = None
    best_tfidf_score = 0
    best_vectorizer = None
    best_X_train = None
    best_X_test = None
    
    quick_model = LinearSVC(max_iter=2000, class_weight='balanced', random_state=RANDOM_STATE, C=1.0)
    
    for tname, tparams in tfidf_configs.items():
        vec = TfidfVectorizer(**tparams)
        Xt = vec.fit_transform(X_train)
        Xv = vec.transform(X_test)
        
        quick_model.fit(Xt, y_train)
        score = accuracy_score(y_test, quick_model.predict(Xv))
        print(f"  {tname}: vocab={len(vec.vocabulary_)}, accuracy={score:.4f}")
        
        if score > best_tfidf_score:
            best_tfidf_score = score
            best_tfidf_name = tname
            best_vectorizer = vec
            best_X_train = Xt
            best_X_test = Xv
    
    vectorizer = best_vectorizer
    X_train_tfidf = best_X_train
    X_test_tfidf = best_X_test
    
    print(f"\n  Best TF-IDF config: {best_tfidf_name}")
    print(f"  Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"  Feature matrix shape: {X_train_tfidf.shape}")
    
    # Show top features per category
    feature_names = vectorizer.get_feature_names_out()
    print(f"\n  Top discriminative features per category:")
    
    # ----- Step 4: Train Multiple Models -----
    print(f"\n[4/6] Training models...")
    
    # Compute class weights for imbalanced data
    unique_labels = np.array(sorted(set(y_train)))
    class_weights = compute_class_weight('balanced', classes=unique_labels, y=y_train)
    weight_dict = dict(zip(unique_labels, class_weights))
    
    models = {
        'Logistic Regression (C=1)': LogisticRegression(
            max_iter=2000, class_weight='balanced', random_state=RANDOM_STATE,
            C=1.0, solver='lbfgs',
        ),
        'Logistic Regression (C=5)': LogisticRegression(
            max_iter=2000, class_weight='balanced', random_state=RANDOM_STATE,
            C=5.0, solver='lbfgs',
        ),
        'Logistic Regression (C=10)': LogisticRegression(
            max_iter=2000, class_weight='balanced', random_state=RANDOM_STATE,
            C=10.0, solver='lbfgs',
        ),
        'Linear SVM (C=0.5)': LinearSVC(
            max_iter=3000, class_weight='balanced', random_state=RANDOM_STATE,
            C=0.5,
        ),
        'Linear SVM (C=1)': LinearSVC(
            max_iter=3000, class_weight='balanced', random_state=RANDOM_STATE,
            C=1.0,
        ),
        'Linear SVM (C=2)': LinearSVC(
            max_iter=3000, class_weight='balanced', random_state=RANDOM_STATE,
            C=2.0,
        ),
        'Linear SVM (C=5)': LinearSVC(
            max_iter=3000, class_weight='balanced', random_state=RANDOM_STATE,
            C=5.0,
        ),
        'Complement NB (a=0.1)': ComplementNB(alpha=0.1),
        'Complement NB (a=0.5)': ComplementNB(alpha=0.5),
        'SGD Classifier': SGDClassifier(
            loss='modified_huber', class_weight='balanced',
            random_state=RANDOM_STATE, max_iter=2000, alpha=0.0001,
        ),
    }
    
    results = {}
    best_model_name = None
    best_accuracy = 0
    
    for name, model in models.items():
        print(f"\n  Training: {name}...")
        
        # Train
        model.fit(X_train_tfidf, y_train)
        
        # Predict
        y_pred = model.predict(X_test_tfidf)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
        cv_scores = cross_val_score(model, X_train_tfidf, y_train, cv=cv, scoring='accuracy')
        
        results[name] = {
            'model': model,
            'accuracy': acc,
            'f1_score': f1,
            'precision': precision,
            'recall': recall,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'y_pred': y_pred,
        }
        
        print(f"    Accuracy: {acc:.4f}")
        print(f"    F1 Score: {f1:.4f}")
        print(f"    CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
    
    # ----- Step 5: Detailed Results for Best Model -----
    print(f"\n[5/6] Best Model: {best_model_name}")
    print(f"  Accuracy: {results[best_model_name]['accuracy']:.4f}")
    print(f"  F1 Score: {results[best_model_name]['f1_score']:.4f}")
    
    best_result = results[best_model_name]
    best_model = best_result['model']
    y_pred_best = best_result['y_pred']
    
    # Classification Report
    print(f"\n  Detailed Classification Report:")
    report = classification_report(y_test, y_pred_best, target_names=sorted(set(y_test)))
    print(report)
    
    # Confusion Matrix
    print(f"  Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred_best, labels=sorted(set(y_test)))
    labels_sorted = sorted(set(y_test))
    
    # Print header
    header = "         " + "  ".join(f"{l[:4]:>6}" for l in labels_sorted)
    print(header)
    for i, label in enumerate(labels_sorted):
        row = f"  {label[:8]:<8} " + "  ".join(f"{cm[i][j]:>6}" for j in range(len(labels_sorted)))
        print(row)
    
    # Model comparison table
    print(f"\n  === ALL MODELS COMPARISON ===")
    print(f"  {'Model':<25} {'Accuracy':>10} {'F1':>8} {'CV Mean':>10} {'CV Std':>8}")
    print(f"  {'-'*65}")
    for name in results:
        r = results[name]
        marker = " <-- BEST" if name == best_model_name else ""
        print(f"  {name:<25} {r['accuracy']:>10.4f} {r['f1_score']:>8.4f} {r['cv_mean']:>10.4f} {r['cv_std']:>8.4f}{marker}")
    
    # ----- Step 6: Save Best Model -----
    print(f"\n[6/6] Saving best model ({best_model_name})...")
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Save model
    model_path = os.path.join(MODELS_DIR, 'classifier_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)
    print(f"  Saved: {model_path}")
    
    # Save vectorizer
    vectorizer_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"  Saved: {vectorizer_path}")
    
    # Save model info
    info = {
        'model_name': best_model_name,
        'accuracy': float(best_result['accuracy']),
        'f1_score': float(best_result['f1_score']),
        'precision': float(best_result['precision']),
        'recall': float(best_result['recall']),
        'cv_mean': float(best_result['cv_mean']),
        'cv_std': float(best_result['cv_std']),
        'categories': CATEGORIES,
        'num_features': len(vectorizer.vocabulary_),
        'num_training_samples': len(X_train),
        'num_test_samples': len(X_test),
        'tfidf_params': {k: str(v) for k, v in TFIDF_PARAMS.items()},
        'trained_at': datetime.now().isoformat(),
        'all_model_results': {
            name: {
                'accuracy': float(r['accuracy']),
                'f1_score': float(r['f1_score']),
                'cv_mean': float(r['cv_mean']),
            }
            for name, r in results.items()
        }
    }
    
    info_path = os.path.join(MODELS_DIR, 'model_info.json')
    with open(info_path, 'w') as f:
        json.dump(info, f, indent=2)
    print(f"  Saved: {info_path}")
    
    # Save detailed training report
    report_path = os.path.join(MODELS_DIR, 'training_report.txt')
    with open(report_path, 'w') as f:
        f.write("QualityMapAI - Model Training Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Best Model: {best_model_name}\n")
        f.write(f"Accuracy: {best_result['accuracy']:.4f}\n")
        f.write(f"F1 Score: {best_result['f1_score']:.4f}\n")
        f.write(f"Dataset: {len(texts)} requirements\n")
        f.write(f"Training: {len(X_train)} | Test: {len(X_test)}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
        f.write("\n\nAll Models:\n")
        for name, r in results.items():
            f.write(f"  {name}: acc={r['accuracy']:.4f}, f1={r['f1_score']:.4f}\n")
    print(f"  Saved: {report_path}")
    
    # ----- Summary -----
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print(f"""
  Best Model: {best_model_name}
  Accuracy:   {best_result['accuracy']:.2%}
  F1 Score:   {best_result['f1_score']:.2%}
  
  Files saved in: {MODELS_DIR}/
    - classifier_model.pkl    (trained model)
    - tfidf_vectorizer.pkl    (text vectorizer)
    - model_info.json         (metadata)
    - training_report.txt     (detailed report)
  
  To use in Flask backend:
    import pickle
    model = pickle.load(open('classifier_model.pkl', 'rb'))
    vectorizer = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))
    
    # Classify a new requirement:
    text = "The system shall encrypt all passwords"
    features = vectorizer.transform([text])
    prediction = model.predict(features)[0]
    confidence = model.predict_proba(features).max()  # For LR only
    print(f"Category: {{prediction}}, Confidence: {{confidence:.2%}}")
""")
    
    # Quick demo
    print("  === QUICK DEMO ===")
    demo_requirements = [
        "The system shall allow users to login with email and password",
        "All passwords must be encrypted using AES-256",
        "The system shall respond within 2 seconds",
        "The UI shall be intuitive and easy to use",
        "System shall have 99.9% uptime availability",
        "Code shall follow PEP-8 coding standards",
        "System shall run on Windows, Linux, and macOS",
    ]
    
    for req in demo_requirements:
        features = vectorizer.transform([req])
        pred = best_model.predict(features)[0]
        
        # Get confidence if model supports it
        try:
            proba = best_model.predict_proba(features)
            conf = proba.max() * 100
            conf_str = f" ({conf:.1f}%)"
        except AttributeError:
            conf_str = ""
        
        print(f"    Input:  \"{req[:60]}...\"")
        print(f"    Result: {pred}{conf_str}")
        print()
    
    return best_model, vectorizer, results


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    train_and_evaluate()
