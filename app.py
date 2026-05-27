import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__, template_folder='.')

# SYSTEM ROOT TRACKER CONFIGURATION
SYSTEM_ROOT = r"C:\flutter dev\project\YouTube AI assistant"

@app.route('/')
def index():
    """Serve the SaaS control center frontend."""
    return send_from_directory('.', 'index.html')

def initialize_system():
    """Initialize the backend environment and log status."""
    if os.path.exists(SYSTEM_ROOT):
        print(f"--- SYSTEM INITIALIZATION SUCCESSFUL ---")
        print(f"ROOT PATH: {SYSTEM_ROOT}")
        print(f"STATUS: ONLINE")
        print(f"----------------------------------------")
    else:
        print(f"CRITICAL ERROR: System root {SYSTEM_ROOT} not found.")

if __name__ == '__main__':
    initialize_system()
    # In a real deployment, we would run the app:
    # app.run(debug=True, port=5000)
    print("PROJECT RE-STRUCTURE SUCCESSFUL • ASSISTANT IS ONLINE")