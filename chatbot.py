import os

from openai import OpenAI
import streamlit as st
import base64


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


@st.cache_resource
def set_logo_urls():
    user_logo_path = "3apChatLogo.png"
    user_logo_base64 = image_to_base64(user_logo_path)
    user_logo_url = f"data:image/png;base64,{user_logo_base64}"

    assistant_logo_path = "CSSChatLogo.png"
    assistant_logo_base64 = image_to_base64(assistant_logo_path)
    assistant_logo_url = f"data:image/png;base64,{assistant_logo_base64}"

    return user_logo_url, assistant_logo_url


@st.cache_resource
def init_assistant():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    assistant = client.beta.assistants.retrieve("asst_AjG7NaW5wpJruPAwNqIk5YqE")
    thread = client.beta.threads.create()
    return client, assistant, thread


if __name__ == '__main__':

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400&display=swap');
        .header {
            display: flex;
            align-items: center;
            background-color: white;
            justify-content: space-between;
            font-family: 'Open Sans', sans-serif;
            margin-bottom: 20px;
        }
        .header img {
            height: 70px;
        }
        .header h1 {
            font-size: 28px;
            margin: 0;
            color: #00327E;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="header">
            <img src="https://bioalps.org/app/uploads/2023/02/CSS-Logo-ohne-Claim.jpg" alt="Logo">
            <h1>Chatbot Assistant</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    with open("style.css" ) as css:
        st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

    client, assistant, thread = init_assistant()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    user_logo_url, assistant_logo_url = set_logo_urls()

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=user_logo_url if message["role"] == "user" else assistant_logo_url):
            st.markdown(message["content"])

    if prompt := st.chat_input("Message here"):

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar=user_logo_url):
            st.markdown(prompt)

        spinner_placeholder = st.empty()
        with spinner_placeholder.container():
            with st.chat_message("assistant", avatar=assistant_logo_url):
                st.markdown("""
                <span style="opacity: 0.7;">*Typing...*</span>
                """, unsafe_allow_html=True)
                client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=prompt,
                )

                run = client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id, assistant_id=assistant.id
                )

                messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
                message = messages[0].content[-1].text.value
        spinner_placeholder.empty()

        with st.chat_message("assistant", avatar=assistant_logo_url):
            st.markdown(message)

        st.session_state.messages.append({"role": "assistant", "content": message})
