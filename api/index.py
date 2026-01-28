from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API is Live!"

@app.route('/api/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query"}), 400

    # इसे और भी हल्का और फ़ास्ट बनाया है
    ydl_opts = {
        'quiet': True,
        'extract_flat': 'in_playlist',
        'skip_download': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'playlist_items': '1,2,3,4,5'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            results = []
            if 'entries' in info:
                for entry in info['entries']:
                    if entry: # खाली डेटा न आए
                        results.append({
                            "id": entry.get('id'),
                            "title": entry.get('title'),
                            "thumbnail": f"https://img.youtube.com/vi/{entry.get('id')}/hqdefault.jpg"
                        })
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel के लिए
def handler(event, context):
    return app(event, context)
    
