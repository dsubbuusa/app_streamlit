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


def get_response_from_groq(message):
    prompt = """
    Act as a customer service relationship manager. You are working in a company TeleTek, which sell television across the world. You have to solve the problem customer faces making sure each and every query is address properly. You have to follow the below guidelines for answering all the queries.
    Guidelines
    1. You cannot be offensive while answering
    2. If the customer is unhappy with the service ask him reason in detail and then try to pacify the customer that team will work on it to provide resolution
    3. If the query is related to replacement, tell the customer polietly that we do not take any replacement but can help him to fix the issue
    4. Do not answer to anything other than your domain
    """
    
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages = [
            {"role" : "system", "content" : prompt},
            {"role" : "user", "content" : message}
        ],
        temperature=0
    )

    return response.choices[0].message.content


def main():
    # question = input("Enter your query: ")
    # res = get_response_from_groq(question)
    # print(res)

    st.title("Welcome to TeleTek Corporation")
    st.subheader("We sell :blue[Televisions]",  divider=True)
    question = st.chat_input(placeholder="Enter your query")
    if question:
        res = get_response_from_groq(question)
        st.write(res)

main()
# to run steamlit
#streamlit run streamlitapp.py