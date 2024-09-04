from itertools import islice
import pandas as pd
from youtube_comment_downloader import *
downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url(
    'https://www.youtube.com/watch?v=ScMzIvxBSi4', sort_by=SORT_BY_POPULAR)
print(comments)

# comment_count = sum(1 for _ in comments)
# print(f"评论数量：{comment_count}")

# Initiate a dictionary to save all comments from Youtube Video
all_comments_dict = {
    'cid': [],
    'text': [],
    'time': [],
    'author': [],
    'channel': [],
    'votes': [],
    'replies': [],
    'photo': [],
    'heart': [],
    'reply': [],
    'time_parsed': []
}

# Take all comment and save it in dictionary using for loop
for comment in comments:
    for key in all_comments_dict.keys():
        all_comments_dict[key].append(comment[key])

# Convert Dictionary to Dataframe using Pandas
comments_df = pd.DataFrame(all_comments_dict)

# Display Dataframe
# display(comments_df)

# comments_df.to_excel('comments_data.xlsx', index=False)
comments_df.to_csv('comments_data.csv', index=False)
# for comment in islice(comments, 10):
#     print(comment)
