"""
Streamlit Dashboard for AI Learning Coach.
"""
import streamlit as st
import requests
import os

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')

st.set_page_config(
    page_title="AI Learning Coach",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Learning Coach Dashboard")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Upload Content", "RSS Feeds", "Daily Digest", "Settings"]
)

if page == "Upload Content":
    st.header("Upload Learning Content")
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt', 'md'])
    
    if uploaded_file is not None:
        if st.button("Upload"):
            files = {'file': uploaded_file}
            data = {'name': uploaded_file.name, 'type': uploaded_file.type}
            
            with st.spinner(f"Uploading and processing {uploaded_file.name}..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/content/",
                        files=files,
                        data=data
                    )
                    if response.status_code == 201:
                        st.success(f"Successfully uploaded {uploaded_file.name}")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error uploading file: {e}")

elif page == "RSS Feeds":
    st.header("RSS Feed Configuration")
    
    # Add new feed
    with st.form("add_feed"):
        feed_url = st.text_input("RSS Feed URL")
        submitted = st.form_submit_button("Add Feed")
        if submitted and feed_url:
            with st.spinner("Adding RSS feed..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/rss/feeds/",
                        json={"feed_url": feed_url}
                    )
                    if response.status_code == 201:
                        st.success("Feed added successfully")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error adding feed: {e}")
    
    # List feeds
    with st.spinner("Loading RSS feeds..."):
        try:
            response = requests.get(f"{API_BASE_URL}/rss/feeds/")
            if response.status_code == 200:
                feeds = response.json()
                if feeds:
                    st.subheader("Configured Feeds")
                for feed in feeds:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{feed.get('name', 'Unnamed')}**")
                        st.write(f"URL: {feed['feed_url']}")
                    with col2:
                        if st.button("Fetch", key=f"fetch_{feed['id']}"):
                            with st.spinner(f"Fetching articles from {feed.get('name', 'feed')}..."):
                                try:
                                    fetch_response = requests.post(
                                        f"{API_BASE_URL}/rss/feeds/{feed['id']}/fetch/"
                                    )
                                    if fetch_response.status_code == 200:
                                        result = fetch_response.json()
                                        st.success(f"Fetched {result.get('created_count', 0)} new articles!")
                                    else:
                                        st.error("Error fetching")
                                except Exception as e:
                                    st.error(f"Error: {e}")
            else:
                st.error("Error loading feeds")
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "Daily Digest":
    st.header("Daily Learning Digest")
    
    if st.button("Generate Digest"):
        with st.spinner("Generating your personalized learning digest... This may take a moment."):
            try:
                response = requests.post(f"{API_BASE_URL}/digest/generate/")
                if response.status_code == 201:
                    st.success("Digest generated successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Show latest digest
    with st.spinner("Loading latest digest..."):
        try:
            response = requests.get(f"{API_BASE_URL}/digest/latest/")
            if response.status_code == 200:
                digest = response.json()
                st.subheader(f"Latest Digest - {digest['generated_at']}")
                
                if digest.get('ragas_score'):
                    st.metric("RAGAS Score", f"{digest['ragas_score']:.2f}")
                
                content = digest.get('content', {})
                if content:
                    st.write("### Today's Focus")
                    st.write(content.get('today_focus', 'N/A'))
                    
                    st.write("### Recommended Content")
                    for item in content.get('recommended_content', []):
                        st.write(f"**{item.get('topic')}**")
                        st.write(item.get('description', ''))
            elif response.status_code == 404:
                st.info("No digests available yet. Generate one to get started!")
        except Exception as e:
            st.error(f"Error: {e}")

elif page == "Settings":
    st.header("Settings")
    
    # List all content sources
    st.subheader("Content Sources")
    with st.spinner("Loading content sources..."):
        try:
            response = requests.get(f"{API_BASE_URL}/content/")
            if response.status_code == 200:
                sources = response.json()
                for source in sources:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{source['name']}** ({source['type']})")
                        st.write(f"Status: {source['status']} | Chunks: {source.get('chunks_count', 0)}")
                    with col2:
                        if st.button("Delete", key=f"del_{source['id']}"):
                            with st.spinner("Deleting content..."):
                                try:
                                    del_response = requests.delete(f"{API_BASE_URL}/content/{source['id']}/")
                                    if del_response.status_code == 204:
                                        st.success("Deleted!")
                                        st.rerun()
                                    else:
                                        st.error("Error deleting content")
                                except Exception as e:
                                    st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

