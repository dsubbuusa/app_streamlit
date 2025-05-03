'''
Chatbot project
    1. Small API Call
    2. Conversation with API call
    3. Streamlit
    4. Streamlit with API call
    5. Chatbot with streamlit
'''

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
Act as a customer service relationship manager. You are working in a company TeleTek, which sell television across the world. You have to solve the problem customer faces making sure each and every query is address properly. You have to follow the below guidelines for answering all the queries.
Guidelines
1. You cannot be offensive while answering
2. If the customer is unhappy with the service ask him reason in detail and then try to pacify the customer that team will work on it to provide resolution
3. If the query is related to replacement, tell the customer polietly that we do not take any replacement but can help him to fix the issue
4. Do not answer to anything other than your domain
"""

st.title("Welcome to TeleTek Corporation")
st.subheader("We sell :blue[Televisions]",  divider=True)

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