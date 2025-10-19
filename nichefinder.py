import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyBwLEIP3GURhx7mEdFcOzb-TS4hv7XiLBI" # Remember to keep your API key private
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# --- KEYWORDS UPDATED AS REQUESTED ---
keywords = [
    # Historical Enigmas
    "what happened to the lost colony of roanoke",
    "dyatlov pass incident explained",
    "antikythera mechanism explained",
    "gobekli tepe documentary",
    "the voynich manuscript",
    "oak island money pit",
    "atlantis documentary",
    "ancient mysteries documentary",
    # Unsolved Crimes
    "jack the ripper documentary",
    "who was db cooper",
    "zodiac killer documentary",
    "elisa lam case explained",
    "black dahlia unsolved",
    "jonbenet ramsey theories",
    "madeleine mccann documentary",
    "unsolved disappearances",
    # Cryptids & Paranormal
    "skinwalker ranch stories",
    "mothman documentary",
    "bigfoot documentary",
    "loch ness monster evidence",
    "real ghost stories",
    "paranormal stories",
    "mysteries of the bermuda triangle",
    "unexplained paranormal phenomena",
    # Conspiracy Theories
    "jfk assassination theory",
    "moon landing conspiracy",
    "area 51 documentary",
    "roswell incident explained",
    "illuminati documentary",
    "new world order explained",
    "chemtrails theory",
    "flat earth documentary",
    "mandela effect examples",
    "simulation theory documentary",
    # Weird History
    "weird history facts",
    "medieval torture devices"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate over the list of keywords
        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            # Define search parameters
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
                "videoDuration": "long"  # <-- THIS LINE FILTERS FOR VIDEOS > 20 MINS
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Check if "items" key exists
            if "items" not in data or not data["items"]:
                st.warning(f"No long videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"Failed to fetch video statistics for keyword: {keyword}")
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"Failed to fetch channel statistics for keyword: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Create a dictionary for quick lookup of channel subscribers
            channel_subs_map = {channel_item["id"]: int(channel_item["statistics"].get("subscriberCount", 0)) for channel_item in channels}

            # Collect results
            for video_snippet in videos:
                video_id = video_snippet["id"]["videoId"]
                
                # Find corresponding stat and channel data
                current_stat = next((s for s in stats if s["id"] == video_id), None)
                if not current_stat:
                    continue # Skip if stats are missing for this video

                title = video_snippet["snippet"].get("title", "N/A")
                description = video_snippet["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                views = int(current_stat["statistics"].get("viewCount", 0))
                
                channel_id = video_snippet["snippet"]["channelId"]
                subs = channel_subs_map.get(channel_id, 0)


                if subs < 3000 and views >= 5000:  # Only include channels with fewer than 3,000 subscribers AND 5,000+ views
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} results across all keywords!")
            sorted_results = sorted(all_results, key=lambda x: x['Views'], reverse=True) # Sort by views
            for result in sorted_results:
                st.markdown(
                    f"**Title:** {result['Title']} \n"
                    f"**Description:** {result['Description']} \n"
                    f"**URL:** [Watch Video]({result['URL']}) \n"
                    f"**Views:** {result['Views']} \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("No results found for channels with fewer than 3,000 subscribers and at least 5,000 views.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
