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
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"Searching for keyword: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
                "videoDuration": "long"
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No long videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos]
            
            # Get a unique set of channel IDs to avoid duplicate API calls
            channel_ids = list(set([video["snippet"]["channelId"] for video in videos]))

            if not video_ids or not channel_ids:
                st.warning(f"Skipping keyword: {keyword} due to missing data.")
                continue

            # Fetch stats for all unique channels in a single API call
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data:
                st.warning(f"Could not fetch channel data for keyword: {keyword}")
                continue
            
            # Create a subscriber lookup dictionary {channel_id: subscriber_count}
            channel_subs_map = {
                channel["id"]: int(channel["statistics"].get("subscriberCount", 0))
                for channel in channel_data.get("items", [])
            }

            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()
            stats = stats_data.get("items", [])

            # Combine video snippets with their corresponding stats
            video_details = {}
            for video in videos:
                video_details[video["id"]["videoId"]] = video["snippet"]
            
            for stat in stats:
                video_id = stat["id"]
                if video_id in video_details:
                    snippet = video_details[video_id]
                    
                    # Use the map to get the correct subscriber count
                    channel_id = snippet["channelId"]
                    subs = channel_subs_map.get(channel_id, 0) # Default to 0 if not found
                    views = int(stat["statistics"].get("viewCount", 0))

                    # Apply the filter for subscribers AND views
                    if subs < 3000 and views >= 5000: # Modified this line
                        all_results.append({
                            "Title": snippet.get("title", "N/A"),
                            "Description": snippet.get("description", "")[:200],
                            "URL": f"https://www.youtube.com/watch?v={video_id}",
                            "Views": views,
                            "Subscribers": subs
                        })

        if all_results:
            st.success(f"Found {len(all_results)} results across all keywords!")
            # Sort results by views for better visibility
            sorted_results = sorted(all_results, key=lambda x: x['Views'], reverse=True)
            for result in sorted_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Subscribers:** {result['Subscribers']} | **Views:** {result['Views']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Description:** {result['Description']}..."
                )
                st.write("---")
        else:
            st.warning("No results found for channels with fewer than 3,000 subscribers and at least 5,000 views.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
