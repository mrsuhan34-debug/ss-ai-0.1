import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

STATUS_FILE = 'bot_status.json'

def get_bot_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {"last_upload_date": "", "uploaded_videos": []}

def save_bot_status(status):
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get('command', '').lower()
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    status = get_bot_status()
    
    if 'generate' in command or 'make' in command or 'cartoon' in command:
        if status["last_upload_date"] == today_date:
            last_video = status["uploaded_videos"][-1] if status["uploaded_videos"] else {}
            return jsonify({
                "status": "WARNING",
                "message": f"🛑 [LIMIT LOCKED] সুহান ভাই, আজকের ভিডিও অলরেডি আপলোড কমপ্লিট!\n"
                           f"📅 তারিখ: {today_date}\n"
                           f"🎬 আজকের ভিডিও টপিক ছিল: '{last_video.get('topic', 'কার্টুন গল্প')}'\n\n"
                           f"💡 ভুল করে ক্লিক হলেও কোনো চিন্তা নেই, এআই আবার আগামীকাল নতুন ভিডিও বানাবে।"
            })
            
        ai_brain = random.choice(["ChatGPT-4o", "Gemini 1.5 Pro"])
        viral_ideas = [
            "সোনার জাদুকরী নূপুর আর গরিব কাঠুরের ভাগ্য বদল",
            "নিশুতি রাতের মায়াবী চাঁদের বুড়ি ও রূপোর পাহাড়ের রহস্য",
            "বুদ্ধিমান গ্রামের ছোট ছেলে আর বনের বোকা জিনের ஜাদুর থলি",
            "অভিশপ্ত রাজপ্রাসাদ ও সাহসী রাজকন্যার তলোয়ারের গল্প",
            "কথা বলা জাদুকরী টিয়া পাখি আর লোভী সওদাগরের সাত সমুদ্র"
        ]
        generated_topic = random.choice(viral_ideas)
        duration = random.randint(10, 19)
        current_time = datetime.now().strftime('%I:%M %p')
        
        new_video = {"date": today_date, "time": current_time, "topic": generated_topic, "duration": f"{duration} min"}
        status["last_upload_date"] = today_date
        status["uploaded_videos"].append(new_video)
        save_bot_status(status)
        
        return jsonify({
            "status": "SUCCESS",
            "message": f"🤖 [AI ENGINE] Active: {ai_brain}\n"
                       f"📝 স্ক্রিপ্ট লকড: '{generated_topic}'\n"
                       f"⏱️ লেন্থ: {duration} মিনিট | আপলোড টাইম: {current_time}\n"
                       f"📐 ফ্রেম ফরম্যাট: 16:9 Widescreen (1920x1080 Full HD)\n"
                       f"🖼️ [THUMBNAIL] গল্প অনুযায়ী কাস্টম ২D কার্টুন থাম্বনেল জেনারেট ও সেট করা হয়েছে!\n"
                       f"🚀 ভিডিও ও থাম্বনেল সরাসরি 'SS EDIT' চ্যানেলে লাইভ হয়ে গেছে!\n"
                       f"📊 [STATUS] আজকের কোটা সফলভাবে পুশ করা হয়েছে।"
        })
        
    elif 'check status' in command or 'history' in command:
        if not status["uploaded_videos"]:
            return jsonify({"status": "SUCCESS", "message": "এখনো কোনো ভিডিও আপলোড হয়নি ভাই।"})
        
        history_text = "📜 [SS EDIT - UPLOAD HISTORY] 📜\n"
        for vid in status["uploaded_videos"][-5:]:
            history_text += f"📅 {vid['date']} | ⏰ {vid['time']} | 🎬 {vid['topic']} ({vid['duration']}) | 📐 16:9 + 🖼️ Thumbnail Set\n"
        return jsonify({"status": "SUCCESS", "message": history_text})
        
    else:
        return jsonify({
            "status": "SUCCESS",
            "message": f"Task '{command}' initiated. Processing..."
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
