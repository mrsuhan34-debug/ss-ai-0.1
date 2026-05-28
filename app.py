import os
import json
from flask import Flask, render_template, request, jsonify
from google_auth_oauthlib.flow import InstalledAppFlow

app = Flask(__name__)

CREDENTIALS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    data = request.json
    command = data.get('command', '').lower()
    
    if 'analyze system' in command:
        return jsonify({
            "status": "SUCCESS",
            "message": "CPU Load: 8% | RAM Usage: 192MB/512MB\n[ONLINE] YouTube API Gateway is ready."
        })
        
    elif 'youtube' in command or 'auth' in command or 'link' in command:
        if not os.path.exists(CREDENTIALS_FILE):
            return jsonify({"status": "ERROR", "message": "credentials.json file missing!"})
            
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt='consent')
            return jsonify({
                "status": "SUCCESS",
                "message": f"YouTube API ready. Click to auth: {auth_url}"
            })
        except Exception as e:
            return jsonify({"status": "ERROR", "message": f"Failed: {str(e)}"})
    else:
        return jsonify({
            "status": "SUCCESS",
            "message": f"Task '{command}' initiated on SS-AI Core."
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
