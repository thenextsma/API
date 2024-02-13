import streamlit as st
import requests

TOGETHER_API_KEY = ""
TOGETHER_API_BASE = "https://api.together.xyz/v1/chat/completions"

def post_chat_completion(model: str, user_input: str) -> str:
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOGETHER_API_KEY}',
    }

    data = {
        'model': model,
        'max_tokens': 512,
        'stop': [" ", "[/"],
        'temperature': 0.7,
        'top_p': 0.7,
        'top_k': 50,
        'repetition_penalty': 1.5,  # Adjust repetition penalty
        'n': 1,
        'messages': [
            {
                'role': 'user',
                'content': user_input,
            }
        ],
    }

    response = requests.post(f"{TOGETHER_API_BASE}", headers=headers, json=data)

    if response.status_code == 200:
        output = response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        if output:
            return output
    else:
        st.error(f"Error: {response.status_code}, {response.text}")
        return None

def main():
    st.set_page_config(page_title="My Streamlit App", page_icon=":robot:", layout="centered")
    st.title("Chat Completion with Together API")

    st.subheader("Generative AI")
    user_input = st.text_input("",placeholder="Ask me anything..")

    if st.button("Enter",type="primary",use_container_width=True):
        if user_input:
            completion = post_chat_completion(model='mistralai/Mixtral-8x7B-Instruct-v0.1', user_input=user_input)
            if completion:
                st.write("", completion)
            else:
                st.error("Failed to get a response from the Together API.")

if __name__ == "__main__":
    main()

    

