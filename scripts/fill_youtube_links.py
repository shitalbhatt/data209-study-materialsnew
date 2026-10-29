"""Fill YouTube links into site/course-videos/videos.json after uploading.

Use the progress file written by the Colab auto-uploader (state.json in your Drive folder DATA209_upload_state):

    python3 scripts/fill_youtube_links.py /path/to/state.json

It sets youtubeId for every uploaded video and Short, and the playlist links. Videos not uploaded yet stay as
'coming soon'. Commit and push site/course-videos/videos.json to update the website.
You can also edit videos.json by hand: paste the id (the part after youtu.be/) into "youtubeId".
"""
import json, sys, os

state = json.load(open(sys.argv[1]))
path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "site", "course-videos", "videos.json")
data = json.load(open(path))
n_v = n_s = 0
for v in data["videos"]:
    st = state.get(v["id"] + ".mp4", {})
    if st.get("id"):
        v["youtubeId"] = st["id"]; n_v += 1
    if v.get("short"):
        sh = state.get("shorts/S_" + v["id"] + ".mp4", {})
        if sh.get("id"):
            v["short"]["youtubeId"] = sh["id"]; n_s += 1
for p in data["playlists"]:
    pid = state.get("_playlists", {}).get(p["title"])
    if pid:
        p["url"] = "https://www.youtube.com/playlist?list=" + pid
json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
print(f"linked {n_v} videos, {n_s} Shorts, {sum(1 for p in data['playlists'] if p['url'])} playlists -> {os.path.normpath(path)}")
