import os
import json
import random
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "suhan_saas_ultra_secure_2026"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90)

# MongoDB Connection - SSL এরর এড়াতে TLS সেটিংস ঠিক করা হয়েছে
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(
    MONGO_URI, 
    tls=True, 
    tlsAllowInvalidCertificates=True, 
    serverSelectionTimeoutMS=5000
)
db = client['ss_ai_database']
users_collection = db['users']

# এরর হ্যান্ডলার
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

# অ্যাডমিন ইনিশিয়ালাইজেশন
if not users_collection.find_one({"_id": "admin"}):
    users_collection.insert_one({"_id": "admin", "user_id": "SS_ELITE_ADMIN_2026", "password": "REK_#9824_SNC_@Z7X", "role": "admin"})

# সাবস্ক্রিপশন ট্র্যাকার
def get_all_customers():
    customers = {}
    for u in users_collection.find({"role": {"$ne": "admin"}}):
        approved_at_str = u.get("approved_at", "")
        days_left = 30
        if approved_at_str:
            try:
                days_diff = (datetime.now() - datetime.strptime(approved_at_str, "%Y-%m-%d")).days
                days_left = max(0, 30 - days_diff)
            except: pass
        customers[u["_id"]] = {**u, "days_left": days_left}
    return customers

# রাউটস
@app.route('/')
def index():
    if 'username' in session:
        if session.get('role') == 'admin': return render_template('index.html', role='admin', customers=get_all_customers())
        u = users_collection.find_one({"_id": session['username']})
        if u and u.get('is_approved'): return render_template('index.html', role='customer', **u, username=u['_id'])
        session.clear()
    return render_template('index.html', role='guest')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    admin = users_collection.find_one({"_id": "admin"})
    if data['username'] == admin['user_id'] and data['password'] == admin['password']:
        session.update({'username': 'Owner', 'role': 'admin'})
        return jsonify({"status": "SUCCESS"})
    u = users_collection.find_one({"_id": data['username'], "password": data['password']})
    if u and u.get('is_approved') and not u.get('is_blocked'):
        session.update({'username': u['_id'], 'role': 'customer'})
        return jsonify({"status": "SUCCESS"})
    return jsonify({"status": "ERROR"})

@app.route('/register_request', methods=['POST'])
def register_request():
    data = request.json
    users_collection.insert_one({"_id": data['phone'], "name": data['name'], "password": data['password'], "gmail": data['gmail'], "is_approved": False, "role": "customer"})
    return jsonify({"status": "SUCCESS"})

@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    data = request.json
    if data['action'] == 'approve':
        users_collection.update_one({"_id": data['target_user']}, {"$set": {"is_approved": True, "approved_at": datetime.now().strftime("%Y-%m-%d")}})
    else: users_collection.delete_one({"_id": data['target_user']})
    return jsonify({"status": "SUCCESS"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    users_collection.delete_one({"_id": request.json['target_user']})
    return jsonify({"status": "SUCCESS"})

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))
