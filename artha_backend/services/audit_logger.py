import json
import datetime
from datetime import timezone
import os
import hashlib
import queue
import threading

# Thread-safe queue for async logging
_LOG_QUEUE = queue.Queue()

def _log_worker():
    while True:
        record_str, log_file = _LOG_QUEUE.get()
        if record_str is None:
            break
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(record_str + "\n")
        except Exception as e:
            print(f"Failed to write to audit log file: {e}")
        finally:
            _LOG_QUEUE.task_done()

# Start background writer thread
_worker_thread = threading.Thread(target=_log_worker, daemon=True)
_worker_thread.start()

def log_event(event_data):
    """
    Appends events to a secure local audit trail using a background worker thread.
    """
    timestamp = datetime.datetime.now(timezone.utc).isoformat()
    log_record = {
        "timestamp": timestamp,
        "payload": event_data
    }
    
    # Generate verification signature hash for audit integrity
    serialized = json.dumps(log_record, sort_keys=True)
    record_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    log_record["integrity_hash"] = record_hash
    
    # Print to system console
    print(f"[AUDIT] {serialized}")
    
    # Append to local file using background queue
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_file = os.path.join(base_dir, "audit.log")
        _LOG_QUEUE.put((json.dumps(log_record), log_file))
    except Exception as e:
        print(f"Failed to queue audit log: {e}")
        
    return log_record


def log_chain_event(plan_id: str, customer_id: str, chain_state: dict, confidence: float, decision: str):
    """Persist full wealth chain artifacts for compliance audit."""
    return log_event({
        "event_type": "wealth_chain_audit",
        "plan_id": plan_id,
        "customer_id": customer_id,
        "confidence": confidence,
        "decision": decision,
        "chain_artifacts": chain_state,
    })