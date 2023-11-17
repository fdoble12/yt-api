import yt_api
from datetime import datetime, timedelta
import pandas as pd
keyNum = 3
api =yt_api.youtubeAPI(keyNum)

for i in range(1,8):
    df = pd.read_csv(f'output_{i}.csv')
    videos = df['videoId'].to_list()
    comments = api.get_comments_from_videos(videos)
    pd.DataFrame(comments).to_csv(f'comments_output_{i}.csv',index=False)