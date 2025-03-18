import requests


API_KEY = 'sk-921e10a4c42740a5854600eab59bb8e6'
BASE_URL = "https://api.deepseek.com/beta"  # Update if necessary

def test_deepseek():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "What is DeepSeek AI?"}]
    }

    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers)

    if response.status_code == 200:
        print("✅ Success:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)

test_deepseek()