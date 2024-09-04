from flask import Flask, jsonify, render_template_string
from itertools import islice
import pandas as pd
from youtube_comment_downloader import *

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
    <h1>Welcome to the YouTube Comment Downloader API</h1>
    <p> use /api/comments</p>
    """)

@app.route('/api/comments', methods=['GET'])
def get_comments():
    downloader = YoutubeCommentDownloader()
    comments = downloader.get_comments_from_url(
        'https://www.youtube.com/watch?v=ScMzIvxBSi4', sort_by=SORT_BY_POPULAR)

    all_comments_dict = {
        'cid': [], 'text': [], 'time': [], 'author': [], 'channel': [],
        'votes': [], 'replies': [], 'photo': [], 'heart': [], 'reply': [], 'time_parsed': []
    }

    # 限制评论数量，例如只取前100条
    for comment in islice(comments, 100):
        for key in all_comments_dict.keys():
            all_comments_dict[key].append(comment[key])

    return jsonify(all_comments_dict)

@app.route('/_ah/health')
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)
