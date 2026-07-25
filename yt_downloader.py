import streamlit as st
import yt_dlp
import os
import tempfile
import re
from pathlib import Path

st.set_page_config(page_title="YouTube Downloader", page_icon="🎥", layout="centered")

st.title("🎥 YouTube Video Downloader")
st.caption("Note: Free cloud servers pe YouTube kabhi-kabhi block laga deta hai.")

url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

col1, col2 = st.columns(2)
with col1:
    download_type = st.radio("Type", ["Video (MP4)", "Audio Only"], horizontal=True)
with col2:
    if download_type == "Video (MP4)":
        quality = st.selectbox("Quality", ["Best", "720p", "480p", "360p"], index=1)
    else:
        quality = "Best"

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()[:100]

def get_format(download_type, quality):
    if download_type == "Audio Only":
        return "bestaudio[ext=m4a]/bestaudio/best"
    formats = {
        "Best": "best[ext=mp4]/best",
        "720p": "best[height<=720][ext=mp4]/best[height<=720]/best",
        "480p": "best[height<=480][ext=mp4]/best[height<=480]/best",
        "360p": "best[height<=360][ext=mp4]/best[height<=360]/best",
    }
    return formats.get(quality, "best[ext=mp4]/best")

def download_media(url, download_type, quality):
    temp_dir = tempfile.mkdtemp()

    ydl_opts = {
        "format": get_format(download_type, quality),
        "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # 403 kam karne ke liye extra options
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        },
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
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
                raise Exception("File download nahi hui")

            with open(downloaded_file, "rb") as f:
                file_bytes = f.read()

            try:
                os.remove(downloaded_file)
                os.rmdir(temp_dir)
            except:
                pass

            ext = downloaded_file.suffix.lstrip(".") or "mp4"
            return file_bytes, f"{title}.{ext}", title

    except Exception as e:
        try:
            for f in Path(temp_dir).iterdir():
                f.unlink()
            os.rmdir(temp_dir)
        except:
            pass
        raise e

if st.button("⬇️ Download", type="primary", use_container_width=True):
    if not url.strip():
        st.error("URL enter karein")
    else:
        with st.spinner("Download ho raha hai..."):
            try:
                file_bytes, filename, title = download_media(url.strip(), download_type, quality)
                st.success(f"✅ {title}")
                st.download_button(
                    "📥 File Download Karein",
                    data=file_bytes,
                    file_name=filename,
                    mime="video/mp4",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.warning("YouTube ne is server ko block kiya hua hai. Free cloud pe yeh problem common hai.")

st.markdown("---")
st.caption("Personal use only.")
