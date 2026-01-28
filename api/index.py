from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

@app.route('/api/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query"}), 400

    # अगर क्वेरी में @ है, तो उसे चैनल के लाइव/वीडियो सेक्शन में ढूंढो
    if query.startswith('@'):
        handle = query.replace('@', '')
        # चैनल के लाइव और वीडियो दोनों को टारगेट करना
        search_target = f"https://www.youtube.com/@{handle}/streams"
    else:
        # नॉर्मल सर्च के लिए 10 रिजल्ट्स
        search_target = f"ytsearch10:{query}"

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'playlist_items': '1-10', # 10 रिजल्ट्स के लिए
        'ignoreerrors': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_target, download=False)
            results = []
            
            entries = info.get('entries', [])
            # अगर चैनल डायरेक्ट URL था तो info खुद एक लिस्ट हो सकती है
            if not entries and 'id' in info: 
                entries = [info]

            for entry in entries:
                if entry:
                    # लाइव वीडियो चेक करने का बेहतर तरीका
                    is_live = entry.get('is_live') or entry.get('live_status') == 'is_live'
                    results.append({
                        "id": entry.get('id'),
                        "title": entry.get('title'),
                        "is_live": is_live,
                        "thumbnail": f"https://img.youtube.com/vi/{entry.get('id')}/hqdefault.jpg"
                    })
            return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

