import yt_api
from datetime import datetime, timedelta
import pandas as pd
keyNum = 1
api =yt_api.youtubeAPI(keyNum)

# Define the search query, max results, and start date
search_query = "Foreigner try filipino food"  # Your search query
max_results = 50  # Maximum results per query
start_date = datetime(2018, 1, 1)  # Start date

# Define the end date
end_date = datetime(2018, 1, 30)

# Create a time delta
delta = timedelta(days=10)
all_responses = pd.DataFrame()
all_comments = pd.DataFrame()
while start_date <= end_date:
    # Convert dates to the required format (ISO 8601)
    published_after = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    next_date = start_date + delta
    published_before = next_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"---Collecting data for {search_query} for Dates {published_after} to {published_before}....")
    # Call the search_vids function with the current date range
    try:
        response = api.get_vid_details_from_search(search_query, max_results, published_after, published_before)
    except Exception as e:
        print(f"Error in search: {e}... trying another api key")
        api = yt_api.youtubeAPI(keyNum+1)
        response = api.get_vid_details_from_search(search_query, max_results, published_after, published_before)

    temp = api.video_stats_to_dataframe(response)
    all_responses = pd.concat([all_responses,temp])
    vidIds = temp['videoId'].to_list()
    print(f"Collecting comments for: {vidIds}....")
    try:
        comment_list = api.get_comments_from_videos(vidIds)
    except Exception as e:
        print(f"Error here in get comments {e}..changing api key")
        api = yt_api.youtubeAPI(keyNum+1)
        comment_list = api.get_comments_from_videos(temp['videoId'].to_list())

    comments_df = pd.DataFrame(comment_list)
    all_comments = pd.concat([all_comments,comments_df])
    # Move to the next delta interval
    start_date = next_date

# Continue with any further processing as needed
# ...
all_responses.to_csv("Foreigner Reacts to Filipinos 2015.csv",index=False)
all_comments.to_csv("Comments_Foreigner Reacts to Filipinos.csv",index=False)
print(f"Data collection for {search_query} from {start_date} to {end_date} completed")