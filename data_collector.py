import yt_api
from datetime import datetime, timedelta
import pandas as pd

class Cl():

    def __init__(self,keyNum):
        self.keyNum = keyNum
        self.api =yt_api.youtubeAPI(keyNum)
    
    def collect(self,search_query,max_results,published_after,published_before):
        response = self.api.get_vid_details_from_search(search_query, max_results, published_after, published_before)
        temp = self.api.video_stats_to_dataframe(response)
        return temp

