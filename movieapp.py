import os
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
import streamlit as st


load_dotenv()

chosen_llm = "groq"

if chosen_llm == 'groq':
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
else:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = """
I am looking for some great movie recommendations! Please suggest a few films based on the following preferences:

Genre: Action, Comedy, Drama, Sci-Fi, Horror, Romance, Thriller
Mood: Lighthearted, Intense, Inspirational, Dark, Suspenseful
Era: Classic, 90s, 2000s, 2010s, or more recent
Favorite Films/Directors/Actors: Steven Spielberg,Martin Scorsese,Christopher Nolan,Stanley Kubrick,Alfred Hitchcock,Quentin Tarantino,Francis Ford Coppola,Akira Kurosawa,Billy Wilder,Peter Jackson,Robert De Niro,Daniel Day-Lewis,Jack Nicholson,Marlon Brando,Tom Hanks,Leonardo DiCaprio,Al Pacino,Denzel Washington,Anthony Hopkins,Humphrey Bogart
Type of Experience: Thought-provoking, Visually stunning, Heartwarming, or Action-packed
Language: English, Bollywood, Telugu
Please give me a mix of well-known masterpieces and hidden gems!
"""

st.title("Welcome to Movie Recomendations")
st.subheader(":blue[English, Bollywood, Telugu ]",  divider=True)

if "conversations" not in st.session_state:
    st.session_state.conversations = [{"role" : "system", "content" : prompt}]

for conversation in st.session_state.conversations[1:]:
    st.chat_message(conversation["role"]).write(conversation["content"])

def get_response_from_groq():
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages = st.session_state.conversations,
        temperature=0
    )

    return response.choices[0].message.content


def chat_history(role, message):
    st.session_state.conversations.append({"role" : role, "content": message})


def main():
    question = st.chat_input(placeholder="Enter your query")
    if question:
        st.chat_message("user").write(question)
        chat_history("user", question)
        res = get_response_from_groq()
        chat_history("assistant", res)
        st.chat_message("assistant").write(res)

main()