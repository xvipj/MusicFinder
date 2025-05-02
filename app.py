from flask import Flask, render_template, request, jsonify, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

YDL_OPTS_SEARCH = {'quiet': True, 'skip_download': True}

# optiones para la descarga en flac 
YDL_OPTS_DOWNLOAD = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'flac',
        'preferredquality': '0',
    }]
}

# Configuración de la aplicación Flask
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la búsqueda de videos
@app.route('/api/search')
def api_search():
    query = request.args.get('query', '')
    max_results = 4
    results = []

    with YoutubeDL({'quiet': True, 'skip_download': True, 'format': 'bestaudio'}) as ydl:
        info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        entries = info.get('entries', [])
        for e in entries:
            audio_url = e['url']
            results.append({
                'id': e['id'],
                'title': e['title'],
                'duration': e.get('duration'),
                'thumbnail': e.get('thumbnail'),
                'audio_url': audio_url  # ✅ URL directa del audio
            })

    return jsonify(results)

# Ruta para la descarga musica
@app.route('/download/<video_id>')
def download(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(YDL_OPTS_DOWNLOAD) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.flac'
    return send_file(filename, as_attachment=True)

# opcion de descarga de videos en formato mp3
YDL_OPTS_DOWNLOAD_MP3 = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

# Ruta para la descarga de videos en formato mp3
@app.route('/download-mp3/<video_id>')
def download_mp3(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    with YoutubeDL(YDL_OPTS_DOWNLOAD_MP3) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)


