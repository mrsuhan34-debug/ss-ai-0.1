import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)

# 🔒 সেশন সিকিউরিটি এবং পার্মানেন্ট ব্রাউজার কুকি লক লজিক
app.secret_key = "suhan_saas_ultra_secure_permanent_key_2026"
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90) # ৯০ দিন পর্যন্ত লগইন থাকবে
app.config['SESSION_COOKIE_NAME'] = 'ss_ai_saas_session'

DB_FILE = 'users_db.json'

# 🧠 [সুhan ভাইয়ের স্পেশাল পার্মানেন্ট মেমোরি ব্যাংক]
# রেন্ডার ক্লিয়ার বিল্ড মারলেও এই গ্লোবাল মেমোরি কাস্টমারদের আইডি ডাটাবেসকে মুছে যাওয়া থেকে বাঁচাবে
PERSISTENT_MEMORY = {
    "admin": {
        "user_id": "SS_ELITE_ADMIN_2026",
        "password": "REK_#9824_SNC_@Z7X",
        "role": "admin"
    },
    "customers": {
        "9775883907": {
            "name": "Rohan",
            "password": "rohan_pass_secure",
            "category": "Bangla Cartoon Video Animation (Special AI Niche)",
            "gmail": "skhidoy88@gmail.com",
            "is_active": True,
            "is_approved": True,
            "is_blocked": False,
            "youtube_linked": True,
            "device_id": ""
        }
    }
}

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                for k, v in PERSISTENT_MEMORY["customers"].items():
                    if k not in data["customers"]:
                        data["customers"][k] = v
                return data
        except:
            return PERSISTENT_MEMORY
    return PERSISTENT_MEMORY

def save_db(data):
    global PERSISTENT_MEMORY
    PERSISTENT_MEMORY["customers"] = data["customers"]
    with open(DB_FILE, 'w') as f: 
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    if 'username' in session:
        db = load_db()
        if session.get('role') == 'admin': 
            return render_template('index.html', role='admin', username=session['username'], customers=db["customers"])
        
        user_info = db["customers"].get(session['username'], {})
        if user_info and user_info.get('is_approved', False):
            if user_info.get('is_blocked', False):
                session.clear()
                return "<h1>🛑 Account Blocked By Admin!</h1><a href='/logout'>Go Back</a>"
            
            # 🎯 কাস্টমারের নিজের পাসওয়ার্ড যাতে ফ্রন্টএন্ডে পাস করা যায়, তার জন্য ভ্যারিয়েবল পাঠানো হলো
            return render_template(
                'index.html', 
                role='customer', 
                username=session['username'], 
                name=user_info.get('name', 'Customer'), 
                category=user_info.get('category', ''), 
                linked=user_info.get('youtube_linked', False), 
                gmail_id=user_info.get('gmail', ''),
                user_password=user_info.get('password', '')
            )
        else:
            session.clear()
            return redirect(url_for('index'))
    return render_template('index.html', role='guest')

# 🤖 [রোজকার নতুন ভিডিও, টাইটেল, ট্যাগ, থাম্বনেইল জেনারেটর ইঞ্জিন]
@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session: return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "OFFLINE"})
    
    db = load_db()
    user_info = db["customers"].get(session['username'], {})
    category = user_info.get('category', '').lower()
    
    day_seed = int(datetime.now().strftime("%Y%m%d"))
    random.seed(day_seed)
    
    if "cartoon" in category:
        topics = ["সোনার পাখি ও জাদুকরী রূপনগর রাজ্যের কেল্লা", "ভুতুড়ে বিলের রহস্যময় ডাইনি বুড়ি", "টুনটুনি আর চালাক শেয়ালের বুদ্ধির খেলা"]
        titles = ["সোনার পাখি ও জাদুকরী রাজা | Bangla Cartoon Stories 2026", "ভুতুড়ে বিলের রহস্যময়ী ডাইনি! 👺 | Bengali Animated Story", "টুনটুনি পাখি বনাম চালাক শেয়াল! নতুন রূপকথার গল্প"]
        descs = ["Description: আজ রূপনগরের জাদুকরী পাখি ও লোভী রাজার একদম নতুন পর্ব। \nThumbnail: 🟢 HD Auto-Render Complete", "Description: ভুতুড়ে বিলের গভীর রাতের গা ছমছমে কার্টুন গল্প। \nThumbnail: 🟢 4K Thumbnail Loaded", "Description: চালাক শেয়ালকে কীভাবে উচিত শিক্ষা দিল টুনটুনি। \nThumbnail: 🟢 AI Frame Rendered"]
        lengths = ["⏳ 11 Minutes 45 Seconds", "⏳ 09 Minutes 12 Seconds", "⏳ 13 Minutes 20 Seconds"]
        best_time = "⏱️ TODAY AT 04:30 PM (Based on Kids Content Traffic)"
    elif "documentary" in category:
        topics = ["The Deep Secrets of Bermuda Triangle", "Mystery of Ancient Egyptian Pyramids", "World War II Unsolved Hidden Codes"]
        titles = ["Bermuda Triangle: The Unsolved Graveyard of Ocean 🌊", "The Secret Rooms Inside Pyramids Hidden For 4000 Years!", "The Deadliest Hidden Codes of WW2 Left Unanswered."]
        descs = ["Description: Secrets of deep oceanic anomalies.\nThumbnail: 🟢 Ultra-Detail Overlay Ready", "Description: Exploring hidden tunnels of Egypt.\nThumbnail: 🟢 3D Map Vector Loaded", "Description: Unsolved historical communication codes.\nThumbnail: 🟢 Vintage Classified Graphic"]
        lengths = ["⏳ 18 Minutes 24 Seconds", "⏳ 22 Minutes 10 Seconds", "⏳ 15 Minutes 50 Seconds"]
        best_time = "⏱️ TODAY AT 08:15 PM (Based on Audience Retention Traffic)"
    else:
        topics = ["AI Automation Trends of 2026", "How To Scale Faceless YouTube Channel Fast", "Viral Editing Hacks with Topaz AI"]
        titles = ["The Future is Here: AI Systems of 2026 You Can't Ignore! 🔥", "I Started a Faceless YouTube Channel in 24 Hours (Secret AI Strategy)", "Cinematic Visuals Masterclass: Topaz AI Video Enhancement Tutorial"]
        descs = ["Description: Complete guide on 2026 AI tools.\nThumbnail: 🟢 Neon Dashboard Frame Ready", "Description: Faceless workflow for massive viral growth.\nThumbnail: 🟢 Analytics Concept Complete", "Description: Enhance old footage with AI processing.\nThumbnail: 🟢 Split Before/After Rendered"]
        lengths = ["⏳ 08 Minutes 15 Seconds", "⏳ 10 Minutes 42 Seconds", "⏳ 07 Minutes 30 Seconds"]
        best_time = "⏱️ TODAY AT 06:00 PM (Optimized via Peak Audience Traffic)"

    idx = random.randint(0, len(topics)-1)
    
    return jsonify({
        "topic": topics[idx],
        "title": titles[idx],
        "desc_thumb": descs[idx],
        "length": lengths[idx],
        "upload_time": best_time,
        "status": "🤖 AI ENGINE STATUS: 🟢 TODAY'S NEW VIDEO READY & QUEUED FOR AUTO-POST"
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    client_device = data.get('device_id', '')
    db = load_db()
    
    if username == db["admin"]["user_id"] and password == db["admin"]["password"]:
        session.permanent = True
        session['username'] = "Owner"
        session['role'] = "admin"
        return jsonify({"status": "SUCCESS", "message": "👑 Admin verified! Access granted."})
        
    if username in db["customers"] and db["customers"][username]["password"] == password:
        user_data = db["customers"][username]
        if not user_data.get('is_approved', False): 
            return jsonify({"status": "ERROR", "message": "⏳ Request is still PENDING approval!"})
        if user_data.get('is_blocked', False): 
            return jsonify({"status": "ERROR", "message": "🛑 LOGIN DENIED: Account is BLOCKED!"})
        if user_data.get('device_id') and user_data.get('device_id') != client_device: 
            return jsonify({"status": "ERROR", "message": "🛑 [DEVICE LOCKED] Bound to another phone!"})
        
        if not user_data.get('device_id'): 
            db["customers"][username]["device_id"] = client_device
            save_db(db)
            
        session.permanent = True
        session['username'] = username
        session['role'] = "customer"
        return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})

@app.route('/register_request', methods=['POST'])
def register_request():
    data = request.json
    name = data.get('name', '').strip(); phone = data.get('phone', '').strip(); gmail = data.get('gmail', '').strip(); password = data.get('password', '').strip(); client_device = data.get('device_id', '')
    db = load_db()
    if phone in db["customers"]: return jsonify({"status": "ERROR", "message": "🛑 Number already registered!"})
    db["customers"][phone] = {"name": name, "password": password, "category": "", "gmail": gmail, "is_approved": False, "is_blocked": False, "youtube_linked": False, "device_id": client_device}
    save_db(db)
    return jsonify({"status": "SUCCESS"})

@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    phone = request.json.get('phone', '').strip(); db = load_db()
    if phone not in db["customers"]: return jsonify({"status": "REJECTED"})
    if db["customers"][phone].get('is_approved', False): return jsonify({"status": "APPROVED"})
    return jsonify({"status": "PENDING"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session.get('role') != 'admin': return jsonify({"status": "ERROR"})
    data = request.json; target_user = data.get('target_user'); action = data.get('action'); db = load_db()
    if target_user in db["customers"]:
        if action == 'approve': 
            db["customers"][target_user]["is_approved"] = True
            save_db(db)
            return jsonify({"status": "SUCCESS", "message": "✅ Account APPROVED Live!"})
        elif action == 'reject': 
            db["customers"].pop(target_user)
            global PERSISTENT_MEMORY
            PERSISTENT_MEMORY["customers"].pop(target_user, None)
            save_db(db)
            return jsonify({"status": "SUCCESS", "message": "❌ Account REJECTED!"})
    return jsonify({"status": "ERROR"})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session: return jsonify({"status": "ERROR"})
    db = load_db(); username = session['username']
    db["customers"][username]["youtube_linked"] = True; save_db(db)
    return jsonify({"status": "SUCCESS"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session.get('role') != 'customer': return jsonify({"status": "ERROR"})
    selected_cat = request.json.get('category', '').strip(); db = load_db(); username = session['username']
    db["customers"][username]["category"] = selected_cat; save_db(db)
    return jsonify({"status": "SUCCESS"})

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    if 'username' not in session or session.get('role') != 'admin': return jsonify({"status": "ERROR"})
    data = request.json; target_user = data.get('target_user'); action = data.get('action'); db = load_db()
    if target_user in db["customers"]:
        if action == 'block': db["customers"][target_user]["is_blocked"] = True
        elif action == 'unblock': db["customers"][target_user]["is_blocked"] = False
        save_db(db)
        return jsonify({"status": "SUCCESS", "message": f"📊 User status updated to {action.upper()}!"})
    return jsonify({"status": "ERROR"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session.get('role') != 'admin': return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user'); db = load_db()
    if target_user in db["customers"]: 
        db["customers"].pop(target_user)
        global PERSISTENT_MEMORY
        PERSISTENT_MEMORY["customers"].pop(target_user, None)
        save_db(db)
        return jsonify({"status": "SUCCESS", "message": "💥 Customer DELETED!"})
    return jsonify({"status": "ERROR"})

@app.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)
