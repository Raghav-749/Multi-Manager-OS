import json
import os
import shutil
import csv
from datetime import datetime
import utils

# ========================================================
# DATA LOADERS & SAVERS
# ========================================================
def auto_backup():
    """Generates an instantaneous secondary backup of the main data."""
    if os.path.exists(utils.DATA_FILE):
        try:
            shutil.copy(utils.DATA_FILE, utils.BACKUP_FILE)
        except Exception as e:
            utils.log_action(f"WARNING - Backup cascade failed: {e}")

def load_data():
    """Pulls Member JSON records into memory."""
    if not os.path.exists(utils.DATA_FILE):
        return []
    try:
        with open(utils.DATA_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        utils.log_action("ERROR - Could not load Database. Source Corrupted.")
        print("Critical Error: Database is corrupted.")
        return []

def save_data(data):
    """Commits JSON list to disk and triggers sequential auto-backup."""
    try:
        with open(utils.DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        auto_backup()
    except Exception as e:
        print(f"Critical System Error: DB Write Failed. {e}")
        utils.log_action(f"ERROR - Save transaction failed: {e}")

def load_users():
    """Loads authentication JSON; Bootstraps a default Admin user if none exists."""
    if not os.path.exists(utils.USERS_FILE):
        # Default fallback credentials Admin / admin123
        default_db = {"admin": utils.hash_password("admin123")}
        with open(utils.USERS_FILE, 'w') as file:
            json.dump(default_db, file, indent=4)
        return default_db
    try:
        with open(utils.USERS_FILE, 'r') as file:
            return json.load(file)
    except Exception:
        # Failsafe in case users.json corrupts
        return {"admin": utils.hash_password("admin123")}

def export_to_csv(data):
    """Marshals Python JSON Dict out directly into physical CSV."""
    print("\n--- Execute CSV Data Extract ---")
    if not data:
        print("Database is currently empty. No records to export.")
        return

    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"gym_records_{stamp}.csv"
    
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"Extraction successful: '{filename}' saved locally.")
        utils.log_action(f"CSV Export executed successfully to {filename}")
    except Exception as e:
        print(f"Extraction Failed. Access Denied or File Open: {e}")
        utils.log_action(f"ERROR - CSV Export denied: {e}")
