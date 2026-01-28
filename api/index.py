from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"status": "Online", "message": "Alpha Zen API is Running!"})

@app.route('/api/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query"}), 400

    # Fast Logic: अगर हैंडल है तो सीधा चैनल के वीडियो सेक्शन को हिट करो
    if query.startswith('@'):
        handle = query.replace('@', '')
        search_target = f"https://www.youtube.com/@{handle}/videos"
    else:
        search_target = f"ytsearch10:{query}"

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # इसे True रखा है ताकि Vercel Timeout न हो (Fastest)
        'skip_download': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'playlist_items': '1-5', # सिर्फ टॉप 5 वीडियो
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_target, download=False)
            results = []
            seen_ids = set()
            
            entries = info.get('entries', [])
            if not entries and 'id' in info: entries = [info]

            for entry in entries:
                if not entry: continue
                
                v_id = entry.get('id')
                # Channel IDs (UC...) को साफ़ हटाना
                if not v_id or v_id.startswith('UC') or v_id in seen_ids: 
                    continue 

                seen_ids.add(v_id)
                
                # Live Status Detection (Flat extraction में limited होता है पर काम करेगा)
                status = entry.get('live_status')
                is_live = status == 'is_live' or entry.get('is_live') is True
                
                results.append({
                    "id": v_id,
                    "title": entry.get('title'),
                    "is_live": is_live,
                    "is_upcoming": status == 'is_upcoming',
                    "thumbnail": f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg"
                })
            
            # अगर चैनल सर्च था और कुछ नहीं मिला, तो एक बार नॉर्मल सर्च ट्राई कर लो
            if not results and query.startswith('@'):
                # Fallback to normal search
                return jsonify([{"id": "error", "title": "No videos found, try searching without @" }])

            # Sorting: Live सबसे ऊपर
            results.sort(key=lambda x: x['is_live'], reverse=True)
            
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
