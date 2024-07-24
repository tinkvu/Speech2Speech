import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings
from groq import Groq
from gtts import gTTS
from IPython.display import Audio, display
import os
import time
import numpy as np
import av

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

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = b""

    def recv_audio(self, frames: av.AudioFrame):
        self.buffer += frames.to_ndarray().tobytes()
        return frames

st.title("Voice Chatbot")
st.write("Record your voice and have a conversation with the chatbot.")

if 'conversation' not in st.session_state:
    st.session_state.conversation = chat_history

webrtc_ctx = webrtc_streamer(
    key="key",
    client_settings=ClientSettings(
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"audio": True, "video": False},
    ),
    audio_processor_factory=AudioProcessor,
)

if webrtc_ctx.audio_processor:
    audio_data = webrtc_ctx.audio_processor.buffer
    if audio_data:
        # Save the audio file
        filename = "user_input.wav"
        with open(filename, "wb") as f:
            f.write(audio_data)
        
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
