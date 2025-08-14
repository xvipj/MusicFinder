from flask import Flask, render_template, request, jsonify, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Opciones para búsqueda
SEARCH_OPTS = {
    'quiet': True,
    'skip_download': True,
    'format': 'bestaudio',
    'noplaylist': True,
    'extract_flat': False,
    'nocheckcertificate': True,  # 👈 Ignorar verificación SSL
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/115.0.0.0 Safari/537.36'
}

# Opciones para descarga FLAC
YDL_OPTS_DOWNLOAD = {
    'format': 'bestaudio/best',
    'nocheckcertificate': True,  # 👈 Ignorar verificación SSL
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'flac',
        'preferredquality': '0',
    }]
}

# Opciones para descarga MP3
YDL_OPTS_DOWNLOAD_MP3 = {
    'format': 'bestaudio/best',
    'nocheckcertificate': True,  # 👈 Ignorar verificación SSL
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para búsqueda
@app.route('/api/search')
def api_search():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "No query provided"}), 400

    max_results = 4
    results = []

    try:
        with YoutubeDL(SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            entries = info.get('entries', []) if info else []

            for e in entries:
                results.append({
                    'id': e.get('id'),
                    'title': e.get('title'),
                    'duration': e.get('duration'),
                    'thumbnail': e.get('thumbnail'),
                    'audio_url': e.get('url')
                })

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

    return jsonify(results)

# Descargar FLAC
@app.route('/download/<video_id>')
def download(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(YDL_OPTS_DOWNLOAD) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.flac'
    return send_file(filename, as_attachment=True)

# Descargar MP3
@app.route('/download-mp3/<video_id>')
def download_mp3(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(YDL_OPTS_DOWNLOAD_MP3) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
