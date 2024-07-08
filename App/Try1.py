import streamlit as st
from pydub import AudioSegment
from gtts import gTTS
import tempfile
import base64
import os
import google.generativeai as ggi
from dotenv import load_dotenv
import whisper

# Load environment variables
load_dotenv(".env")

fetched_api_key = os.getenv("API_KEY")
ggi.configure(api_key="AIzaSyCiVJZmXhOOc-SrwKx4KH6JXONvFEhMbnA")

model = ggi.GenerativeModel("gemini-pro")
chat = model.start_chat()

# Function to get LLM response
def LLM_Response(question):
    response = chat.send_message(question, stream=True)
    return response

# Function to transcribe audio
def transcribe_audio(file_path):
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

# Custom component for recording audio
def audio_recorder():
    st.markdown(
        """
        <h3>Record your voice:</h3>
        <button onclick="startRecording()">Start Recording</button>
        <button onclick="stopRecording()">Stop Recording</button>
        <p id="status"></p>
        <audio id="recordedAudio" controls></audio>
        <script>
            let mediaRecorder;
            let audioChunks = [];

            function startRecording() {
                document.getElementById("status").innerText = "Recording...";
                navigator.mediaDevices.getUserMedia({ audio: true })
                    .then(stream => {
                        mediaRecorder = new MediaRecorder(stream);
                        mediaRecorder.start();
                        mediaRecorder.ondataavailable = event => {
                            audioChunks.push(event.data);
                        };
                        mediaRecorder.onstop = () => {
                            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                            const audioUrl = URL.createObjectURL(audioBlob);
                            const audio = document.getElementById("recordedAudio");
                            audio.src = audioUrl;
                            audioChunks = [];
                            const reader = new FileReader();
                            reader.onload = function() {
                                const base64String = reader.result.replace("data:", "").replace(/^.+,/, "");
                                fetch('/upload-audio', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({ audio: base64String })
                                }).then(response => response.json())
                                  .then(data => {
                                      console.log(data);
                                  });
                            };
                            reader.readAsDataURL(audioBlob);
                        };
                    });
            }

            function stopRecording() {
                mediaRecorder.stop();
                document.getElementById("status").innerText = "Recording stopped.";
            }
        </script>
        """, unsafe_allow_html=True
    )

def main():
    st.title("Voice Chat App")

    # Include the audio recorder component
    audio_recorder()

    # Placeholder to upload audio
    audio_base64 = st.text_area("Upload Audio Base64 Here:")

    if audio_base64:
        st.session_state.audio_uploaded = True
        audio_data = audio_base64.split(",")[1]
        audio_path = "input_audio.wav"
        with open(audio_path, "wb") as f:
            f.write(base64.b64decode(audio_data))

        st.write("Processing audio...")
        
        # Transcribe audio
        transcribed_text = transcribe_audio(audio_path)
        st.write(f"Transcribed Text: {transcribed_text}")

        # Generate response using Google Gemini
        response = LLM_Response(transcribed_text)
        response_text = response  # Adjust based on actual response format

        # Generate audio response using gTTS
        tts = gTTS(text=response_text, lang='en')
        tts.save("response.mp3")

        # Play response audio
        st.audio("response.mp3", format='audio/mp3')

if __name__ == "__main__":
    main()
