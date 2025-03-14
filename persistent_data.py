import json
import os

DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def save_data(data, path):
    new_path = os.path.join(DATA_FOLDER, path)
    with open(new_path, 'w') as f:
        json.dump(data, f)

def load_data(path):
    new_path = os.path.join(DATA_FOLDER, path)
    try:
        with open(new_path, 'r') as f:
            return json.load(f)
    except:
        return None