from flask import Flask, jsonify, render_template_string, request
from itertools import islice
import pandas as pd
from youtube_comment_downloader import *
from datetime import datetime
import os
from google.cloud import storage
import io

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
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"youtube_comments_{timestamp}.xlsx"
        
        # 创建一个字节流
        output = io.BytesIO()
        
        # 将DataFrame写入字节流
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        # 重置流的位置到开始
        output.seek(0)
        
        # 初始化Google Cloud Storage客户端
        storage_client = storage.Client()
        
        # 获取你的存储桶（请替换为你的存储桶名称）
        bucket = storage_client.bucket('yt-comments-bucket')
        
        # 创建一个新的blob并上传文件
        blob = bucket.blob(filename)
        blob.upload_from_file(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        # 生成文件的公共URL（可选，取决于你的存储桶权限）
        file_url = blob.public_url
        
        return jsonify({"message": "file saved", "filename": filename, "url": file_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/_ah/health')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
