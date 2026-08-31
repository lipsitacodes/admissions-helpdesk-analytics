import requests
import json
from database import get_database

# Test the backend API
url = "http://127.0.0.1:5000/query"
payload = {"query": "scholarship kya hai?"}

print("Sending query to backend...")
response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}\n")

if response.status_code == 200:
    result = response.json()
    print(f"Query: {result.get('query')}")
    print(f"Predicted Intent: {result.get('predicted_intent')}")
    print(f"Confidence: {result.get('classifier_confidence')}")
    print(f"Escalated: {result.get('escalated')}")
    print(f"\nAnswer: {result.get('answer')[:150]}...")
    
    # Check MongoDB
    print("\n" + "="*50)
    print("Checking MongoDB for saved interaction...")
    db = get_database()
    interactions = db["helpdesk_interactions"]
    recent = interactions.find_one(sort=[("timestamp", -1)])
    if recent:
        print(f"✓ Latest interaction saved in MongoDB:")
        print(f"  - Query: {recent.get('query')}")
        print(f"  - Intent: {recent.get('predicted_intent')}")
        print(f"  - Timestamp: {recent.get('timestamp')}")
    else:
        print("✗ No interactions found in MongoDB")
else:
    print(f"Error: {response.text}")
