from flask import Flask, jsonify, request
from services import text
from services import audio
from services import video
import json
from moviepy.editor import AudioFileClip

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home_func():
    return "Welcome to Text to Video Generator"

# creating the script
@app.route("/create-script", methods=["POST"])
def create_script():
    user_input = request.json.get("user_input")
    script_content = text.generate_textual_content(user_input)

    # find the top words for video search
    search_queries = text.find_query_word(script_content, amount=5)
    res = {
        "status": 200,
        "search_queries": search_queries,
        "script_content": script_content
    }
    
    return res

# creating the audio file
@app.route("/create-audio", methods=["POST"])
def create_audio_file():
    script_content = request.json.get("script")
    status, audio_unique_id, audio_path = audio.create_audio_file(script=script_content)
    
    if status is True:
        print(f"Audio genrated file path is {audio_path}")
        return audio_path
    else:
        return None


# creating subtitles and downloading the videos
@app.route("/find-videos", methods=["POST"])
def download_video_create_subtitles():
    search_queries = request.json.get("search_queries")
    num_videos = request.json.get("num_videos")
    audio_path = request.json.get("audio_path")
    script_content = request.json.get("script_content")
    
    
    video_urls = video.find_relevant_videos(keywords=search_queries, num_videos=int(num_videos))
    video_paths = []
    for url in video_urls:
        video_path = video.download_video(url=url)
        if video_path[0] is True:
            video_paths.append(video_path[-1])

    res = json.dumps(video_urls)
    
    # split script into sentances
    sentences = script_content.split(". ")
    sentences = list(filter(lambda x: x != "", sentences))
    paths = []
    
    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    audio_clip.close()

    # Create subtitles for the video
    subtitles = video.generate_subtitles(audio_path)
    
    # combine videos
    com_video_path = video.combine_all_videos(audio_dura=audio_duration, video_path_lst=video_paths)

    res = {
        "subtitles": subtitles,
        "com_video_path": com_video_path
    }

    return res


# combine all videos
@app.route("/combine-video", methods=["POST"])
def combine_all_videos():
    audio_path = request.json.get("audio_path")
    com_video_path = request.json.get("com_video_path")
    subtitles = request.json.get("subtitles")
    subtitles_postion = request.json.get("subtitles_postion")
    
    # Final Video
    final_vid = video.generate_final_video(audio_path, com_video_path, subtitles, subtitles_postion, text_color="#FFFF00")
    print(final_vid)
    
    return final_vid


# application work started
@app.route("/convert_to_text", methods=["GET","POST"])
def create_script():
    ipt = request.json.get("user_input")
    try:
        # creating script
        script_content = text.generate_textual_content(user_input=ipt)
        # generating audio
        msg, audio_unique_id, audio_path = audio.create_audio_file(script=script_content)
        if msg is True:
            print(f"Audio genrated file path is {audio_path}")
        else:
            print("Error creating audio")
        # find the top words for video search
        search_queries = text.find_query_word(script_content, amount=5)
        
        # find videos
        video_urls = video.find_relevant_videos(keywords=search_queries, num_videos=2)
        video_paths = []
        for url in video_urls:
            video_path = video.download_video(url=url)
            if video_path[0] is True:
                video_paths.append(video_path[-1])

        res = json.dumps(video_urls)
        
        # split script into sentances
        sentences = script_content.split(". ")
        sentences = list(filter(lambda x: x != "", sentences))
        paths = []
        
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        audio_clip.close()

        # Create subtitles for the video
        subtitles = video.generate_subtitles(audio_path)
        
        # combine videos
        com_video_path = video.combine_all_videos(audio_dura=audio_duration, video_path_lst=video_paths)

        
        # Final Video
        subtitles_postion = "center,bottom"
        final_vid = video.generate_final_video(audio_path, com_video_path, subtitles, subtitles_postion, text_color="#FFFF00")
        print(final_vid)
                
        return jsonify({"video_urls": res, "words": "".join(search_queries)})

    except Exception as e:
        return f"Invalid user input {e}"
    
    
# Create script
@app.route("/create_script", methods=['POST'])
def create_scipt():
    ipt = request.json.get("user_input")
    
    script_content = text.generate_textual_content(user_input=ipt)
    return jsonify({"script": script_content, "status": 200})


app.run(port=6200, debug=True)