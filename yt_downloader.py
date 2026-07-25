"""
YouTube Video Downloader - Streamlit Web App
=============================================
Run karne ka tareeqa:
1. Terminal mein:  pip install streamlit yt-dlp
2. Phir:           streamlit run yt_downloader.py

Browser automatically open ho jayega (http://localhost:8501)
"""

import streamlit as st
import yt_dlp
import os
import tempfile
import re
from pathlib import Path

# Page config
st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="🎥",
    layout="centered"
)

st.title("🎥 YouTube Video Downloader")
st.markdown("YouTube video ka URL paste karein aur quality select karke download karein.")

# Sidebar info
with st.sidebar:
    st.header("ℹ️ Info")
    st.markdown("""
    **Kaise use karein:**
    1. YouTube video URL paste karein
    2. Video ya Audio choose karein
    3. Quality select karein
    4. Download button dabayein
    5. File download ho jayegi

    **Note:**  
    - Sirf personal use ke liye  
    - Internet chahiye  
    - FFmpeg recommended hai (best quality ke liye)
    """)
    st.markdown("---")
    st.caption("Made with Streamlit + yt-dlp")

# Input
url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Video ka complete URL paste karein"
)

col1, col2 = st.columns(2)

with col1:
    download_type = st.radio(
        "Download Type",
        ["Video (MP4)", "Audio Only (MP3)"],
        horizontal=True
    )

with col2:
    if download_type == "Video (MP4)":
        quality = st.selectbox(
            "Quality",
            ["Best", "1080p", "720p", "480p", "360p"],
            index=1
        )
    else:
        quality = st.selectbox(
            "Audio Quality",
            ["Best", "192kbps", "128kbps"],
            index=0
        )

def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename"""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()[:100]  # limit length

def get_format_string(download_type: str, quality: str) -> str:
    if download_type == "Audio Only (MP3)":
        return "bestaudio/best"
    else:
        formats = {
            "Best": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        }
        return formats.get(quality, "bestvideo+bestaudio/best")

def download_media(url: str, download_type: str, quality: str):
    """Download video/audio and return file bytes + filename"""
    temp_dir = tempfile.mkdtemp()
    
    ydl_opts = {
        "format": get_format_string(download_type, quality),
        "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    # Audio convert to mp3
    if download_type == "Audio Only (MP3)":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192" if quality == "Best" else quality.replace("kbps", ""),
        }]
        ydl_opts["format"] = "bestaudio/best"

    # For video, prefer mp4
    if download_type == "Video (MP4)":
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info.get("title", "video"))
            
            # Find the downloaded file
            downloaded_file = None
            for f in Path(temp_dir).iterdir():
                if f.is_file():
                    downloaded_file = f
                    break
            
            if not downloaded_file:
                raise Exception("File download nahi hua")

            with open(downloaded_file, "rb") as f:
                file_bytes = f.read()

            # Cleanup
            try:
                os.remove(downloaded_file)
                os.rmdir(temp_dir)
            except:
                pass

            ext = "mp3" if download_type == "Audio Only (MP3)" else "mp4"
            filename = f"{title}.{ext}"
            return file_bytes, filename, title

    except Exception as e:
        # Cleanup on error
        try:
            for f in Path(temp_dir).iterdir():
                f.unlink()
            os.rmdir(temp_dir)
        except:
            pass
        raise e

# Download button
if st.button("⬇️ Download", type="primary", use_container_width=True):
    if not url or not url.strip():
        st.error("Pehle URL enter karein!")
    elif "youtube.com" not in url and "youtu.be" not in url:
        st.warning("Yeh YouTube URL nahi lag raha. Phir bhi try kar rahe hain...")
    
    with st.spinner("Download ho raha hai... thoda wait karein ⏳"):
        try:
            file_bytes, filename, title = download_media(url.strip(), download_type, quality)
            
            st.success(f"✅ Download complete: **{title}**")
            
            mime = "audio/mpeg" if filename.endswith(".mp3") else "video/mp4"
            
            st.download_button(
                label="📥 File Download Karein (Click here)",
                data=file_bytes,
                file_name=filename,
                mime=mime,
                use_container_width=True
            )
            
            st.info("Upar wale button se file apne computer mein save kar lein.")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.markdown("""
            **Possible reasons:**
            - Invalid / private / age-restricted video
            - Internet issue
            - YouTube ne temporarily block kiya
            - FFmpeg installed nahi hai (audio convert ke liye zaroori)
            """)

st.markdown("---")
st.caption("⚠️ Disclaimer: Sirf un videos ke liye use karein jinke aapke paas rights hain. Personal use only.")
