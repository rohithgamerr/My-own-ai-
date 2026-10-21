
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_execution():
    print("Testing Correct SQL...")
    payload = {"sql": "SELECT name FROM users WHERE id = 1", "challenge_id": "basic_1"}
    resp = requests.post(f"{BASE_URL}/execute", json=payload)
    print(f"Response: {resp.json()}")
    assert resp.json()["is_correct"] == True

    print("\nTesting Incorrect SQL...")
    payload = {"sql": "SELECT name FROM users WHERE id = 2", "challenge_id": "basic_1"}
    resp = requests.post(f"{BASE_URL}/execute", json=payload)
    print(f"Response: {resp.json()}")
    assert resp.json()["is_correct"] == False

    print("\nTesting Daily Challenge...")
    resp = requests.get(f"{BASE_URL}/challenge/daily?module=Basics")
    print(f"Response: {resp.json()}")
    assert "id" in resp.json()

if __name__ == "__main__":
    try:
        test_execution()
        print("\nALL TESTS PASSED")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
