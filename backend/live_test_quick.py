
"""Quick live API test for chatbot behavior verification."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import httpx

BASE = "http://localhost:8000/api"

def run_quick_tests():
    # Create session
    sess = httpx.post(f"{BASE}/chat/sessions", json={"customer_name": "TestUser"}, timeout=10).json()
    sid = sess["session_id"]
    print(f"Session: {sid}\n{'='*60}")

    test_messages = [
        "hi",
        "introduce ur self",
        "tell me a joke",
        "what can you do",
        "my order is late",
        "where is order #45821",
        "nobody is helping me and I am very frustrated",
    ]

    for msg in test_messages:
        try:
            r = httpx.post(f"{BASE}/chat/message", json={
                "session_id": sid, "message": msg, "llm_provider": "auto"
            }, timeout=20).json()
            
            mode = r.get("interaction_mode", "UNKNOWN")
            sent = r.get("sentiment", "?")
            score = r.get("sentiment_score", "?")
            intent = r.get("intent", "?")
            emotion = r.get("emotion", "?")
            provider = r.get("llm_provider", "?")
            resp = (r.get("assistant_response") or r.get("empathetic_response") or "NO_RESPONSE")[:120]
            esc = r.get("escalation", {})
            
            print(f'MSG: "{msg}"')
            print(f"  MODE: {mode}")
            print(f"  SENTIMENT: {sent} ({score})")
            print(f"  INTENT: {intent} | EMOTION: {emotion}")
            print(f"  PROVIDER: {provider}")
            print(f"  ESCALATION: should_escalate={esc.get('should_escalate')} score={esc.get('score')} severity={esc.get('severity')}")
            print(f"  RESPONSE: {resp}")
            print(f"  ---")
        except Exception as e:
            print(f'MSG: "{msg}" => ERROR: {e}')
            print(f"  ---")

if __name__ == "__main__":
    run_quick_tests()
