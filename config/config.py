import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INCOMING = os.path.join(BASE_DIR, "Incoming")
PROCESSING = os.path.join(BASE_DIR, "Processing")
PROCESSED = os.path.join(BASE_DIR, "Processed")