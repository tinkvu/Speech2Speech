import streamlit as st
from audiorecorder import audiorecorder
from gtts import gTTS
import os
import time
from io import BytesIO
import requests

# Initialize Groq client
class Groq:
    def __init__(self, api_key):
        self.api_key = api_key

    def audio_transcriptions_create(self, file, model, response_format):
        # Mock implementation for the transcription API call
        # Replace this with the actual API call to Groq
        return {"text": "Transcribed text from audio"}

    def chat_completions_create(self, model, messages, temperature, max_tokens, top_p, stream, stop):
        # Mock implementation for the chat completion API call
        # Replace this with the actual API call to Groq
        class MockCompletion:
            def __init__(self):
                self.choices = [type('Choice', (object,), {'delta': type('Delta', (object,), {'content': 'This is a response.'})()})]

        return iter([MockCompletion()])

client = Groq(api_key="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")

# Initialize chat history
if 'conversation' not in st.session_state:
    st.session_state.conversation = [
        {
            "role": "system",
            "content": "You are an English trainer. Your job is to keep communicating with the user and make them speak a lot. Using the chat history, chat and help improve their communication."
        }
    ]

def transcribe_audio(audio_bytes):
    # Replace this mock implementation with actual API call
    # Use BytesIO to handle audio bytes directly
    with BytesIO(audio_bytes) as audio_file:
        transcription = client.audio_transcriptions_create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="verbose_json",
        )
    return transcription["text"]

def play_audio(text):
    tts = gTTS(text)
    audio_file = "assistant_response.mp3"
    tts.save(audio_file)
    st.audio(audio_file, format='audio/mp3')
    os.remove(audio_file)

st.title("Voice Chatbot")
st.write("Record your voice and have a conversation with the chatbot.")

audio_bytes = audiorecorder("Click to record", "Recording...")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    # Transcribe audio
    user_input = transcribe_audio(audio_bytes)
    st.write(f"You said: {user_input}")
    
    # Append user message to chat history
    st.session_state.conversation.append({
        "role": "user",
        "content": user_input
    })
    
    # Get response from the assistant
    completion = client.chat_completions_create(
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
    
