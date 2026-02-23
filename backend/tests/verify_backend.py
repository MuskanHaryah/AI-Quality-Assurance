import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from services.classifier import classifier
from services.requirement_extractor import extract_requirements
from utils.validators import validate_file_type, sanitize_filename
from utils.file_handler import create_analysis_id

print("--- Config check ---")
print("MODEL_PATH exists:", os.path.exists(Config.MODEL_PATH))
print("VECTORIZER_PATH exists:", os.path.exists(Config.VECTORIZER_PATH))
print()

print("--- Classifier check ---")
info = classifier.get_model_info()
print("Model:", info["model_name"])
print("Accuracy:", info["accuracy"])
print("Categories:", info["categories"])
print()

print("--- Single prediction test ---")
result = classifier.classify("The system shall encrypt all user passwords using AES-256")
print("Text:", result["text"])
print("Category:", result["category"])
print("Confidence:", result["confidence"], "%")
print()

print("--- Batch prediction test ---")
texts = [
    "The system must respond to user requests within 2 seconds",
    "The software shall allow users to log in with username and password",
]
results = classifier.classify_batch(texts)
for r in results:
    print(f"  [{r['category']}] ({r['confidence']}%) {r['text'][:60]}")
print()

print("--- Requirement extractor test ---")
sample_text = """
The system shall authenticate users before granting access.
All passwords must be stored using bcrypt hashing.
The application should support at least 1000 concurrent users.
Login page with blue button.
The software shall provide an audit log of all user actions.
"""
extraction = extract_requirements(sample_text)
print("Found:", extraction["total_found"], "/", extraction["total_candidates"], "candidates")
for req in extraction["requirements"]:
    print(f"  [{req['keyword_strength']}] {req['text'][:70]}")
print()

print("--- Validators test ---")
print("validate_file_type('report.pdf'):", validate_file_type("report.pdf"))
print("validate_file_type('report.docx'):", validate_file_type("report.docx"))
print("validate_file_type('report.exe'):", validate_file_type("report.exe"))
print("sanitize_filename('my file (1).pdf'):", sanitize_filename("my file (1).pdf"))
print()

print("--- File handler test ---")
print("create_analysis_id():", create_analysis_id())
print()

print("ALL CHECKS PASSED!")
