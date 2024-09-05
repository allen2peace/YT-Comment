from flask import Flask, jsonify, render_template_string, request
from itertools import islice
import pandas as pd
from youtube_comment_downloader import *
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <h1>Welcome to the YouTube Comment Downloader API</h1>
    <p> use /api/comments</p>
    """)

@app.route('/api/comments', methods=['GET'])
def get_comments():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Provide a YouTube video URL"}), 400

    print("video_url is ", video_url)
    downloader = YoutubeCommentDownloader()
    try:
        comments = downloader.get_comments_from_url(video_url, sort_by=SORT_BY_POPULAR)

        all_comments_dict = {
            'cid': [], 'text': [], 'time': [], 'author': [], 'channel': [],
            'votes': [], 'replies': [], 'photo': [], 'heart': [], 'reply': [], 'time_parsed': []
        }

        # 限制评论数量，例如只取前100条
        for comment in islice(comments, 100):
            for key in all_comments_dict.keys():
                all_comments_dict[key].append(comment[key])

        return jsonify(all_comments_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/commentsFile', methods=['GET'])
def comments_file():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Provide a YouTube video URL"}), 400

    print("video_url is ", video_url)
    downloader = YoutubeCommentDownloader()
    try:
        comments = downloader.get_comments_from_url(video_url, sort_by=SORT_BY_POPULAR)

        all_comments_dict = {
            'cid': [], 'text': [], 'time': [], 'author': [], 'channel': [],
            'votes': [], 'replies': [], 'photo': [], 'heart': [], 'reply': [], 'time_parsed': []
        }

        # 限制评论数量，例如只取前100条
        for comment in islice(comments, 100):
            for key in all_comments_dict.keys():
                all_comments_dict[key].append(comment[key])

        df = pd.DataFrame(all_comments_dict)
        
        # 生成带有时间戳和毫秒的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"youtube_comments_{timestamp}.xlsx"
        
        # 确保 'downloads' 文件夹存在
        os.makedirs('downloads', exist_ok=True)
        
        # 将文件保存在 'downloads' 文件夹中
        file_path = os.path.join('downloads', filename)
        df.to_excel(file_path, index=False)

        return jsonify({"message": "file saved", "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/_ah/health')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
