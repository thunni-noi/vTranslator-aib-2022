import json
import requests


def api_test(api_token):
    api_url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {api_token}"}
    
    test_payload = 'Tell me more about '
    data = json.dumps(test_payload)
    response = requests.request("POST", api_url, headers=headers, data=data)
    output = json.loads(response.content.decode("utf-8"))
    if 'error' in output:
        return False
    else:
        return True
        
        
if __name__ == "__main__":
    api_test('testkey')