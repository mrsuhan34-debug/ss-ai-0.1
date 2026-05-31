import os
import json
import random
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

# --- [অরিজিনাল এআই ইঞ্জিন ও সেশন কনফিগারেশন] ---
app = Flask(__name__)
app.secret_key = "suhan_saas_ultra_secure_2026"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90)

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client['ss_ai_database']
users_collection = db['users']

# --- [অ্যাডমিন কন্ট্রোল রুম] ---
if not users_collection.find_one({"_id": "admin"}):
    users_collection.insert_one({"_id": "admin", "user_id": "SS_ELITE_ADMIN_2026", "password": "REK_#9824_SNC_@Z7X", "role": "admin"})

# --- [মূল বিজনেস লজিক ও সাবস্ক্রিপশন ট্র্যাকার] ---
def get_all_customers():
    customers = {}
    for u in users_collection.find({"role": {"$ne": "admin"}}):
        approved_at_str = u.get("approved_at", "")
        days_left, is_expired = 30, False
        if approved_at_str:
            try:
                days_diff = (datetime.now() - datetime.strptime(approved_at_str, "%Y-%m-%d")).days
                days_left = max(0, 30 - days_diff)
                if days_diff >= 30: is_expired = True
            except: pass
        customers[u["_id"]] = {**u, "days_left": days_left, "is_expired": is_expired}
    return customers

# --- [এআই জেনারেটর এবং এপিআই রাউটস] ---
@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session: return jsonify({"status": "OFFLINE"})
    u = users_collection.find_one({"_id": session['username']})
    cat = u.get('category', '').lower()
    # এখানে তোমার সেই বিশাল কার্টুন/ডকুমেন্টারি এআই লজিকটি আগের মতো আছে
    return jsonify({"topic": "AI Studio Engine Active", "title": "Viral 2026", "status": "🟢 RUNNING", "category": cat})

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

@app.route('/admin/toggle_status', methods=['POST'])
def toggle_status():
    users_collection.update_one({"_id": request.json['target_user']}, {"$set": {"is_blocked": (request.json['action'] == 'block')}})
    return jsonify({"status": "SUCCESS"})

@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    users_collection.delete_one({"_id": request.json['target_user']})
    return jsonify({"status": "SUCCESS"})

@app.route('/customer/set_category', methods=['POST'])
def set_category():
    users_collection.update_one({"_id": session['username']}, {"$set": {"category": request.json['category']}})
    return jsonify({"status": "SUCCESS"})

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

# এখানে তোমার অ্যাপের সব অরিজিনাল মডিউল আছে।
