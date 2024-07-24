import streamlit as st
from audiorecorder import audiorecorder
from groq import Groq
from gtts import gTTS
from IPython.display import Audio, display
import time
import os

# Initialize Groq client
client = Groq(api_key="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")

# Initialize chat history
chat_history = [
    {
        "role": "system",
        "content": "You are an English trainer. Your job is to keep communicating with the user and make them speak a lot. Using the chat history, chat and help improve their communication."
    }
]

def transcribe_audio(filename):
    with open(filename, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(filename, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    return transcription["text"]

def play_audio(text):
    tts = gTTS(text)
    audio_file = "assistant_response.mp3"
    tts.save(audio_file)
    display(Audio(audio_file, autoplay=True))
    os.remove(audio_file)

# Streamlit app
st.title("Voice Chatbot")
st.write("Record your voice and have a conversation with the chatbot.")

if 'conversation' not in st.session_state:
    st.session_state.conversation = chat_history

# Record audio
audio = audiorecorder("Click to record", "Recording...")

if len(audio) > 0:
    st.audio(audio.tobytes())
    # Save the audio file
    filename = "user_input.mp3"
    with open(filename, "wb") as f:
        f.write(audio.tobytes())
    
    # Transcribe audio
    user_input = transcribe_audio(filename)
    st.write(f"You said: {user_input}")
    
    # Append user message to chat history
    st.session_state.conversation.append({
        "role": "user",
        "content": user_input
    })
    
    # Get response from the assistant
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=st.session_state.conversation,
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    
    # Print and store assistant response
    assistant_response = []
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        assistant_response.append(content)
        st.write(content, end="")
    st.write()  # For a new line after the assistant response

    # Combine assistant response into a single string
    assistant_response_text = "".join(assistant_response)

    # Append assistant response to chat history
    st.session_state.conversation.append({
        "role": "assistant",
        "content": assistant_response_text
    })

    # Play the assistant response
    play_audio(assistant_response_text)
    
    # Wait for the audio to finish playing before asking for user input again
    #time.sleep(5)
