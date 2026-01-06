
import logging
import sys
import os
from services.google_docs_service import GoogleDocsService

# Configure logging to stdout with flushing
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_config():
    print("--- STARTING GOOGLE AUTH TEST ---", flush=True)
    if os.path.exists("credentials.json"):
        print(f"Found credentials.json ({os.path.getsize('credentials.json')} bytes)", flush=True)
    else:
        print("ERROR: credentials.json NOT FOUND", flush=True)
        return

    try:
        print("Initializing GoogleDocsService...", flush=True)
        service = GoogleDocsService()
        
        if service.service:
            print("[OK] Authentication successful!", flush=True)
            
            print("Attempting to create a test document...", flush=True)
            try:
                url = service.create_doc("Test Doc from VSS", "This is a test document to verify credentials.")
                if url:
                    print(f"[OK] Document created successfully: {url}", flush=True)
                else:
                    print("[FAIL] Document creation failed (url is None).", flush=True)
            except Exception as doc_e:
                 print(f"[FAIL] Document creation error: {doc_e}", flush=True)
        else:
            print("[FAIL] Authentication failed (service is None). It might be waiting for browser login.", flush=True)
            
    except Exception as e:
        print(f"[FAIL] Exception occurred details: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    print("--- TEST COMPLETE ---", flush=True)

if __name__ == "__main__":
    test_config()
