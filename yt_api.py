import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
class youtubeAPI():
    api_key = '' #TODO: paste your API key here; https://console.cloud.google.com/apis/dashboard
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
    #   result_count - the number of videos you want to retrieve from the search
    def search_vids(self, search_query, result_count):
        request = self.youtube.search().list(
            part="snippet",
            maxResults=result_count,
            q=search_query
        )
        response = request.execute()
        response = response['items']
        print("--- Search Results ---\n")
        return response

    # Returns comment threads from a video
    # Parameters
    #   id - the videoId of the video you want to get the comments from
    def comments_from_vidId(self,id):
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
                    data = {
                        'author':comment_author_name,
                        'authorId':comment_author_id,
                        'comment':comment
                    }
                    data_list.append(data)
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
        
                    # print comment with list of reply
                    print(comment, replies, end = '\n\n')

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

    def get_transcript(self,video_id):
        return YouTubeTranscriptApi.get_transcript(video_id)
    
    def get_vid_statistics(self,video_id):
        statistics = self.youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()
        print(statistics)
        return statistics

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
    
    def get_comments_fromVids(self,vidIds):
        comments_list = []
        for vid in vidIds:
            vid_comment = self.comments_from_vidId(vid)
            comments_list.append(vid_comment)
        return comments_list
    
    def get_comments_from_search(self,search_query,max_result):
        search_results = self.search_vids(search_query,max_result)
        vid_ids = []
        for res in search_results:
            id = res['id']['videoId']
            vid_ids.append(id)
        return self.get_comments_fromVids(vid_ids)

def main():
    youtube = youtubeAPI()
    df = pd.DataFrame(youtube.get_comments_from_search("foreigner reacts to filipinos", 25))
    df.to_csv('comments.csv',index=False)
    

    #vid_details = youtube.get_vid_statistics('CEc6TTW1Cpo')
    #youtube.video_info_to_dataframe(vid_details).to_csv('vid_deets.csv',index=False)
    #TODO: try the API functions here

if __name__ == "__main__":
    main()

