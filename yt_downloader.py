"""
YouTube Video Downloader - Streamlit Web App
FFmpeg ke bina bhi kaam karega (Streamlit Cloud ke liye optimized)
"""

import streamlit as st
import yt_dlp
import os
import tempfile
import re
from pathlib import Path

st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="🎥",
    layout="centered"
)

st.title("🎥 YouTube Video Downloader")
st.markdown("YouTube video ka URL paste karein aur quality select karke download karein.")

with st.sidebar:
    st.header("ℹ️ Info")
    st.markdown("""
    **Kaise use karein:**
    1. YouTube video URL paste karein
    2. Video ya Audio choose karein
    3. Quality select karein
    4. Download button dabayein
    5. File download ho jayegi
    """)
    st.markdown("---")
    st.caption("Made with Streamlit + yt-dlp")

url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
)

col1, col2 = st.columns(2)

with col1:
    download_type = st.radio(
        "Download Type",
        ["Video (MP4)", "Audio Only"],
        horizontal=True
    )

with col2:
    if download_type == "Video (MP4)":
        quality = st.selectbox(
            "Quality",
            ["Best", "720p", "480p", "360p"],
            index=1
        )
    else:
        quality = st.selectbox(
            "Audio Quality",
            ["Best"],
            index=0
        )

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()[:100]

def get_format_string(download_type: str, quality: str) -> str:
    if download_type == "Audio Only":
        return "bestaudio[ext=m4a]/bestaudio/best"
    
    formats = {
        "Best": "best[ext=mp4]/best",
        "720p": "best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best",
        "480p": "best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]/best",
        "360p": "best[height<=360][ext=mp4]/best[height<=360]/best[ext=mp4]/best",
    }
    return formats.get(quality, "best[ext=mp4]/best")

def download_media(url: str, download_type: str, quality: str):
    temp_dir = tempfile.mkdtemp()
    
    ydl_opts = {
        "format": get_format_string(download_type, quality),
        "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = sanitize_filename(info.get("title", "video"))
            
            downloaded_file = None
            for f in Path(temp_dir).iterdir():
                if f.is_file():
                    downloaded_file = f
                    break
            
            if not downloaded_file:
                raise Exception("File download nahi hua")

            with open(downloaded_file, "rb") as f:
                file_bytes = f.read()

            try:
                os.remove(downloaded_file)
                os.rmdir(temp_dir)
            except:
                pass

            ext = downloaded_file.suffix.lstrip(".") or "mp4"
            filename = f"{title}.{ext}"
            
            return file_bytes, filename, title

    except Exception as e:
        try:
            for f in Path(temp_dir).iterdir():
                f.unlink()
            os.rmdir(temp_dir)
        except:
            pass
        raise e

if st.button("⬇️ Download", type="primary", use_container_width=True):
    if not url or not url.strip():
        st.error("Pehle URL enter karein!")
    else:
        with st.spinner("Download ho raha hai... thoda wait karein ⏳"):
            try:
                file_bytes, filename, title = download_media(url.strip(), download_type, quality)
                
                st.success(f"✅ Download complete: **{title}**")
                
                mime = "audio/mp4" if "m4a" in filename else "video/mp4"
                
                st.download_button(
                    label="📥 File Download Karein (Click here)",
                    data=file_bytes,
                    file_name=filename,
                    mime=mime,
                    use_container_width=True
                )
                
                st.info("Upar wale button se file save kar lein.")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.caption("⚠️ Disclaimer: Personal use only.")
