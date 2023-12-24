import pandas as pd
from googleapiclient.discovery import build

# Define your YouTube API key and create the YouTube service
api_key = 'AIzaSyBof5NTAckcmW1Wu4V2UL0lxSB2kZogJmg'  # Replace with your actual YouTube API key
youtube = build('youtube', 'v3', developerKey=api_key)

# Function to check if a channel is from the Philippines
def is_philippine_channel(channel_id):
    try:
        channel_info = youtube.channels().list(
            part='snippet',
            id=channel_id
        ).execute()
        
        country = channel_info['items'][0]['snippet']['country']
        
        return country == 'PH'  # 'PH' is the country code for the Philippines
    except Exception as e:
        print(f"Error checking channel {channel_id}: {str(e)}")
        return False

# Function to check if a video has relevant terms in its title, caption, or keywords
def has_relevant_terms(video_id, relevant_terms):
    try:
        video_info = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        snippet = video_info['items'][0]['snippet']
        
        # Check if the video title, description, or keywords contain relevant terms
        title = snippet.get('title', '').lower()
        description = snippet.get('description', '').lower()
        tags = [tag.lower() for tag in snippet.get('tags', [])]
        
        return any(term in title or term in description or term in tags for term in relevant_terms)
    except Exception as e:
        print(f"Error checking video {video_id}: {str(e)}")
        return False

for i in range(2,8):
    # Load the CSV file into a DataFrame
    csv_file = f'videos_reacts_0{i}-2018.csv'  # Replace with the path to your CSV file
    df = pd.read_csv(csv_file)

    # Define relevant terms related to the Philippines, including Tagalog words
    relevant_terms = ['philippines', 'pinoy', 'tagalog', 'filipino', 'manila', 'filipina', 'pinas']

    # Filter out channels that are not from the Philippines and videos with relevant terms
    df['is_philippine'] = df['channelId'].apply(is_philippine_channel)
    df['has_relevant_terms'] = df['videoId'].apply(lambda video_id: has_relevant_terms(video_id, relevant_terms))

    filtered_df = df[(df['is_philippine'] == False) & (df['has_relevant_terms'] == True)]

    # Save the filtered DataFrame to a new CSV file
    output_csv = f'output_{i}.csv'  # Replace with the desired output file path
    filtered_df.to_csv(output_csv, index=False)

    print(f"Filtered channels and videos saved to {output_csv}")
