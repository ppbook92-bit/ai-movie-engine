from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "data_store.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.route('/get_batch', methods=['GET'])
def api_get_batch():
    user_id = request.args.get('user_id', 'user_101')
    data = load_data()
    user = data.get(user_id)
    
    if not user:
        return jsonify({"status": "error", "message": f"User {user_id} not found."}), 404

    queue = user.get("queue_35", [])
    
    if len(queue) >= 5:
        batch = queue[:5]
        user["queue_35"] = queue[5:]
        user["current_batch"] = batch
        save_data(data)
        return jsonify({"status": "success", "batch": batch})
    elif len(queue) > 0:
        batch = queue
        user["queue_35"] = []
        user["current_batch"] = batch
        save_data(data)
        return jsonify({"status": "success", "batch": batch})
    else:
        return jsonify({"status": "empty", "message": "Queue is empty! Need new AI batch."})

@app.route('/process_checkmarks', methods=['POST'])
def api_process_checkmarks():
    req_data = request.json
    user_id = req_data.get('user_id', 'user_101')
    watched_titles = req_data.get('watched_titles', [])
    
    data = load_data()
    user = data.get(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found."}), 404

    current_batch = user.get("current_batch", [])
    
    for title in current_batch:
        if title in watched_titles:
            user["watched_blacklist"].append(title)
        else:
            user["unwatched_recycle_pool"].append(title)
            
    user["current_batch"] = []
    save_data(data)
    
    return jsonify({"status": "success", "message": "Checkmarks processed."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
