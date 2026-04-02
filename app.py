from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import json
import os
import uuid
import csv
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "super_secret_dynamic_key"

DATA_FILE = 'data.json'
LATE_FEE_PER_DAY = 2.0

# ==========================================
# DYNAMIC MODULE CONFIGURATION
# ==========================================
MODULES = {
    "gym": {
        "name": "Gym Management",
        "icon": "🏋️",
        "fields": [
            {"id": "name", "label": "Member Name", "type": "text"},
            {"id": "phone", "label": "Phone Number", "type": "text"},
            {"id": "plan", "label": "Plan Duration (Days)", "type": "number"},
            {"id": "start_date", "label": "Join Timestamp", "type": "date"}
        ],
        "has_expiry": True,
        "date_field": "start_date",
        "duration_field": "plan", 
        "has_status": True,
        "status_options": ["Paid", "Unpaid"]
    },
    "library": {
        "name": "Library Management",
        "icon": "📚",
        "fields": [
            {"id": "book_title", "label": "Book Title", "type": "text"},
            {"id": "borrower", "label": "Borrower Full Name", "type": "text"},
            {"id": "issue_date", "label": "Issue Date", "type": "date"},
            {"id": "return_date", "label": "Expected Return / Deadline", "type": "date"}
        ],
        "has_expiry": True,
        "date_field": "return_date",
        "duration_field": None, # Indicates the date_field is the absolute expiry rule
        "has_status": True,
        "status_options": ["Borrowed", "Returned"]
    },
    "hostel": {
        "name": "Hostel Management",
        "icon": "🏢",
        "fields": [
            {"id": "student", "label": "Student Name", "type": "text"},
            {"id": "room", "label": "Room Number Allocation", "type": "text"},
            {"id": "check_in", "label": "Check-in Date", "type": "date"}
        ],
        "has_expiry": False,
        "has_status": True,
        "status_options": ["Active Resident", "Checked Out"]
    },
    "coaching": {
        "name": "Coaching Center",
        "icon": "🎓",
        "fields": [
            {"id": "student", "label": "Student Name", "type": "text"},
            {"id": "subject", "label": "Batch / Subject", "type": "text"},
            {"id": "enroll_date", "label": "Enrollment Date", "type": "date"}
        ],
        "has_expiry": False,
        "has_status": True,
        "status_options": ["Fee Paid", "Fee Pending"]
    }
}

# ==========================================
# FILE IO LOGIC
# ==========================================
def load_data():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, 'r') as file: return json.load(file)
    except: return []

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# ==========================================
# MULTI-PURPOSE ROUTING
# ==========================================
@app.route('/')
def module_selector():
    return render_template('selector.html', modules=MODULES)

@app.route('/<module_id>')
def dashboard(module_id):
    if module_id not in MODULES: return redirect(url_for('module_selector'))
    mod = MODULES[module_id]
    
    data = load_data()
    records = [r for r in data if r.get('module') == module_id]
    
    stats = {'total': len(records), 'active': 0, 'expired': 0, 'unpaid': 0, 'alerts': []}
    today = datetime.now().date()
    
    for r in records:
        # Generic status tracking logic mapping to negative sounding statuses
        if mod['has_status'] and r.get('status', '').lower() in ['unpaid', 'borrowed', 'fee pending']:
            stats['unpaid'] += 1
            
        if mod['has_expiry'] and 'expiry_date' in r:
            try:
                exp_date = datetime.strptime(r['expiry_date'], "%Y-%m-%d").date()
                diff = (exp_date - today).days
                if diff < 0:
                    stats['expired'] += 1
                    stats['alerts'].append(f"OVERDUE: '{r.get('name') or r.get('book_title')}' [{r['id']}] expired {abs(diff)} days ago!")
                else:
                    stats['active'] += 1
                    if diff <= 7:
                        stats['alerts'].append(f"WARNING: '{r.get('name') or r.get('book_title')}' [{r['id']}] expires in {diff} days.")
            except: pass
                
    return render_template('index.html', module_id=module_id, module=mod, stats=stats)


@app.route('/<module_id>/add', methods=['GET', 'POST'])
def add_record(module_id):
    if module_id not in MODULES: return redirect(url_for('module_selector'))
    mod = MODULES[module_id]
    
    if request.method == 'POST':
        form_data = request.form
        record = {
            "id": f"{module_id[:3].upper()}-{str(uuid.uuid4())[:6].upper()}",
            "module": module_id
        }
        
        # Iteratively assemble dictionary schema!
        for field in mod['fields']:
            record[field['id']] = form_data.get(field['id'], '').strip()
            
        if mod['has_status']:
            record['status'] = form_data.get('status', '').strip()
            
        if mod['has_expiry']:
            try:
                base_date = datetime.strptime(record[mod['date_field']], "%Y-%m-%d").date()
                if mod['duration_field']:
                    expiry = base_date + timedelta(days=int(record[mod['duration_field']]))
                else:
                    expiry = base_date
                record['expiry_date'] = str(expiry)
            except Exception as e:
                flash("Error: Number/Date calculation failed.", "error")
                return redirect(url_for('add_record', module_id=module_id))
                
        data = load_data()
        data.append(record)
        save_data(data)
        flash("Record injected natively into database!", "success")
        return redirect(url_for('view_records', module_id=module_id))
        
    return render_template('add.html', module_id=module_id, module=mod)


@app.route('/<module_id>/view')
def view_records(module_id):
    if module_id not in MODULES: return redirect(url_for('module_selector'))
    mod = MODULES[module_id]
    query = request.args.get('q', '').strip().lower()
    
    data = load_data()
    records = [r for r in data if r.get('module') == module_id]
    
    if query:
        # Deep fuzzy search scanning entirely across sub-values dynamically
        records = [r for r in records if any(query in str(v).lower() for v in r.values())]
        
    return render_template('view.html', module_id=module_id, module=mod, records=records, query=query)


@app.route('/<module_id>/update/<record_id>', methods=['GET', 'POST'])
def update_record(module_id, record_id):
    mod = MODULES[module_id]
    data = load_data()
    record = next((r for r in data if r['id'] == record_id and r.get('module') == module_id), None)
    
    if not record:
        flash("Target pointer missing from index", "error")
        return redirect(url_for('view_records', module_id=module_id))
        
    if request.method == 'POST':
        form_data = request.form
        for field in mod['fields']:
            record[field['id']] = form_data.get(field['id'], '').strip()
            
        if mod['has_status']:
            record['status'] = form_data.get('status', '').strip()
            
        if mod['has_expiry']:
            try:
                base = datetime.strptime(record[mod['date_field']], "%Y-%m-%d").date()
                if mod['duration_field']:
                    record['expiry_date'] = str(base + timedelta(days=int(record[mod['duration_field']])))
                else:
                    record['expiry_date'] = str(base)
            except: pass
                
        save_data(data)
        flash("Payload successfully patched inside JSON", "success")
        return redirect(url_for('view_records', module_id=module_id))
        
    return render_template('update.html', module_id=module_id, module=mod, record=record)


@app.route('/<module_id>/delete/<record_id>')
def delete_record(module_id, record_id):
    data = load_data()
    post_del = [r for r in data if r['id'] != record_id]
    
    if len(data) == len(post_del):
        flash("Record not located for deletion.", "error")
    else:
        save_data(post_del)
        flash("Record physically expunged.", "success")
        
    return redirect(url_for('view_records', module_id=module_id))


@app.route('/<module_id>/export')
def export_csv(module_id):
    data = [r for r in load_data() if r.get('module') == module_id]
    if not data:
        flash("No active records mapped to module to export.", "error")
        return redirect(url_for('dashboard', module_id=module_id))
        
    filename = f"{module_id}_systems_export.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
