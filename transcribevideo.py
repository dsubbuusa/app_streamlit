from openai import OpenAI
import yt_dlp
import speech_recognition as sr
import os
from pydub import AudioSegment
import streamlit as st
from groq import Groq
import whisper

# Initialize OpenAI client (new API)
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # or hardcode if preferred

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        # Construct the expected mp3 filename
        mp3_filename = 'downloaded_audio.mp3'
        return mp3_filename

# Convert audio to wav for better transcription compatibility
def convert_to_wav(mp3_filename):
    sound = AudioSegment.from_mp3(mp3_filename)
    wav_filename = mp3_filename.replace('.mp3', '.wav')
    sound.export(wav_filename, format="wav")
    return wav_filename

# Transcribe audio to text
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

# Use OpenAI GPT to answer a question based on the transcription
def answer_question_gpt(context, conversation_history, question):
    messages = []

    # Add system context
    messages.append({
        "role": "system",
        "content": "You are a helpful assistant answering questions based on a transcript."
    })

    # Add full context from the transcript
    messages.append({
        "role": "user",
        "content": f"Context: {context}"
    })

    # Add previous Q&A
    for q, a in conversation_history:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})

    # Add the new question
    messages.append({"role": "user", "content": question})

    # Call GPT-4 or GPT-3.5
    response = client.chat.completions.create(
        model="gemma2-9b-it",  # or "gpt-3.5-turbo"
        messages=messages,
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()

# ---------- Streamlit App ----------

def main():
    st.title("🎙️ YouTube Video Transcription + GPT Q&A")

    # --- Session State Init ---
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    if 'transcription' not in st.session_state:
        st.session_state.transcription = ""

    if 'video_url' not in st.session_state:
        st.session_state.video_url = ""

    st.markdown("Paste a YouTube URL, get transcript and ask questions!")

    youtube_url = st.text_input("YouTube URL")

    if youtube_url and youtube_url != st.session_state.video_url:
        st.session_state.video_url = youtube_url

        with st.spinner("🔊 Downloading and transcribing..."):
            audio_file = download_audio(youtube_url)
            wav_file = convert_to_wav(audio_file)
            transcription = transcribe_audio(wav_file)

            # Save to session
            st.session_state.transcription = transcription

            # Clean up
            os.remove(audio_file)
            os.remove(wav_file)

            # Clear previous chat
            st.session_state.conversation_history = []

    # Show transcription
    if st.session_state.transcription:
        st.subheader("📝 Transcription")
        st.text_area("Transcribed Text", st.session_state.transcription, height=300)

        st.subheader("💬 Ask a Question")

        latest_answer = None  # Placeholder for latest answer

        with st.form("question_form", clear_on_submit=True):
            user_question = st.text_input("Your Question")
            submitted = st.form_submit_button("Submit Question")

            if submitted and user_question.strip():
                with st.spinner("🤖 Thinking..."):
                    answer = answer_question_gpt(
                        st.session_state.transcription,
                        st.session_state.conversation_history,
                        user_question.strip()
                    )
                    # Store only in memory, not shown to user
                    st.session_state.conversation_history.append((user_question.strip(), answer))
                    latest_answer = answer

        # Display only the latest answer (after submit)
        if latest_answer:
            st.markdown("### 🧠 GPT Answer")
            st.write(latest_answer)


        # st.subheader("💬 Ask a Question")

        # # --- Input form ---
        # with st.form("question_form", clear_on_submit=True):
        #     user_question = st.text_input("Your Question")
        #     submitted = st.form_submit_button("Submit Question")

        #     if submitted and user_question.strip():
        #         with st.spinner("🤖 Thinking..."):
        #             answer = answer_question_gpt(
        #                 st.session_state.transcription,
        #                 st.session_state.conversation_history,
        #                 user_question.strip()
        #             )
        #             st.session_state.conversation_history.append((user_question.strip(), answer))

        # # Show chat history
        # if st.session_state.conversation_history:
        #     st.subheader("🧠 Q&A History")
        #     for i, (q, a) in enumerate(st.session_state.conversation_history):
        #         st.markdown(f"**Q{i+1}: {q}**")
        #         st.markdown(f"**A{i+1}:** {a}")

if __name__ == "__main__":
    main()