from gtts import gTTS
import uuid
import os

current_file_path = os.path.abspath(__file__)

base_path = os.path.dirname(os.path.dirname(current_file_path))
audio_files_path = os.path.join(base_path, "video_resources", "audios")

# create audio file
def create_audio_file(script: str):
    tts = gTTS(text=script, lang="en", tld='co.in')
    unique_num = uuid.uuid4()
    audio_file_path = os.path.join(audio_files_path, f"audio_{unique_num}.mp3")

    tts.save(audio_file_path)
    
    return True, unique_num, audio_file_path
