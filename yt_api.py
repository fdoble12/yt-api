import os
from dotenv import load_dotenv

from googleapiclient.discovery import build
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd

class youtubeAPI():
    load_dotenv()
    api_key = os.environ.get("API_KEY")

    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey= self.api_key)

    #Downloads the thumbnail of a video
    # Parameters needed: 
    #   img_url - URL of the thumbnail
    #   vid_id - id of the video    
    def download_image(self,img_url,vid_id):
        try:
            save_directory = "/Users/francisdoble/Documents/youtube-api/Thumbnails" #TODO: Change path
            os.makedirs(save_directory, exist_ok=True)        
            response = requests.get(img_url)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx HTTP status codes
            save_path = os.path.join(save_directory, f"{vid_id}.jpg")
            with open(save_path, 'wb') as file:
                file.write(response.content)

            print(f"Image downloaded and saved as {save_path}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    # Returns a JSON list of youtube videos from the search query
    # Parameters:
    #   search_query - string of keywords of videos that will be searched
    #   max_results - the number of videos you want to retrieve from the search
    def search_vids(self, search_query, max_results):
        request = self.youtube.search().list(
            part="snippet",
            maxResults=max_results,
            q=search_query
        )
        response = request.execute()
        response = response['items']
        return response
    
    # Returns the video details and statistics of a single video ID
    def get_vid_details(self,video_id):
        statistics = self.youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()
        return statistics
    
    # Returns comment threads from a single video
    # Parameters
    #   id - the videoId of the video you want to get the comments from
    def get_comments_from_vidId(self,id):
        video_response=self.youtube.commentThreads().list(
			part='snippet,replies',
			videoId=id
			).execute()
        comments_file = 'comments.txt'
        data_list = []
        with open(comments_file,'w',encoding='utf-8') as file:
            while video_response:
                for item in video_response['items']:
                # Extracting comments
                    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    comment_author_id = item['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
                    comment_author_name = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                    # counting number of reply of comment
                    replycount = item['snippet']['totalReplyCount']
                    file.write(f"Author: {comment_author_name} - {comment_author_id}\n")
                    file.write(f"{comment} - - - Reply Count: {replycount}\n")
                    
                    replies = []
                    # if reply is there
                    if replycount>0:
                        file.write('Replies:\n')
                        # iterate through all reply
                        for reply in item['replies']['comments']:
                        
                            # Extract reply
                            reply = reply['snippet']['textDisplay']
                            
                            # Store reply is list
                            replies.append(reply)
                            file.write(f"{reply}\n")
                    file.write("\n------------------\n")
                    data = {
                        'author':comment_author_name,
                        'authorId':comment_author_id,
                        'comment':comment,
                        'replies':replies,
                        'videoId':id
                    }
                    data_list.append(data)
                    # empty reply list
                    replies = []
                # Again repeat
                if 'nextPageToken' in video_response:
                    video_response = self.youtube.commentThreads().list(
                            part = 'snippet,replies',
                            videoId = id,
                            pageToken = video_response['nextPageToken']
                        ).execute()
                else:
                    break
        return data_list
    
    #Get comments from an array of video Ids
    def get_comments_from_videos(self,vidIds):
        comments_list = []
        for vid in vidIds:
            vid_comment = self.comments_from_vidId(vid)
            comments_list.append(vid_comment)
        comments_list = [item for sublist in comments_list for item in sublist]
        return comments_list

    def get_transcript(self,video_id):
        return YouTubeTranscriptApi.get_transcript(video_id)
    
    # Get comments from a video search query; Returns a JSON list of comments
    def get_comments_from_search(self,search_query,max_result):
        search_results = self.search_vids(search_query,max_result)
        vid_ids = []
        for res in search_results:
            id = res['id']['videoId']
            vid_ids.append(id)
        return self.get_comments_from_videos(vid_ids)

    # Get video details and statistics of videos from a search query; Returns a JSON list of video details and statistics
    def get_vid_details_from_search(self,search_query,max_result):
        videos = self.search_vids(search_query,max_result)
        vid_details = []
        for vid in videos:
            id = vid['id']['videoId']
            vid_details.append(self.get_vid_details(id))
        return vid_details
    
    # Accepts a JSON list of video details and statistics then converts video details to dataframe
    def video_stats_to_dataframe(self,videos):
        data_list = []
        print(videos)
        for video_info in videos:
            items = video_info['items']
            if not items:
                return None

            for item in items:
                video_data = item['snippet']
                statistics = item['statistics']

                data = {
                    'title': video_data['title'],
                    'videoId': item['id'],
                    'channelTitle': video_data['channelTitle'],
                    'channelId': video_data['channelId'],
                    'publishedAt': video_data['publishedAt'],
                    'viewCount': int(statistics['viewCount']),
                    'likeCount': int(statistics['likeCount']),
                    'favoriteCount': int(statistics['favoriteCount']),
                    'commentCount': int(statistics['commentCount']),
                    #'tags': video_data['tags']
                }

                data_list.append(data)
        df = pd.DataFrame(data_list)
        return df