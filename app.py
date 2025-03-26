import os
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from yt_dlp import YoutubeDL
import threading
import time

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Carpeta de descargas
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def descargar_mp3(url, path):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'quiet': False,
            'nooverwrites': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            return os.path.basename(filename)
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            flash("Por favor, ingresa una URL.", "warning")
            return redirect(url_for('index'))
        
        if "youtube.com" not in url and "youtu.be" not in url:
            flash("Por favor, ingresa una URL válida de YouTube.", "warning")
            return redirect(url_for('index'))
        
        def download_task():
            filename = descargar_mp3(url, DOWNLOAD_FOLDER)
            if filename:
                with app.app_context():
                    flash(f"¡Descarga completada! <a href='/download/{filename}' class='download-link'>Descargar MP3</a>", "success")
            else:
                with app.app_context():
                    flash("Ocurrió un error durante la descarga.", "error")

        threading.Thread(target=download_task).start()
        return redirect(url_for('index'))
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)
    else:
        flash("El archivo no existe.", "error")
        return redirect(url_for('index'))

# Limpiar archivos antiguos
def clean_downloads():
    while True:
        for file in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, file)
            if os.path.isfile(file_path) and (time.time() - os.path.getmtime(file_path)) > 3600:
                os.remove(file_path)
        time.sleep(600)

threading.Thread(target=clean_downloads, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))