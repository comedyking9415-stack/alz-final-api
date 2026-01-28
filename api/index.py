from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/api/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query"}), 400

    if query.startswith('@'):
        handle = query.replace('@', '')
        search_target = f"https://www.youtube.com/@{handle}"
    else:
        search_target = f"ytsearch10:{query}"

    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'skip_download': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'playlist_items': '1-10',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_target, download=False)
            results = []
            seen_ids = set() # Improvement 1: Duplicate Filter
            
            entries = info.get('entries', [])
            if not entries and 'id' in info: entries = [info]

            for entry in entries:
                if not entry: continue
                
                v_id = entry.get('id')
                if not v_id or v_id.startswith('UC') or v_id in seen_ids: 
                    continue 

                seen_ids.add(v_id)
                status = entry.get('live_status')
                
                results.append({
                    "id": v_id,
                    "title": entry.get('title'),
                    "is_live": status == 'is_live',
                    "is_upcoming": status == 'is_upcoming',
                    "thumbnail": f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg"
                })
            
            # Improvement 2: Priority Sorting (Live > Upcoming > Normal)
            results.sort(key=lambda x: (x['is_live'], x['is_upcoming']), reverse=True)
            
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()

