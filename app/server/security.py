import json

def load_api_keys() -> dict:
    try:
        with open('api_keys.json', 'r') as f:
            return json.loads(f.read())
    except FileNotFoundError:
        with open('api_keys.json', 'w') as f:
            json.dump({}, f)
        return {}

def key_exists(api_key: str) -> bool:
    api_keys = load_api_keys()
    return api_key in api_keys
