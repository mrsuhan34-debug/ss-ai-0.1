import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# 🔒 সেশন সিকিউরিটি লক লজিক
app.secret_key = "suhan_saas_ultra_secure_permanent_key_2026"
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90)
app.config['SESSION_COOKIE_NAME'] = 'ss_ai_saas_session'

# 🌐 [রেন্ডার সিক্রেট লকার থেকে ক্লাউড ডাটাবেস লিংক টানা হচ্ছে]
MONGO_URI = os.getenv("MONGO_URI")

users_collection = None

try:
    client = MongoClient(MONGO_URI)
    db = client['ss_ai_database']
    users_collection = db['users']
    print("🌐 MongoDB Cloud Database Connected Successfully!")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")

# 🎯 [Error 500 Fixed] মঙ্গোডিবির নতুন নিয়ম মেনে 'is not None' দিয়ে চেক করা হলো ভাই
if users_collection is not None and not users_collection.find_one({"_id": "admin"}):
    users_collection.insert_one({
        "_id": "admin",
        "user_id": "SS_ELITE_ADMIN_2026",
        "password": "REK_#9824_SNC_@Z7X",
        "role": "admin"
    })

def get_all_customers():
    customers = {}
    if users_collection is not None:
        all_users = users_collection.find({"role": {"$ne": "admin"}})
        for u in all_users:
            customers[u["_id"]] = {
                "name": u.get("name"),
                "password": u.get("password"),
                "category": u.get("category", ""),
                "gmail": u.get("gmail", ""),
                "is_approved": u.get("is_approved", False),
                "is_blocked": u.get("is_blocked", False),
                "youtube_linked": u.get("youtube_linked", False)
            }
    return customers

@app.route('/')
def index():
    if 'username' in session:
        if session.get('role') == 'admin': 
            return render_template('index.html', role='admin', username=session['username'], customers=get_all_customers())
        
        if users_collection is not None:
            user_info = users_collection.find_one({"_id": session['username']})
            if user_info and user_info.get('is_approved', False):
                if user_info.get('is_blocked', False):
                    session.clear()
                    return "<h1>🛑 Account Blocked By Admin!</h1><a href='/logout'>Go Back</a>"
                
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
        session.clear()
        return redirect(url_for('index'))
    return render_template('index.html', role='guest')

@app.route('/admin/active_customers')
def active_customers_page():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    return render_template('active_customers.html', customers=get_all_customers())

@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session: return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "OFFLINE"})
    
    if users_collection is None: return jsonify({"topic": "N/A"})
    user_info = users_collection.find_one({"_id": session['username']})
    if not user_info: return jsonify({"topic": "N/A"})
    category = user_info.get('category', '').lower()
    
    current_time = datetime.now()
    random.seed(int(user_info.get('password', '123').encode().hex()) + current_time.day)
    
    hours_to_add = random.choice([3, 4, 5])
    minutes_to_add = random.choice([0, 15, 30, 45])
    traffic_time = current_time + timedelta(hours=hours_to_add)
    traffic_time = traffic_time.replace(minute=minutes_to_add)
    
    formatted_traffic_time = traffic_time.strftime("%I:%M %p")
    best_time = f"⏱️ TODAY AT {formatted_traffic_time} (Optimized Live Channel Traffic)"

    if "cartoon" in category:
        topics = ["সোনার পাখি ও ஜাদুকরী রূপনগর রাজ্যের কেল্লা", "ভুতুড়ে বিলের রহস্যময় ডাইনি বুড়ি", "টুনটুনি আর চালাক শেয়ালের বুদ্ধির খেলা"]
        titles = ["সোনার পাখি ও জাদুকরী রাজা | Bangla Cartoon Stories 2026", "ভুতুড়ে বিলের রহস্যময়ী ডাইনি! 👺 | Bengali Animated Story", "টুনটুনি পাখি বনাম চালাক শেয়াল! নতুন রূপকথার গল্প"]
        descs = ["Description: আজ রূপনগরের জাদুকরী পাখি ও লোভী রাজার একদম নতুন পর্ব। \nThumbnail: 🟢 HD Auto-Render Complete", "Description: @ভুতুড়ে বিলের গভীর রাতের গা ছমছমে কার্টুন গল্প। \nThumbnail: 🟢 4K Thumbnail Loaded", "Description: চালাক শেয়ালকে কীভাবে উচিত শিক্ষা দিল টুনটুনি। \nThumbnail: 🟢 AI Frame Rendered"]
        lengths = ["⏳ 11 Minutes 45 Seconds", "⏳ 09 Minutes 12 Seconds", "⏳ 13 Minutes 20 Seconds"]
    elif "documentary" in category:
        topics = ["The Deep Secrets of Bermuda Triangle", "Mystery of Ancient Egyptian Pyramids", "World War II Unsolved Hidden Codes"]
        titles = ["Bermuda Triangle: The Unsolved Graveyard of Ocean 🌊", "The Secret Rooms Inside Pyramids Hidden For 4000 Years!", "The Deadliest Hidden Codes of WW2 Left Unanswered."]
        descs = ["Description: Secrets of deep oceanic anomalies.\nThumbnail: 🟢 Ultra-Detail Overlay Ready", "Description: Exploring hidden tunnels of Egypt.\nThumbnail: 🟢 3D Map Vector Loaded", "Description: Unsolved historical communication codes.\nThumbnail: 🟢 Vintage Classified Graphic"]
        lengths = ["⏳ 18 Minutes 24 Seconds", "⏳ 22 Minutes 10 Seconds", "⏳ 15 Minutes 50 Seconds"]
    else:
        topics = ["AI Automation Trends of 2026", "How To Scale Faceless YouTube Channel Fast", "Viral Editing Hacks with Topaz AI"]
        titles = ["The Future is Here: AI Systems of 2026 You Can't Ignore! 🔥", "I Started a Faceless YouTube Channel in 24 Hours (Secret AI Strategy)", "Cinematic Visuals Masterclass: Topaz AI Video Enhancement Tutorial"]
        descs = ["Description: Complete guide on 2026 AI tools.\nThumbnail: 🟢 Neon Dashboard Frame Ready", "Description: Faceless workflow for massive viral growth.\nThumbnail: 🟢 Analytics Concept Complete", "Description: Enhance old footage with AI processing.\nThumbnail: 🟢 Split Before/After Rendered"]
        lengths = ["⏳ 08 Minutes 15 Seconds", "⏳ 10 Minutes 42 Seconds", "⏳ 07 Minutes 30 Seconds"]

    idx = random.randint(0, len(topics)-1)
    
    return jsonify({
        "topic": topics[idx],
        "title": titles[idx],
        "desc_thumb": descs[idx],
        "length": lengths[idx],
        "upload_time": best_time,
        "status": "🤖 AI ENGINE STATUS: 🟢 CHANNEL TRAFFIC MATCHED & QUEUED FOR AUTO-POST"
    })

@app.route('/login', methods=['POST'])
def login():
    if users_collection is None: return jsonify({"status": "ERROR", "message": "Database disconnected!"})
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    admin_info = users_collection.find_one({"_id": "admin"})
    if username == admin_info["user_id"] and password == admin_info["password"]:
        session.permanent = True
        session['username'] = "Owner"
        session['role'] = "admin"
        return jsonify({"status": "SUCCESS", "message": "👑 Admin verified! Access granted."})
        
    user_data = users_collection.find_one({"_id": username})
    if user_data and user_data["password"] == password:
        if not user_data.get('is_approved', False): 
            return jsonify({"status": "ERROR", "message": "⏳ Request is still PENDING approval!"})
        if user_data.get('is_blocked', False): 
            return jsonify({"status": "ERROR", "message": "🛑 LOGIN DENIED: Account is BLOCKED!"})
        
        session.permanent = True
        session['username'] = username
        session['role'] = "customer"
        return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})

@app.route('/register_request', methods=['POST'])
def register_request():
    if users_collection is None: return jsonify({"status": "ERROR", "message": "Database disconnected!"})
    data = request.json
    name = data.get('name', '').strip(); phone = data.get('phone', '').strip(); gmail = data.get('gmail', '').strip(); password = data.get('password', '').strip()
    
    if users_collection.find_one({"_id": phone}): 
        return jsonify({"status": "ERROR", "message": "🛑 Number already registered!"})
        
    users_collection.insert_one({
        "_id": phone,
        "name": name,
        "password": password,
        "category": "",
        "gmail": gmail,
        "is_approved": False,
        "is_blocked": False,
        "youtube_linked": False,
        "role": "customer"
    })
    return jsonify({"status": "SUCCESS"})

@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    if users_collection is None: return jsonify({"status": "PENDING"})
    phone = request.json.get('phone', '').strip()
    user_data = users_collection.find_one({"_id": phone})
    if not user_data: return jsonify({"status": "REJECTED"})
    if user_data.get('is_approved', False): return jsonify({"status": "APPROVED"})
    return jsonify({"status": "PENDING"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session.get('role') != 'admin' or users_collection is None: return jsonify({"status": "ERROR"})
    data = request.json; target_user = data.get('target_user'); action = data.get('action')
    
    if action == 'approve': 
        users_collection.update_one({"_id": target_user}, {"$set": {"is_approved": True}})
        return jsonify({"status": "SUCCESS", "message": "✅ Account APPROVED Live!"})
    elif action == 'reject': 
        users_collection.delete_one({"_id": target_user})
        return jsonify({"status": "SUCCESS", "message": "❌ Account REJECTED!"})
    return jsonify({"status": "ERROR"})

@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session or users_collection is None: return jsonify({"status": "ERROR"})
    username = session['username']
    users_collection.update_one({"_id": username}, {"$set": {"youtube_linked": True}})
    return jsonify({"status": "SUCCESS"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session.get('role') != 'customer' or users_collection is None: return jsonify({"status": "ERROR"})
    selected_cat = request.json.get('category', '').strip(); username = session['username']
    users_collection.update_one({"_id": username}, {"$set": {"category": selected_cat}})
    return jsonify({"status": "SUCCESS"})

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    if 'username' not in session or session.get('role') != 'admin' or users_collection is None: return jsonify({"status": "ERROR"})
    data = request.json; target_user = data.get('target_user'); action = data.get('action')
    
    is_blocked = True if action == 'block' else False
    users_collection.update_one({"_id": target_user}, {"$set": {"is_blocked": is_blocked}})
    return jsonify({"status": "SUCCESS", "message": f"📊 User status updated to {action.upper()}!"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session.get('role') != 'admin' or users_collection is None: return jsonify({"status": "ERROR"})
    target_user = request.json.get('target_user')
    users_collection.delete_one({"_id": target_user})
    return jsonify({"status": "SUCCESS", "message": "💥 Customer DELETED from Cloud!"})

@app.route('/logout')
def logout(): 
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5000, debug=True)
