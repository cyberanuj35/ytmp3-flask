from flask import Flask, render_template_string, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Change this password for access
PASSWORD = "mypassword"

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader</title>
</head>
<body>
    {% if not logged_in %}
        <h2>Login</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter password" required>
            <input type="submit" value="Login">
        </form>
        {% if error %}
            <p style="color:red;">Incorrect password!</p>
        {% endif %}
    {% else %}
        <h2>YouTube to MP3/MP4</h2>
        <form action="/download" method="post">
            <input type="text" name="url" placeholder="Enter YouTube URL" required>
            <select name="format">
                <option value="mp3">MP3</option>
                <option value="mp4">MP4</option>
            </select>
            <input type="submit" value="Download">
        </form>
    {% endif %}
</body>
</html>
'''

# Store session temporarily (for this basic version)
session_logged_in = False

@app.route('/', methods=['GET', 'POST'])
def index():
    global session_logged_in
    error = False
    if request.method == 'POST':
        if request.form.get('password') == PASSWORD:
            session_logged_in = True
        else:
            error = True
    return render_template_string(HTML_TEMPLATE, logged_in=session_logged_in, error=error)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format_type = request.form['format']
    os.makedirs("downloads", exist_ok=True)
    outtmpl = "downloads/%(title)s.%(ext)s"

    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'bestaudio/best' if format_type == 'mp3' else 'bestvideo+bestaudio/best',
        'postprocessors': []
    }

    if format_type == 'mp3':
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if format_type == 'mp3':
            filename = filename.rsplit('.', 1)[0] + '.mp3'

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
