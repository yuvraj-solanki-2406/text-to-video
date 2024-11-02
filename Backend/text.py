import google.generativeai as genai
import dotenv
import os
import re

GOOGLE_API = os.environ.get("GEMINI_KEY")

genai.configure(api_key=GOOGLE_API)

# preprocess text
def preprocess_text(text: str):
    text = text.replace("*", "").replace("#", "")
    text = re.sub(r"\[.*\]", "", text)
    text = re.sub(r"\(.*\)", "", text)

    return text

def generate_textual_content(user_input):
    model = genai.GenerativeModel(model_name="gemini-pro")
    
    prompt = f"""
        create a script for a short video on the topic {user_input} the script must be engaging
        and directly to the point do not include any unnecessary things like, "welcome to this video".
        The script should be related to {user_input}.
        
        You must not include any type of markdown or formatting in the script, never use a title.
        Only return the raw content of the script. 
        Do not include "voiceover", "narrator" or similar indicators of what should be spoken at the 
        beginning of each paragraph or line.
        You must not mention the prompt, or anything about the script itself. 
        also, never talk about the amount of paragraphs or lines. just write the script.
    """
    
    script = model.generate_content(prompt).text
    script = preprocess_text(text=script)
    return script
    

# find meaningful word
def find_query_word(script: str, amount: int):
    model = genai.GenerativeModel("gemini-pro")
    
    prompt = f"""
        Generate {amount} search terms for stock videos, depending contect of {script} of a video.
        The search terms are to be returned as a JSON-Array of strings.
        Each search term should consist of 1-3 words, always add the main subject of the video.
        
        YOU MUST ONLY RETURN THE JSON-ARRAY OF STRINGS.
        YOU MUST NOT RETURN ANYTHING ELSE. 
        YOU MUST NOT RETURN THE SCRIPT.
        
        The search terms must be related to the subject of the video.
        Here is an example of a JSON-Array of strings:
        ["search term 1", "search term 2", "search term 3"]

        For context, here is the full text:
        {script}
    """
    response = model.generate_content(prompt).text
    
    
    return response

