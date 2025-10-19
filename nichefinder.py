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
        start_date = (datetime.utcnow() - timedelta(days=int(days
