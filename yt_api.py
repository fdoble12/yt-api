import os
from dotenv import load_dotenv

from googleapiclient.discovery import build
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd

class youtubeAPI():

    def __init__(self,keyNum):
        load_dotenv()
        api_key = os.environ.get(f"API_KEY{keyNum}")
        self.youtube = build('youtube', 'v3', developerKey=api_key)

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
    def search_vids(self, search_query, max_results,dateAfter,dateBefore):
        request = self.youtube.search().list(
            part="snippet",
            maxResults=max_results,
            q=search_query,
            type="video",
            publishedAfter=dateAfter,
        	publishedBefore=dateBefore
        )
        response = request.execute()
        response = response['items']
        return response
    
    # Returns the video details and statistics of a single video ID
    def get_vid_details(self,video_id):
        details = self.youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()
        return details
    
    # Returns comment threads from a single video
    # Parameters
    #   id - the videoId of the video you want to get the comments from
    def get_comments_from_vidId(self,id):
        video_response=self.youtube.commentThreads().list(
            part='snippet,replies',
            videoId=id
            ).execute()
        data_list = []
        print(f"Getting comments for Video: {id}....")
        while video_response:
            for item in video_response['items']:
            # Extracting comments
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                try:
                    comment_author_id = item['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
                except:
                    comment_author_id = 'N/A'
                comment_author_name = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                publishedAt = item['snippet']['topLevelComment']['snippet']['publishedAt']
                # counting number of reply of comment
                replycount = item['snippet']['totalReplyCount']
                topLevelLikeCount = item['snippet']['topLevelComment']['snippet']['likeCount']
                
                replies = []
                # if reply is there
                if replycount>0:
                    # iterate through all reply
                    for reply in item['replies']['comments']:
                    
                        # Extract reply
                        rep = reply['snippet']['textDisplay']
                        replyAuthorId = reply['snippet']['authorChannelId']['value']
                        replyAuthorName = reply['snippet']['authorDisplayName']
                        publishedAt = reply['snippet']['publishedAt']
                        likeCount = reply['snippet']['likeCount']
                        replyDetails = {
                            'replyAuthorId':replyAuthorId,
                            'replyAuthorName':replyAuthorName,
                            'datePublished':publishedAt,
                            'replyText':rep,
                            'likeCount':likeCount
                        }
                        # Store reply is list
                        replies.append(replyDetails)
                data = {
                    'videoId':id,
                    'author':comment_author_name,
                    'authorId':comment_author_id,
                    'comment':comment,
                    'datePublished':publishedAt,
                    'replies':replies,
                    'likeCount':topLevelLikeCount
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
            #print((data_list))
        return data_list
        
    
    #Get comments from an array of video Ids
    def get_comments_from_videos(self,vidIds):
        comments_list = []
        for vid in vidIds:
            try:
                vid_comment = self.get_comments_from_vidId(vid)
                comments_list.append(vid_comment)
            except Exception as e:
                print(f'{vid} has no comments: {e}')
        comments_list = [item for sublist in comments_list for item in sublist]
        return comments_list

    def get_transcript(self,video_id):
        return YouTubeTranscriptApi.get_transcript(video_id)
    
    # Get comments from a video search query; Returns a JSON list of comments
    def get_comments_from_search(self,search_query,max_result):
        search_results = self.search_vids(search_query,max_result)
        vid_ids = []
        i = 0
        for res in search_results:
            print(f'count: {i}\n')
            id = res['id']['videoId']
            vid_ids.append(id)
            i+=1
        return self.get_comments_from_videos(vid_ids)

    # Get video details and statistics of videos from a search query; Returns a JSON list of video details and statistics
    def get_vid_details_from_search(self,search_query,max_result,dateAfter,dateBefore):
        videos = self.search_vids(search_query,max_result,dateAfter,dateBefore)
        vid_details = []
        for vid in videos:
            id = vid['id']['videoId']
            vid_details.append(self.get_vid_details(id))
        return vid_details
    
    # Accepts a JSON list of video details and statistics then converts video details to dataframe
    def video_stats_to_dataframe(self,videos):
        data_list = []
        for video_info in videos:
            items = video_info['items']
            if not items:
                return None

            for item in items:
                video_data = item['snippet']
                statistics = item['statistics']
                title= video_data['title']
                videoId= item['id']
                channelTitle= video_data['channelTitle']
                channelId= video_data['channelId']
                publishedAt= video_data['publishedAt']
                try:
                    viewCount= int(statistics['viewCount'])
                except:
                    viewCount = -1

                try:
                    likeCount= int(statistics['likeCount'])
                except:
                    likeCount = -1
                
                try:
                    favoriteCount= int(statistics['favoriteCount'])
                except:
                    favoriteCount=-1
                try:
                    commentCount= int(statistics['commentCount'])
                except:
                    commentCount = -1
                data = {
                    'title': title,
                    'videoId': videoId,
                    'channelTitle': channelTitle,
                    'channelId': channelId,
                    'publishedAt': publishedAt,
                    'viewCount': viewCount,
                    'likeCount': likeCount,
                    'favoriteCount': favoriteCount,
                    'commentCount': commentCount,
                    #'tags': video_data['tags']
                }
                data_list.append(data)
        df = pd.DataFrame(data_list)
        return df