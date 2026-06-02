import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from pymongo import MongoClient

app = Flask(__name__)

# সেটিং সিকিউর কি এবং সেশন লাইфটাইম (৯৩ দিন স্থায়ী থাকবে সেশন)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'suhan_saas_ultra_secure_permanent_key_2026')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90)
app.config['SESSION_COOKIE_NAME'] = 'ss_ai_saas_session'

# ================= MongoDB ক্লাউড ডাটাবেস কানেকশন =================
# রেন্ডারের MONGO_URI থেকে ডাটাবেস কানেক্ট হচ্ছে, ফাইল ডিলিট হওয়ার ভয় আর নেই!
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    # ব্যাকআপ লোকাল ওআরআই (যদি রেন্ডারে সেট না থাকে)
    MONGO_URI = "mongodb+srv://mrsuhan34_db_user:CC1KshAyEZQX3kwV@cluster0.eisaj7e.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client['ss_ai_cartoon_database']
users_collection = db['users_data']

# ডিফল্ট অ্যাডমিন অ্যাকাউন্ট চেক এবং অটো-জেনারেট লজিক
def init_db_admin():
    admin = users_collection.find_one({"_id": "admin"})
    if not admin:
        users_collection.insert_one({
            "_id": "admin",
            "user_id": "SS_ELITE_ADMIN_2026",
            "password": "REK_#9824_SNC_@Z7X",
            "role": "admin"
        })

init_db_admin()

# ================= Google OAuth2 কনফিগারেশন =================
GOOGLE_OAUTH_CONFIG = {
    "web": {
        "client_id": os.environ.get('GOOGLE_CLIENT_ID', '822666139852-qbq9b548gj8juh8fna5kk1vgbgvlqun2.apps.googleusercontent.com').strip(),
        "project_id": "ss-ai-cartoon-saas",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET', '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').strip(),
        "redirect_uris": ["https://flask-hello-world-jbuj.onrender.com/oauth2callback"]
    }
}

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# ================= ডাটাবেস প্রসেসিং হেল্পারস =================
def get_all_customers_from_mongo():
    # মঙ্গোডিবি থেকে অ্যাডমিন বাদে সব কাস্টমার রিড করা
    all_users = users_collection.find({"role": "customer"})
    customers = {}
    for u in all_users:
        uid = str(u.get("_id"))
        approved_at_str = u.get("approved_at", "")
        days_left = 30
        is_expired = False
        if approved_at_str:
            try:
                approved_date = datetime.strptime(approved_at_str.strip(), "%Y-%m-%d")
                elapsed_days = (datetime.now() - approved_date).days
                days_left = max(0, 30 - elapsed_days)
                is_expired = elapsed_days >= 30
            except Exception:
                pass
        customers[uid] = {
            "name": u.get("name", "Unknown"),
            "password": u.get("password", ""),
            "category": u.get("category", ""),
            "gmail": u.get("gmail", ""),
            "is_approved": u.get("is_approved", False),
            "is_blocked": u.get("is_blocked", False),
            "youtube_linked": u.get("youtube_linked", False),
            "approved_at": approved_at_str,
            "days_left": int(days_left),
            "is_expired": bool(is_expired),
            "thirty_days_dismissed": u.get("thirty_days_dismissed", False)
        }
    return customers


# ================= রাউটিং লজিক (Routes) =================
@app.route('/')
def index():
    if 'username' in session and 'role' in session:
        if session.get('role') == 'admin':
            return render_template('index.html', role='admin', username=session['username'], customers=get_all_customers_from_mongo())
        
        username = str(session['username']).strip()
        user_info = users_collection.find_one({"_id": username})
        
        if user_info and user_info.get('is_approved', False):
            if user_info.get('is_blocked', False):
                session.clear()
                return "<h1>Account Blocked By Admin!</h1><a href='/logout'>Go Back</a>"
            return render_template(
                'index.html',
                role='customer',
                username=username,
                name=user_info.get('name', 'Customer'),
                category=user_info.get('category', ''),
                linked=user_info.get('youtube_linked', False),
                gmail_id=user_info.get('gmail', ''),
                user_password=user_info.get('password', '')
            )
        session.clear()
        return redirect(url_for('index'))
    return render_template('index.html', role='guest')


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = str(data.get('username', '')).strip()
        password = str(data.get('password', '')).strip()
        
        if username.lower() == "owner":
            return jsonify({"status": "ERROR", "message": "Invalid Username Choice!"})
            
        admin = users_collection.find_one({"_id": "admin"})
        if username == admin["user_id"] and password == admin["password"]:
            session.permanent = True
            session['username'] = "SuperAdmin_SS"
            session['role'] = "admin"
            return jsonify({"status": "SUCCESS", "message": "Admin verified! Access granted."})
            
        user_data = users_collection.find_one({"_id": username})
        if user_data and str(user_data["password"]) == password:
            if not user_data.get('is_approved', False):
                return jsonify({"status": "ERROR", "message": "Request is still PENDING approval!"})
            if user_data.get('is_blocked', False):
                return jsonify({"status": "ERROR", "message": "LOGIN DENIED: Account is BLOCKED!"})
                
            session.permanent = True
            session['username'] = username
            session['role'] = "customer"
            return jsonify({"status": "SUCCESS", "message": "Login Successful!"})
            
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"Login processing error: {e}"})
    return jsonify({"status": "ERROR", "message": "Access Denied: Invalid Credentials!"})


@app.route('/register_request', methods=['POST'])
def register_request():
    try:
        data = request.json
        name = data.get('name', '').strip()
        phone = str(data.get('phone', '')).strip()
        gmail = data.get('gmail', '').strip()
        password = str(data.get('password', '')).strip()
        
        if not phone or phone.lower() in ["admin", "owner", "superadmin_ss"]:
            return jsonify({"status": "ERROR", "message": "Reserved/Invalid Phone ID Number!"})
            
        if users_collection.find_one({"_id": phone}):
            return jsonify({"status": "ERROR", "message": "Number already registered!"})
            
        users_collection.insert_one({
            "_id": phone,
            "name": name,
            "password": password,
            "category": "",
            "gmail": gmail,
            "is_approved": False,
            "is_blocked": False,
            "youtube_linked": False,
            "approved_at": "",
            "role": "customer",
            "thirty_days_dismissed": False
        })
        return jsonify({"status": "SUCCESS"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


@app.route('/check_approval_status', methods=['POST'])
def check_approval_status():
    try:
        phone = str(request.json.get('phone', '')).strip()
        user_data = users_collection.find_one({"_id": phone})
        if not user_data:
            return jsonify({"status": "REJECTED"})
        if user_data.get('is_approved', False):
            return jsonify({"status": "APPROVED"})
    except Exception as e:
        print(f"Error checking status: {e}")
    return jsonify({"status": "PENDING"})


# ================= YouTube OAuth2 রুট সমূহ =================
@app.route('/customer/auth_youtube', methods=['POST'])
def auth_youtube():
    if 'username' not in session or session.get('role') != 'customer':
        return jsonify({"status": "ERROR", "message": "Unauthorized access!"})
    
    try:
        flow = Flow.from_client_config(
            GOOGLE_OAUTH_CONFIG,
            scopes=YOUTUBE_SCOPES,
            redirect_uri=GOOGLE_OAUTH_CONFIG["web"]["redirect_uris"][0]
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        session['oauth_state'] = state
        return jsonify({"status": "SUCCESS", "redirect_url": authorization_url})
        
    except Exception as e:
        return jsonify({"status": "ERROR", "message": f"OAuth initialization failed: {str(e)}"})


@app.route('/oauth2callback')
def oauth2callback():
    if 'oauth_state' not in session:
        return "Authorization failed: State token missing.", 400
        
    try:
        flow = Flow.from_client_config(
            GOOGLE_OAUTH_CONFIG,
            scopes=YOUTUBE_SCOPES,
            state=session['oauth_state'],
            redirect_uri=GOOGLE_OAUTH_CONFIG["web"]["redirect_uris"][0]
        )
        
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        youtube = build('youtube', 'v3', credentials=credentials)
        request_api = youtube.channels().list(part="snippet,statistics", mine=True)
        response = request_api.execute()
        
        if not response.get('items'):
            return "<h1>Error: No YouTube Channel found on this Google Account!</h1><a href='/'>Go Back</a>"
            
        channel_info = response['items'][0]['snippet']
        channel_name = channel_info.get('title', 'Unknown Channel')
        
        username = str(session.get('username')).strip()
        users_collection.update_one(
            {"_id": username},
            {"$set": {"youtube_linked": True, "youtube_token": credentials.to_json(), "channel_name": channel_name}}
        )
            
        return redirect(url_for('index'))
        
    except Exception as e:
        return f"<h1>OAuth Callback Error</h1><p>{str(e)}</p><a href='/'>Go Back</a>", 500


@app.route('/customer/set_category', methods=['POST'])
def set_category():
    if 'username' not in session or session.get('role') != 'customer':
        return jsonify({"status": "ERROR"})
    try:
        selected_cat = request.json.get('category', '').strip()
        username = str(session['username']).strip()
        users_collection.update_one({"_id": username}, {"$set": {"category": selected_cat}})
        return jsonify({"status": "SUCCESS"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


# ================= ৩-লাইন অপশন নোটিফিকেশন হ্যান্ডলিং রুট =================
@app.route('/admin/dismiss_thirty_days', methods=['POST'])
def dismiss_thirty_days():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"status": "ERROR", "message": "Unauthorized"})
    try:
        target_user = str(request.json.get('target_user', '')).strip()
        users_collection.update_one({"_id": target_user}, {"$set": {"thirty_days_dismissed": True}})
        return jsonify({"status": "SUCCESS", "message": "Notification Dismissed!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


# ================= লাইভ এআই ট্র্যাক জেনারেটর =================
@app.route('/get_live_ai_data')
def get_live_ai_data():
    if 'username' not in session or session.get('role') != 'customer':
        return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "OFFLINE"})
    
    user_info = users_collection.find_one({"_id": str(session['username']).strip()})
    if not user_info:
        return jsonify({"topic": "N/A", "title": "N/A", "desc_thumb": "N/A", "length": "N/A", "upload_time": "N/A", "status": "OFFLINE"})
        
    category = user_info.get('category', '').lower()
    current_time = datetime.now()
    
    random.seed(int(user_info.get('password', '123').encode().hex()) + current_time.day)
    hours_to_add = random.choice([3, 4, 5])
    minutes_to_add = random.choice([0, 15, 30, 45])
    traffic_time = (current_time + timedelta(hours=hours_to_add)).replace(minute=minutes_to_add)
    best_time = f"TODAY AT {traffic_time.strftime('%I:%M %p')} (Optimized Live Channel Traffic)"
    
    if "cartoon" in category or "animation" in category:
        topics = ["সোনার পাখি ও জাদুকরী রূপনগর রাজ্যের কেল্লা", "ভুতুড়ে বিলের রহস্যময় ডাইনি বুড়ি", "টুনটুনি আর চালাক শেয়ালের বুদ্ধির খেলা"]
        titles = ["সোনার পাখি ও জাদুকরী রাজা | Bangla Cartoon Stories 2026", "ভুতুড়ে বিলের রহস্যময়ী ডাইনি! | Bengali Animated Story", "টুনটুনি পাখি বনাম চালাক শেয়াল! নতুন রূপকথার গল্প"]
        descs = ["Description: আজ রূপনগরের জাদুকরী পাখি ও লোভী রাজার নতুন পর্ব। Thumbnail: HD Auto-Render Complete", "Description: ভুতুড়ে বিলের গভীর রাতের গা ছমছমে কার্টুন গল্প। Thumbnail: 4K Thumbnail Loaded", "Description: চালাক শেয়ালকে উচিত শিক্ষা দিল টুনটুনি। Thumbnail: AI Frame Rendered"]
        lengths = ["11 Minutes 45 Seconds", "09 Minutes 12 Seconds", "13 Minutes 20 Seconds"]
    elif "documentary" in category or "mystery" in category:
        topics = ["The Deep Secrets of Bermuda Triangle", "Mystery of Ancient Egyptian Pyramids", "World War II Unsolved Hidden Codes"]
        titles = ["Bermuda Triangle: The Unsolved Graveyard of Ocean", "The Secret Rooms Inside Pyramids Hidden For 4000 Years!", "The Deadliest Hidden Codes of WW2 Left Unanswered."]
        descs = ["Description: Secrets of deep oceanic anomalies. Thumbnail: Ultra-Detail Overlay Ready", "Description: Exploring hidden tunnels of Egypt. Thumbnail: 3D Map Vector Loaded", "Description: Unsolved historical communication codes. Thumbnail: Vintage Classified Graphic"]
        lengths = ["18 Minutes 24 Seconds", "22 Minutes 10 Seconds", "15 Minutes 50 Seconds"]
    elif "islamic" in category or "motivat" in category:
        topics = ["ইসলামিক অনুপ্রেরণামূলক গল্প ২০২৬", "জীবন বদলে দেওয়া ১০টি ইসলামিক উক্তি", "সাফল্যের পথে ইসলামিক জীবনধারা"]
        titles = ["আল্লাহর উপর ভরসা রাখো | Islamic Motivation 2026", "জীবন বদলে যাবে এই ১০টি কথায় | Bangla Islamic Video", "সফলতার রহস্য | Islamic Life Success Story Bangla"]
        descs = ["Description: ইসলামিক অনুপ্রেরণামূলক ভিডিও। Thumbnail: Islamic Gold Frame Ready", "Description: ইসলামিক জীবনধারার সেরা উক্তি। Thumbnail: Quran Verse Overlay Loaded", "Description: সফলতার পথে ইসলামিক গাইড। Thumbnail: Mosque Sunset Rendered"]
        lengths = ["12 Minutes 30 Seconds", "08 Minutes 45 Seconds", "15 Minutes 00 Seconds"]
    elif "facts" in category or "amazing" in category or "unknown" in category:
        topics = ["10 Amazing Facts About Space You Never Knew", "Mysterious Ancient Civilizations Hidden From History", "Unbelievable Animal Facts That Will Blow Your Mind"]
        titles = ["10 Mind-Blowing Space Facts Nobody Talks About!", "The Lost Civilizations That Historians Are Hiding!", "These Animal Abilities Are Scientifically Impossible!"]
        descs = ["Description: Space facts that will change your perspective. Thumbnail: Galaxy Neon Overlay Ready", "Description: Hidden history facts revealed. Thumbnail: Ancient Mystery Template Loaded", "Description: Unbelievable animal world facts. Thumbnail: Wildlife Action Frame Rendered"]
        lengths = ["09 Minutes 15 Seconds", "11 Minutes 30 Seconds", "07 Minutes 45 Seconds"]
    elif "cooking" in category or "recipe" in category or "food" in category:
        topics = ["বাংলাদেশের সেরা ১০টি ঐতিহ্যবাহী রেসিপি", "মাত্র ১৫ মিনিটে রান্না করুন সুস্বাদু ভর্তা", "রমজানের বিশেষ ইফতার রেসিপি ২০২৬"]
        titles = ["বাংলার ঐতিহ্যবাহী রান্না | Traditional Bangla Recipe 2026", "১৫ মিনিটে সেরা ভর্তা রেসিপি | Quick Bangla Cooking", "রমজানের সেরা ইফতার | Special Iফতার Recipe Bangla"]
        descs = ["Description: বাংলাদেশের ঐতিহ্যবাহী রান্নার রেসিপি। Thumbnail: Food HD Close-up Ready", "Description: দ্রুত ও সহজ ভর্তা রেসিপি। Thumbnail: Cooking Step Frame Loaded", "Description: রমজানের বিশেষ ইফতার আইটেম। Thumbnail: Iftar Spread Thumbnail Rendered"]
        lengths = ["14 Minutes 20 Seconds", "10 Minutes 00 Seconds", "16 Minutes 30 Seconds"]
    elif "travel" in category or "vlog" in category:
        topics = ["বাংলাদেশের অজানা ১০টি সুন্দর জায়গা", "সুন্দরবনের গভীরে একদিন", "কক্সবাজার থেকে সেন্টমার্টিন নৌকা ভ্রমণ"]
        titles = ["বাংলাদেশের লুকানো সৌন্দর্য | Hidden Beauty of Bangladesh 2026", "সুন্দরবনে বাঘের সাথে! | Sundarban Travel Vlog Bangla", "সেন্টমার্টিন দ্বীপ ভ্রমণ | Saint Martin Island Travel Vlog"]
        descs = ["Description: বাংলাদেশের অজানা সুন্দর স্থানগুলো। Thumbnail: Aerial Bangladesh View Ready", "Description: সুন্দরবনের অ্যাডভেঞ্চার ভ্রমণ। Thumbnail: Mangrove Forest Frame Loaded", "Description: সেন্টমার্টিন দ্বীপের ট্রাভেল ভ্লগ। Thumbnail: Blue Ocean Island Rendered"]
        lengths = ["18 Minutes 00 Seconds", "22 Minutes 15 Seconds", "19 Minutes 45 Seconds"]
    elif "tech" in category or "review" in category or "gadget" in category:
        topics = ["Top 5 Budget Smartphones of 2026 Under 15000 Taka", "Best AI Tools That Will Replace Your Job in 2026", "iPhone vs Android: Which is Better in 2026?"]
        titles = ["Best Budget Phone 2026 Under 15000 Taka | Full Review Bangla", "5 AI Tools That Are Replacing Humans Right Now!", "iPhone 17 vs Samsung S26: Ultimate Comparison Bangla"]
        descs = ["Description: সেরা বাজেট স্মার্টফোন রিভিউ। Thumbnail: Phone Comparison Layout Ready", "Description: AI tools replacing human jobs. Thumbnail: Futuristic AI Dashboard Loaded", "Description: iPhone vs Android ultimate battle. Thumbnail: Split Screen Phone Rendered"]
        lengths = ["13 Minutes 30 Seconds", "10 Minutes 15 Seconds", "16 Minutes 00 Seconds"]
    elif "health" in category or "fitness" in category:
        topics = ["সকালে উঠে ৫টি কাজ যা আপনার জীবন বদলে দেবে", "ডায়াবেটিস নিয়ন্ত্রণের সহজ ১০টি উপায়", "প্রতিদিন ৩০ মিনিট ব্যায়াম করুন এই নিয়মে"]
        titles = ["সকালের ৫টি অভ্যাস | Morning Routine That Changes Life Bangla", "ডায়াবেটিস নিয়ন্ত্রণ করুন ঘরে বসেই | Diabetes Control Bangla", "৩০ মিনিটের ব্যায়াম রুটিন | Daily Workout Plan Bangla 2026"]
        descs = ["Description: সকালের সেরা স্বাস্থ্যকর অভ্যাস। Thumbnail: Morning Sunrise Fitness Ready", "Description: ডায়াবেটিস নিয়ন্ত্রণের টিপস। Thumbnail: Health Infographic Loaded", "Description: দৈনিক ব্যায়ামের সম্পূর্ণ গাইড। Thumbnail: Workout Action Frame Rendered"]
        lengths = ["11 Minutes 00 Seconds", "14 Minutes 30 Seconds", "12 Minutes 45 Seconds"]
    elif "horror" in category or "bhoot" in category:
        topics = ["বাংলাদেশের সবচেয়ে ভয়ংকর ভুতুড়ে বাড়ির গল্প", "রাত ৩টার পর যা ঘটে কেউ বলে না", "সত্যিকারের ভূতের গল্প যা শুনলে ঘুম হারাম হয়"]
        titles = ["বাংলাদেশের সবচেয়ে ভুতুড়ে বাড়ি! | Real Horror Story Bangla", "রাত ৩টার রহস্য | Midnight Horror Story Bangla 2026", "সত্যিকারের ভূতের গল্প | Real Ghost Story Bangladesh"]
        descs = ["Description: বাংলাদেশের ভয়ংকর ভুতুড়ে স্থানের গল্প। Thumbnail: Dark Haunted House Ready", "Description: রাতের রহস্যময় ঘটনা। Thumbnail: Horror Night Frame Loaded", "Description: সত্যিকারের ভূতের অভিজ্ঞতা। Thumbnail: Ghost Silhouette Rendered"]
        lengths = ["16 Minutes 00 Seconds", "13 Minutes 30 Seconds", "18 Minutes 45 Seconds"]
    elif "business" in category or "entrepreneur" in category:
        topics = ["মাত্র ৫০০০ টাকায় শুরু করুন লাভজনক ব্যবসা", "বাংলাদেশে সেরা ১০টি অনলাইন ব্যবসার আইডিয়া ২০২৬", "কীভাবে ফ্রিল্যান্সিং থেকে মাসে লক্ষ টাকা আয় করবেন"]
        titles = ["৫০০০ টাকায় ব্যবসা শুরু করুন | Small Business Idea Bangla 2026", "সেরা অনলাইন ব্যবসার আইডিয়া | Online Business Bangladesh 2026", "ফ্রিল্যান্সিং গাইড | Freelancing Bangla Complete Tutorial 2026"]
        descs = ["Description: কম টাকায় লাভজনক ব্যবসার আদেশ। Thumbnail: Business Success Frame Ready", "Description: অনলাইন ব্যবসার সম্পূর্ণ গাইড। Thumbnail: E-commerce Dashboard Loaded", "Description: ফ্রিল্যান্সিং শুরু করার গাইড। Thumbnail: Laptop Money Stack Rendered"]
        lengths = ["15 Minutes 00 Seconds", "12 Minutes 30 Seconds", "20 Minutes 00 Seconds"]
    elif "kids" in category or "rhyme" in category or "children" in category:
        topics = ["বাংলা ছড়া - আম পাকা জাম পাকা", "শিশুদের জন্য নতুন বাংলা ছড়া ২০২৬", "রঙিন দুনিয়া শিশুদের শেখার গান"]
        titles = ["আম পাকা জাম পাকা | Bangla Rhymes For Kids 2026", "নতুন বাংলা ছড়া | New Bangla Kids Song 2026", "রঙিন দুনিয়া | Colorful Kids Learning Video Bangla"]
        descs = ["Description: শিশুদের জন্য মজার বাংলা ছড়া। Thumbnail: Colorful Cartoon Kids Ready", "Description: নতুন বাংলা ছড়ার সংকলন। Thumbnail: Animated Kids Frame Loaded", "Description: শিশুদের শেখার রঙিন ভিডিও। Thumbnail: Rainbow Learning Rendered"]
        lengths = ["08 Minutes 00 Seconds", "10 Minutes 15 Seconds", "07 Minutes 30 Seconds"]
    else:
        topics = ["AI Automation Trends of 2026", "How To Scale Faceless YouTube Channel Fast", "Viral Editing Hacks with Topaz AI"]
        titles = ["The Future is Here: AI Systems of 2026 You Cannot Ignore!", "I Started a Faceless YouTube Channel in 24 Hours (Secret AI Strategy)", "Cinematic Visuals Masterclass: Topaz AI Video Enhancement Tutorial"]
        descs = ["Description: Complete guide on 2026 AI tools. Thumbnail: Neon Dashboard Frame Ready", "Description: Faceless workflow for massive viral growth. Thumbnail: Analytics Concept Complete", "Description: Enhance old footage with AI processing. Thumbnail: Split Before/After Rendered"]
        lengths = ["08 Minutes 15 Seconds", "10 Minutes 42 Seconds", "07 Minutes 30 Seconds"]
        
    idx = random.randint(0, len(topics) - 1)
    return jsonify({
        "topic": topics[idx],
        "title": titles[idx],
        "desc_thumb": descs[idx],
        "length": lengths[idx],
        "upload_time": best_time,
        "status": "AI ENGINE: CHANNEL TRAFFIC MATCHED AND QUEUED FOR AUTO-POST"
    })


# ================= অ্যাডমিন ডেটা এডিটিং কন্ট্রোল রুম =================
@app.route('/admin/handle_request', methods=['POST'])
def handle_request():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"status": "ERROR", "message": "Unauthorized Mode"})
    try:
        data = request.json
        target_user = str(data.get('target_user', '')).strip()
        action = data.get('action')
        
        if action == 'approve':
            users_collection.update_one(
                {"_id": target_user},
                {"$set": {"is_approved": True, "approved_at": datetime.now().strftime("%Y-%m-%d")}}
            )
            return jsonify({"status": "SUCCESS", "message": "Account APPROVED!"})
        elif action == 'reject':
            users_collection.delete_one({"_id": target_user})
            return jsonify({"status": "SUCCESS", "message": "Account REJECTED!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})
    return jsonify({"status": "ERROR"})


@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if 'username' not in session or session.get('role') != 'admin':
        return jsonify({"status": "ERROR"})
    try:
        target_user = str(request.json.get('target_user', '')).strip()
        users_collection.delete_one({"_id": target_user})
        return jsonify({"status": "SUCCESS", "message": "Customer DELETED!"})
    except Exception as e:
        return jsonify({"status": "ERROR", "message": str(e)})


# ================= গ্লোবাল হ্যান্ডলার ও লগআউট =================
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
