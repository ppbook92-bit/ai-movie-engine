import json
import os

DATA_FILE = "data_store.json"

def load_data():
    """Load existing user data from the local JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    """Save user data back to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_next_batch(user_id):
    """
    Pulls 5 movies from queue_35 into current_batch.
    Returns the 5 movies for the user to see.
    """
    data = load_data()
    user = data.get(user_id)
    if not user:
        return {"status": "error", "message": f"User {user_id} not found."}

    queue = user.get("queue_35", [])
    
    if len(queue) >= 5:
        # Take the first 5 movies
        batch = queue[:5]
        # Keep the rest in the queue
        user["queue_35"] = queue[5:]
        user["current_batch"] = batch
        save_data(data)
        return {"status": "success", "batch": batch}
    elif len(queue) > 0:
        # Take whatever is left if less than 5
        batch = queue
        user["queue_35"] = []
        user["current_batch"] = batch
        save_data(data)
        return {"status": "success", "batch": batch}
    else:
        return {"status": "empty", "message": "Queue is empty! Need new AI batch."}

def process_checkmarks(user_id, watched_titles):
    """
    Moves checked titles from current_batch into watched_blacklist,
    and moves unchecked titles into unwatched_recycle_pool.
    """
    data = load_data()
    user = data.get(user_id)
    if not user:
        return {"status": "error", "message": "User not found."}

    current_batch = user.get("current_batch", [])
    
    for title in current_batch:
        if title in watched_titles:
            user["watched_blacklist"].append(title)
        else:
            user["unwatched_recycle_pool"].append(title)
            
    # Clear the current batch now that we've processed it
    user["current_batch"] = []
    save_data(data)
    
    return {"status": "success", "message": "Checkmarks processed."}
