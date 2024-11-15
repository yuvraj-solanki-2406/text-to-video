import os
import requests
from dotenv import load_dotenv
from termcolor import colored
import uuid
import moviepy
import assemblyai as aai
from moviepy.editor import *
from moviepy.video.fx.all import crop
from moviepy.video.tools.subtitles import SubtitlesClip
# import srt_qualizer

# configure imagemagick
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

load_dotenv()

pexel_api = os.getenv("PEXEL_API")
ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI")

# find relvant video from pixel
def find_relevant_videos(keywords: list, num_videos=5, api_key=pexel_api):
    query = "".join(keywords)
    
    header = {
        'authorization': api_key,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    qurl = f"https://api.pexels.com/videos/search?query={query}&per_page={num_videos}"

    # Send the request
    raw_response = requests.get(qurl ,headers=header)

    response = raw_response.json()
    
    # Parse each video
    video_url = []
    
    try:
        # loop through each video in the result
        for i in range(num_videos):
            raw_urls = response["videos"][i]["video_files"]
            temp_video_url = ""
            video_res = 0
            # loop through each url to determine the best quality
            for video in raw_urls:
                if ".com/video-files" in video["link"]:
                    if (video["width"]*video["height"]) > video_res:
                        temp_video_url = video["link"]
                        video_res = video["width"]*video["height"]
                        
            if temp_video_url != "":
                video_url.append(temp_video_url)
                
    except Exception as e:
        print("[-] No Videos found.", "red")

    return video_url


# downlaod a video
def download_video(url):
    unique_id = uuid.uuid4()
    
    video_path = f"./resources/videos/video_file_{unique_id}.mp4"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    response = requests.get(url, stream=True, headers=header)
    
    if response.status_code == 200:
        with open(video_path, mode="wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        if os.path.getsize(video_path) > 0:
            print(f"Video downloaded successfully: {video_path}")
            return (True, video_path)
        else:
            return (False, "Error: The downloaded video file is empty.")
    else:
        return (False, f"Failed to download video. HTTP Status Code: {response.status_code}")


# merge different videos:
def combine_all_videos(video_path_lst, audio_dura, max_clip_duration=8, threads=2):
    video_id = uuid.uuid4()
    
    combined_video_dir = "resources/videos/"
    os.makedirs(combined_video_dir, exist_ok=True)
    
    combined_video_path = f"{combined_video_dir}combined_{video_id}.mp4"
    
    if len(video_path_lst) == 1:
        combined_video_path = video_path_lst[0]
        return combined_video_path
    
    # Required duration of each clip
    req_dur = audio_dura / len(video_path_lst)

    clips = []
    tot_dur = 0
    while tot_dur < audio_dura:
        for video_path in video_path_lst:
            clip = VideoFileClip(video_path)
            clip = clip.without_audio()
            # Check if clip is longer than the remaining audio
            if (audio_dura - tot_dur) < clip.duration:
                clip = clip.subclip(0, (audio_dura - tot_dur))
            # Only shorten clips if the calculated clip length (req_dur) is shorter than the actual clip to prevent still image
            elif req_dur < clip.duration:
                clip = clip.subclip(0, req_dur)
            clip = clip.set_fps(30)

            # Not all videos are same size,
            # so we need to resize them
            if round((clip.w/clip.h), 4) < 0.9625:
                clip = crop(clip, width=clip.w, height=round(clip.w/0.9625), \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            else:
                clip = crop(clip, width=round(0.9625*clip.h), height=clip.h, \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            clip = clip.resize((1080, 1920))

            if clip.duration > max_clip_duration:
                clip = clip.subclip(0, max_clip_duration)

            clips.append(clip)
            tot_dur += clip.duration

    final_clip = concatenate_videoclips(clips)
    final_clip = final_clip.set_fps(30)
    final_clip.write_videofile(combined_video_path, threads=threads)

    return combined_video_path


# create subtitles for a video
def generate_subtitles(audio_path):
    subtitles_path = f"resources/subtitles/subtitle_{uuid.uuid4()}.srt"
    
    if ASSEMBLY_AI_API_KEY is not None and ASSEMBLY_AI_API_KEY != "":
        print(colored("[+] Creating subtitles using AssemblyAI", "blue"))
        aai.settings.api_key = ASSEMBLY_AI_API_KEY
        
        config = aai.TranscriptionConfig(language_code="en")
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_path)
        subtitles = transcript.export_subtitles_srt()
    else:
        return "Subtitles cannot be created check Assembly API"

    with open(subtitles_path, "w") as file:
        file.write(subtitles)
    print(colored("[+] Subtitles created", "green"))
    return subtitles_path


# generate final video
def generate_final_video(audio, com_video, subtitles, subtitles_position, text_color, n_threads=2):
    generator = lambda txt: TextClip(
        txt,
        font="resources/fonts/bold_font.ttf",
        fontsize=60,
        color=text_color,
        stroke_color="black",
        stroke_width=4,
    )
    
    # Split the subtitles position into horizontal and vertical
    horizontal_subtitles_position, vertical_subtitles_position = subtitles_position.split(",")

    # Burn the subtitles into the video
    subtitles = SubtitlesClip(subtitles, generator)
    result = CompositeVideoClip([
        VideoFileClip(com_video),
        subtitles.set_pos((horizontal_subtitles_position, vertical_subtitles_position))
    ])

    # Add the audio
    audio = AudioFileClip(audio)
    result = result.set_audio(audio)

    result.write_videofile(f"resources/videos/output_{uuid.uuid4()}.mp4", threads=n_threads or 2)

    print(f"File created output_{uuid.uuid4()}.mp4", color="green")
    
    return f"output_{uuid.uuid4()}.mp4"
