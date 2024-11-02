from gtts import gTTS
import uuid

# create audio file
def create_audio_file(script: str):
    tts = gTTS(text=script, lang="en", tld='co.in')
    unique_num = uuid.uuid4()
    audio_file_path = f"./resources/audios/audio_{unique_num}.mp3"
    
    tts.save(audio_file_path)
    
    return True, unique_num, audio_file_path
