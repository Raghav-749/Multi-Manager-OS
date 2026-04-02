import uuid
from datetime import datetime, timedelta
import data_handler
import utils

# ========================================================
# VALIDATION SUB-LOGIC
# ========================================================
def check_duplicate_phone(data, phone, exclude_id=None):
    """Checks the dataset to ensure no two accounts share identical phone IDs."""
    for m in data:
        if m['phone'] == phone and m['id'] != exclude_id:
            return True
    return False

# ========================================================
# CORE CRUD SERVICES
# ========================================================
def add_member(data):
    """Creates a member leveraging strict validation controls."""
    print("\n" + "-"*40)
    print("   NEW MEMBER INTAKE FORM   ")
    print("-"*40)
    
    name = utils.get_non_empty_string("Enter Member Name: ")
    age = utils.get_valid_integer("Enter Age (Years): ", min_val=12) # Reasonable minimum age
    
    # Phone uniqueness lock
    while True:
        phone = utils.get_valid_phone("Enter Contact Phone (Digits only): ")
        if check_duplicate_phone(data, phone):
            print("Error: Account exists under that phone number.")
        else:
            break
            
    print("\nAvailable Enrollment Plans:")
    for plan_key, plan_data in utils.AVAILABLE_PLANS.items():
        print(f" [{plan_key}] - {plan_data['name']} ({plan_data['days']} Days)")
        
    plan_choice = utils.get_valid_choice("\nAssign Plan ID: ", list(utils.AVAILABLE_PLANS.keys()))
    
    join_date = utils.get_valid_date("Input Join Date [YYYY-MM-DD]: ")
    days_to_add = utils.AVAILABLE_PLANS[plan_choice]['days']
    expiry_date = join_date + timedelta(days=days_to_add)
    
    status = utils.get_valid_choice("Payment Validated? [Paid/Unpaid]: ", ["Paid", "Unpaid", "paid", "unpaid"]).capitalize()
    
    member_id = "GYM-" + str(uuid.uuid4())[:6].upper()
    
    # Construct schema payload
    member = {
        "id": member_id,
        "name": name,
        "age": age,
        "phone": phone,
        "plan_id": plan_choice,
        "plan_name": utils.AVAILABLE_PLANS[plan_choice]['name'],
        "join_date": str(join_date),
        "expiry_date": str(expiry_date),
        "status": status
    }
    
    data.append(member)
    data_handler.save_data(data)
    utils.log_action(f"ADDED: Member '{name}' via ID {member_id}")
    
    print(f"\n[!] Success. User Registered: {member_id}")
    print(f"[!] Target Expiry Populated : {expiry_date}")

def view_members(data):
    """Tabulates active members using aesthetic CLI formatting."""
    print("\n" + "="*85)
    print(f"{'SYS-ID':<12} | {'FULL NAME':<16} | {'PRIMARY PHONE':<14} | {'PLAN TIER':<10} | {'EXPIRATION':<11} | {'STATUS':<8}")
    print("="*85)
    if not data:
        print(" > Database currently empty.")
    else:
        for m in data:
            print(f"{m['id']:<12} | {m['name'][:16]:<16} | {m['phone']:<14} | {m['plan_name'][:10]:<10} | {m['expiry_date']:<11} | {m['status']:<8}")
    print("="*85)

def search_member(data):
    """Filters dataset locally for fuzzy matching IDs or Names."""
    print("\n--- Directory Search Engine ---")
    query = utils.get_non_empty_string("Input Member Name or SYS-ID: ").lower()
    
    results = [m for m in data if query in m['name'].lower() or query == m['id'].lower()]
    view_members(results)

def update_member(data):
    """Selectively patches components of a profile while maintaining rest of dict."""
    print("\n--- Profile Modifier Engine ---")
    member_id = utils.get_non_empty_string("Input Exact Member ID: ").upper()
    
    for m in data:
        if m['id'] == member_id:
            print(f"\nProfile Found: '{m['name']}'. Leave input blank to bypass edit.")
            
            new_name = input(f"Update Name [{m['name']}]: ").strip()
            if new_name: m['name'] = new_name
            
            new_phone = input(f"Update Phone [{m['phone']}]: ").strip()
            if new_phone:
                if new_phone.isdigit() and len(new_phone) >= 10:
                    if check_duplicate_phone(data, new_phone, m['id']):
                        print(" > Action Denied. Phone registered on another profile.")
                    else:
                        m['phone'] = new_phone
                else:
                    print(" > Action Denied. Corrupt phone format.")
            
            new_status = input(f"Update Payment/Status [{m['status']}]: ").strip().capitalize()
            if new_status in ["Paid", "Unpaid"]:
                m['status'] = new_status
                
            data_handler.save_data(data)
            utils.log_action(f"MODIFIED: Profile adjusted for {member_id}")
            print("\n[!] Profile Synchronized Successfully.")
            return
            
    print("Error: Target ID not located on network.")

def delete_member(data):
    """Expunges a profile permanently from working JSON memory."""
    print("\n--- Profile Eradication Protocol ---")
    member_id = utils.get_non_empty_string("Input Exact Member ID to delete: ").upper()
    
    for i, m in enumerate(data):
        if m['id'] == member_id:
            confirm = input(f"CRITICAL: Wipe {m['name']} from database completely? (y/n): ").strip().lower()
            if confirm == 'y':
                del data[i]
                data_handler.save_data(data)
                utils.log_action(f"DELETED: Network wipe for '{m['name']}' / {member_id}")
                print("[!] Profile completely discarded.")
            else:
                print("Eradication cancelled.")
            return
    print("Error: No such ID located.")

# ========================================================
# ANALYTICS & REVENUE TRACKING
# ========================================================
def check_alerts(data):
    """Locates Overdue statuses and compiles accumulated Late Fees globally."""
    print("\n--- System Audit: Penalties & Alerts ---")
    today = datetime.now().date()
    alerts_triggered = 0
    
    for m in data:
        try:
            exp_date = datetime.strptime(m['expiry_date'], "%Y-%m-%d").date()
            diff_days = (exp_date - today).days
            
            if diff_days < 0:
                fee = abs(diff_days) * utils.LATE_FEE_PER_DAY if m['status'] == 'Unpaid' else 0
                fee_display = f"| Penalty: ${fee:.2f}" if fee > 0 else "| Financials Cleared"
                
                print(f" [EXPIRED] {m['name']} ({m['id']}) overdue {abs(diff_days)} Day(s) {fee_display}")
                alerts_triggered += 1
                
            elif 0 <= diff_days <= 7:
                print(f" [WARNING] {m['name']} ({m['id']}) grace period ends in {diff_days} Day(s)!")
                alerts_triggered += 1
        except Exception:
            pass # Skips completely unparseable timestamps quietly
            
    if alerts_triggered == 0:
        print(" > Network clean. Zero alerts active.")

def generate_statistics(data):
    """Aggregates demographic macro-data across the database."""
    print("\n--- High-Level Business Metrics ---")
    total_users = len(data)
    if total_users == 0:
        print(" > Metric aggregation unavailable. Zero users.")
        return
        
    today = datetime.now().date()
    active_count = 0
    pending_cashFlow = 0
    
    for m in data:
        if m['status'] == 'Unpaid':
            pending_cashFlow += 1
        try:
            if datetime.strptime(m['expiry_date'], "%Y-%m-%d").date() >= today:
                active_count += 1
        except:
            pass
            
    print(f"  Gross Audience       : {total_users}")
    print(f"  Active Memberships   : {active_count}")
    print(f"  Inactive / Expired   : {total_users - active_count}")
    print(f"  Unpaid Receivables   : {pending_cashFlow} Invoices Out")
