import hashlib
from datetime import datetime

# ========================================================
# SYSTEM CONFIGURATION
# ========================================================
DATA_FILE = 'data.json'
BACKUP_FILE = 'backup.json'
USERS_FILE = 'users.json'
LOG_FILE = 'log.txt'

LATE_FEE_PER_DAY = 2.0  # Constant penalty fee

# Flexible dynamic plans
AVAILABLE_PLANS = {
    "1": {"name": "1 Month", "days": 30},
    "3": {"name": "3 Months", "days": 90},
    "6": {"name": "6 Months", "days": 180},
    "12": {"name": "1 Year", "days": 365}
}

# ========================================================
# SECURITY & LOGGING
# ========================================================
def hash_password(password):
    """Secures passwords by returning a SHA-256 hash string."""
    return hashlib.sha256(password.encode()).hexdigest()

def log_action(action_msg):
    """Appends an operational log to log.txt with timestamps."""
    with open(LOG_FILE, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {action_msg}\n")

# ========================================================
# DATA VALIDATION HELPERS
# ========================================================
def get_non_empty_string(prompt):
    """Prevents empty inputs and whitespace-only entries."""
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Error: Input cannot be uniquely empty.")

def get_valid_phone(prompt):
    """Strictly ensures a phone string is numerical and of valid length."""
    while True:
        phone = input(prompt).strip()
        if phone.isdigit() and len(phone) >= 10:
            return phone
        print("Error: Phone number must contain only digits and be at least 10 numbers long.")

def get_valid_date(prompt):
    """Checks input against exact Date formatting dynamically."""
    while True:
        date_str = input(prompt).strip()
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Error: Invalid date format. Please properly use YYYY-MM-DD.")
            
def get_valid_integer(prompt, min_val=None):
    """Ensures input evaluates to a standard Integer within bounds."""
    while True:
        try:
            val = int(input(prompt).strip())
            if min_val is not None and val < min_val:
                print(f"Error: Value must be at least {min_val}.")
                continue
            return val
        except ValueError:
            print("Error: Invalid number format.")

def get_valid_choice(prompt, choices):
    """Ensures user selects from an explicit list of available keys."""
    while True:
        val = input(prompt).strip()
        if val in choices:
            return val
        print(f"Error: Invalid choice. Available options: {', '.join(choices)}")
