import data_handler
import member_service
import utils
import getpass

# ========================================================
# AUTHORIZATION TUNNELS
# ========================================================
def authenticate():
    """Requests and securely checks Admin inputs against configuration config."""
    print("\n" + "-"*40)
    print("   ADMINISTRATIVE AUTHENTICATION   ")
    print("-"*40)
    
    users_db = data_handler.load_users()
    
    username = input("Username: ").strip()
    # Masks string visually for secure over-the-shoulder inputs handling
    password = getpass.getpass("Password: ").strip() 
    
    hashed_pass = utils.hash_password(password)
    
    if username in users_db and users_db[username] == hashed_pass:
        return True
    return False

# ========================================================
# DASHBOARDS
# ========================================================
def admin_menu(data):
    while True:
        print("\n" + "="*45)
        print("          ADMINISTRATIVE CONTROL DASHBOARD")
        print("="*45)
        print("  1. Intake New Member")
        print("  2. Directory: View & Search")
        print("  3. Modify Member Profile")
        print("  4. Expunge Member Profile")
        print("  5. Penalty Audits & Expiration Reports")
        print("  6. Business Analytics")
        print("  7. Run Data Export (CSV)")
        print("  0. Secure Logout")
        print("="*45)
        
        choice = input("Command Access: ").strip()
        
        if choice == '1': member_service.add_member(data)
        elif choice == '2': 
            sub = input("  -> [1] View Master List | [2] Run Search: ").strip()
            if sub == '1': member_service.view_members(data)
            elif sub == '2': member_service.search_member(data)
            else: print("Invalid subcommand.")
        elif choice == '3': member_service.update_member(data)
        elif choice == '4': member_service.delete_member(data)
        elif choice == '5': member_service.check_alerts(data)
        elif choice == '6': member_service.generate_statistics(data)
        elif choice == '7': data_handler.export_to_csv(data)
        elif choice == '0':
            utils.log_action("AUTH: Administrator logout.")
            break
        else:
            print("Unrecognized command.")

def viewer_menu(data):
    while True:
        print("\n" + "="*45)
        print("          RECEPTION / KIOSK DASHBOARD")
        print("="*45)
        print("  1. Browse Member Master List")
        print("  2. Search Specific Client")
        print("  0. Quick Logout")
        print("="*45)
        
        choice = input("Command Access: ").strip()
        
        if choice == '1': member_service.view_members(data)
        elif choice == '2': member_service.search_member(data)
        elif choice == '0':
            utils.log_action("AUTH: Kiosk logout.")
            break
        else:
            print("Unrecognized command.")

# ========================================================
# KERNEL INITIALIZATION
# ========================================================
def main():
    """Bootloader & Main System Routing"""
    # Force initialize configs and loads
    data = data_handler.load_data()
    utils.log_action("SYSTEM: Primary boot sequence complete. Awaiting Login.")
    
    while True:
        print("\n" + "#"*55)
        print(" MULTI-PURPOSE GYM MANAGER SYSTEM - V3 (PRODUCTION) ")
        print("#"*55)
        print("  [1] Secure Admin Login (Write Permissions)")
        print("  [2] Kiosk Reader Portal (Read-Only Permissions)")
        print("  [0] Disarm & Exit Server")
        print("#"*55)
        
        access_path = input("Set Operation Mode: ").strip()
        
        if access_path == '1':
            if authenticate():
                utils.log_action("AUTH: Admin root-access granted.")
                print("\n[!] Verified. Tunneling to Dashboard...")
                admin_menu(data)
            else:
                utils.log_action("AUTH: Failed intrusion attempt on Admin login.")
                print("\n[X] DENIED: Invalid credentials detected.")
                print("    (Hint: First-time setup defaults are admin//admin123)")
        
        elif access_path == '2':
            utils.log_action("AUTH: Kiosk Reader instantiated.")
            viewer_menu(data)
            
        elif access_path == '0':
            utils.log_action("SYSTEM: Root command invoked shutdown protocol. Goodbye.")
            print("\nShutting down master processes. Data synced successfully.")
            break
        else:
            print("Unrecognized mode selector. Please read prompt.")

if __name__ == '__main__':
    main()
