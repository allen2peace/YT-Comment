from flask import Flask, jsonify, render_template_string, request
from itertools import islice
import pandas as pd
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from datetime import datetime
import os
from google.cloud import storage
import io
import logging
import time

# 在文件开头设置日志级别
logging.basicConfig(level=logging.DEBUG)

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
    logging.debug(f"Received video URL: {video_url}")
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
        comment_count = 0
        for comment in islice(comments, 100):
            for key in all_comments_dict.keys():
                all_comments_dict[key].append(comment[key])
            comment_count += 1

        # 添加评论数量到返回的数据中
        response_data = {
            "comment_count": comment_count,
            "comments": all_comments_dict
        }

        return jsonify(response_data)
    except ValueError as ve:
        logging.error(f"Invalid URL: {str(ve)}")
        return jsonify({"error": f"Invalid URL: {str(ve)}"}), 400
    except Exception as e:
        logging.error(f"Error fetching comments: {str(e)}")
        return jsonify({"error": f"Error fetching comments: {str(e)}"}), 500

@app.route('/api/commentsFile', methods=['GET'])
def comments_file():
    video_url = request.args.get('url')
    logging.debug(f"Received video URL for file generation: {video_url}")
    if not video_url:
        return jsonify({"error": "Provide a YouTube video URL"}), 400

    print("video_url is ", video_url)
    downloader = YoutubeCommentDownloader()
    try:
        comments = downloader.get_comments_from_url(video_url, sort_by=SORT_BY_POPULAR)
        print("comments is ", comments)
        all_comments_dict = {
            'cid': [], 'text': [], 'time': [], 'author': [], 'channel': [],
            'votes': [], 'replies': [], 'photo': [], 'heart': [], 'reply': [], 'time_parsed': []
        }

        comment_count = 0

        # 限制评论数量，例如只取前100条
        for comment in islice(comments, 100):
            for key in all_comments_dict.keys():
                all_comments_dict[key].append(comment[key])
            comment_count += 1

        df = pd.DataFrame(all_comments_dict)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        excel_filename = f"youtube_comments_{timestamp}.xlsx"
        csv_filename = f"youtube_comments_{timestamp}.csv"
        
        start_time = time.time()
        
        # 创建 Google Cloud Storage 客户端
        storage_client = storage.Client()
        bucket = storage_client.bucket('yt-comments-bucket')
        
        # 保存 Excel 文件
        excel_output = io.BytesIO()
        with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_output.seek(0)
        excel_blob = bucket.blob(excel_filename)
        excel_blob.upload_from_file(excel_output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        excel_url = excel_blob.public_url
        
        # 保存 CSV 文件
        csv_output = io.StringIO()
        df.to_csv(csv_output, index=False)
        csv_output.seek(0)
        csv_blob = bucket.blob(csv_filename)
        csv_blob.upload_from_string(csv_output.getvalue(), content_type='text/csv')
        csv_url = csv_blob.public_url
        
        logging.info(f"File generation and upload took {time.time() - start_time} seconds")
        
        return jsonify({
            "message": "files saved",
            "filename": excel_filename,
            "url": excel_url,
            "comment_count": comment_count,
            "thumb": "",
            "csvUrl": csv_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/_ah/health')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
