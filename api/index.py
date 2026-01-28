from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Alpha Zen API is Online!"

@app.route('/api/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Search query is missing"}), 400

    # yt-dlp की सेटिंग्स - इसे सुपर फ़ास्ट बनाने के लिए
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # सिर्फ टॉप 5 रिजल्ट्स सर्च करेगा
            search_query = f"ytsearch5:{query}"
            info = ydl.extract_info(search_query, download=False)
            
            results = []
            if 'entries' in info:
                for entry in info['entries']:
                    results.append({
                        "id": entry.get('id'),
                        "title": entry.get('title'),
                        "thumbnail": f"https://img.youtube.com/vi/{entry.get('id')}/hqdefault.jpg",
                        "channel": entry.get('uploader', 'Unknown')
                    })
            
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel के लिए ज़रूरी
def handler(event, context):
    return app(event, context)

