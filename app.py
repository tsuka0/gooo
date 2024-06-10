from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from pytube import YouTube
import os
import re

app = Flask(__name__)
app.config['VIDEO_FOLDER'] = os.path.join(os.getcwd(), 'videos')

# 動画フォルダを確認・作成
if not os.path.exists(app.config['VIDEO_FOLDER']):
    try:
        os.makedirs(app.config['VIDEO_FOLDER'])
    except OSError as e:
        app.logger.error('Error creating directory: %s', e)
        raise

def sanitize_filename(filename):
    # ファイル名に使用できない文字を除去
    return re.sub(r'[\\/*?:"<>|]', "", filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').first()
        if video is None:
            raise Exception("MP4形式の動画が見つかりませんでした。")

        sanitized_title = sanitize_filename(yt.title)
        video_path = os.path.join(app.config['VIDEO_FOLDER'], f"{sanitized_title}.mp4")
        video.download(output_path=app.config['VIDEO_FOLDER'], filename=f"{sanitized_title}.mp4")
        return jsonify({'video_url': url_for('video', filename=f"{sanitized_title}.mp4")})
    except Exception as e:
        app.logger.error('Error downloading video: %s', e)
        return jsonify({'error': str(e)}), 500

@app.route('/videos/<filename>')
def video(filename):
    return send_from_directory(app.config['VIDEO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)