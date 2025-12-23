try:
    print("1. Importing torch...")
    import torch
    print(f"   Success. Version: {torch.__version__}")
except ImportError as e:
    print(f"   Failed: {e}")

try:
    print("2. Importing sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    print("   Success.")
except Exception as e:
    import traceback
    traceback.print_exc()
