from services import video
import uuid
import os
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

audio_path = "resources/audios/audio_e3f38469-7009-4d13-8fe8-474bfebfd489.mp3"
com_video_path = "resources/videos/combined_0066ddf8-2abb-4e31-97ef-fb17f515f231.mp4"
subtitles = "resources/subtitles/subtitle_76c16d6f-8713-40e6-b863-dec50f6851a1.srt"

subtitles_postion = "center,center"

if __name__ == "__main__":
    final_vid = video.generate_final_video(audio_path, com_video_path, subtitles, subtitles_postion, text_color="#FFFF00")
    print(final_vid)


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
            if round((clip.w/clip.h), 4) < 0.5625:
                clip = crop(clip, width=clip.w, height=round(clip.w/0.5625), \
                            x_center=clip.w / 2, \
                            y_center=clip.h / 2)
            else:
                clip = crop(clip, width=round(0.5625*clip.h), height=clip.h, \
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

