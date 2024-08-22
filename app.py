from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
import mutagen
from mutagen.mp3 import MP3
import json
from datetime import datetime
import yt_dlp as youtube_dl
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  

class YouTubeURLForm(FlaskForm):
    url = StringField('YouTube URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Convert')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/youtube_to_mp3', methods=['GET', 'POST'])
def youtube_to_mp3():
    form = YouTubeURLForm()
    if form.validate_on_submit():
        url = form.url.data
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(app.config['UPLOAD_FOLDER'], '%(title)s.%(ext)s'),
                'verbose': True  
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                if info_dict:
                    filename = ydl.prepare_filename(info_dict)
                    ydl.download([url])
                    filename = os.path.splitext(filename)[0] + '.mp3'
                    
                    
                    metadata = extract_metadata(filename)
                    save_metadata(os.path.basename(filename), metadata)
                    
                    return jsonify({'success': 'Video converted and added to library', 'filename': os.path.basename(filename)})
                else:
                    return jsonify({'error': 'Could not extract video information'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return render_template('youtube_to_mp3.html', form=form)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        metadata = extract_metadata(file_path)
        save_metadata(filename, metadata)
        return jsonify({'success': 'File uploaded successfully', 'filename': filename, 'metadata': metadata}), 200
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        return jsonify({'success': 'File deleted successfully'}), 200
    return jsonify({'error': 'File not found'}), 404

@app.route('/music')
def get_music_files():
    music_files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            metadata = load_metadata(filename)
            if metadata:
                music_files.append({
                    'filename': filename,
                    'metadata': metadata
                })
    return jsonify(music_files)

@app.route('/edit/<filename>', methods=['POST'])
def edit_metadata(filename):
    data = request.json
    metadata = load_metadata(filename)
    if metadata:
        metadata.update(data)
        save_metadata(filename, metadata)
        return jsonify({'success': 'Metadata updated successfully', 'metadata': metadata}), 200
    return jsonify({'error': 'File not found'}), 404

def extract_metadata(file_path):
    try:
        audio = mutagen.File(file_path)
        if isinstance(audio, MP3):
            metadata = {
                'title': audio.get('TIT2', ['Unknown'])[0],
                'artist': audio.get('TPE1', ['Unknown'])[0],
                'album': audio.get('TALB', ['Unknown'])[0],
                'duration': str(int(audio.info.length)) + " seconds",
                'bitrate': f"{audio.info.bitrate / 1000:.0f} kbps",
                'sample_rate': f"{audio.info.sample_rate} Hz",
                'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            metadata = {
                'title': audio.get('title', ['Unknown'])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'duration': str(int(audio.info.length)) + " seconds",
                'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    except:
        metadata = {
            'title': 'Unknown',
            'artist': 'Unknown',
            'album': 'Unknown',
            'duration': 'Unknown',
            'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    return metadata

def save_metadata(filename, metadata):
    metadata_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)

def load_metadata(filename):
    metadata_file = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return None

@app.route('/stats')
def get_stats():
    total_files = 0
    total_duration = 0
    artists = set()
    albums = set()
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if allowed_file(filename):
            metadata = load_metadata(filename)
            if metadata:
                total_files += 1
                total_duration += int(metadata['duration'].split()[0])
                artists.add(metadata['artist'])
                albums.add(metadata['album'])
    
    return jsonify({
        'total_files': total_files,
        'total_duration': f"{total_duration // 60} minutes, {total_duration % 60} seconds",
        'unique_artists': len(artists),
        'unique_albums': len(albums)
    })

if __name__ == '__main__':
    app.run(debug=True)