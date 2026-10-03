import sys
sys.stdout.reconfigure(encoding='utf-8')
import httpx
import json

BASE = 'http://localhost:8000/api'

TESTS = [
    ('hi', 'GENERAL_CHAT'),
    ('introduce ur self', 'GENERAL_CHAT'),
    ('what can you do?', 'GENERAL_CHAT'),
    ('tell me a joke', 'GENERAL_CHAT'),
    ('explain machine learning', 'GENERAL_CHAT'),
    ('my order is late', 'RETAIL_SUPPORT'),
    ('nobody is helping me and I am very frustrated', 'ESCALATION'),
]

def run_live_tests():
    # Create a session
    print('Creating session...')
    r = httpx.post(f'{BASE}/chat/sessions', json={'customer_name': 'TestUser'}, timeout=10)
    session_id = r.json()['session_id']
    print(f'Session: {session_id}')

    print()
    print('=' * 70)
    for msg, expected_mode in TESTS:
        r = httpx.post(
            f'{BASE}/chat/message',
            json={'session_id': session_id, 'message': msg, 'llm_provider': 'auto'},
            timeout=20
        )
        data = r.json()
        mode = data.get('interaction_mode', 'UNKNOWN')
        sentiment = data.get('sentiment', '?')
        intent = data.get('intent', '?')
        response_text = data.get('assistant_response') or data.get('empathetic_response') or ''
        provider = data.get('llm_provider', '?')
        
        status = 'PASS' if mode == expected_mode else 'FAIL'
        
        # Check for banned retail phrases in general chat
        banned_found = ''
        if expected_mode == 'GENERAL_CHAT':
            banned = [
                'Thank you for contacting TCS Retail Support',
                "I'm sorry you're facing this problem",
                'Please give me a few more details'
            ]
            for b in banned:
                if b.lower() in response_text.lower():
                    banned_found = f' | BANNED PHRASE: {b}'
                    status = 'FAIL'
        
        print(f'[{status}] "{msg[:40]}"')
        print(f'       Mode: {mode} (expected: {expected_mode}) | Sentiment: {sentiment} | Intent: {intent}')
        print(f'       Provider: {provider}')
        print(f'       Response: {response_text[:120]}...{banned_found}')
        print()

if __name__ == '__main__':
    run_live_tests()
