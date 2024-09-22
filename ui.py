import os
import streamlit as st
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_host = "localhost"  # Change to "localhost" when running locally
api_port = int(os.environ.get("PORT", "8080"))

# Streamlit UI elements
st.title("InternationalNews Alerts")

question = st.text_input(
    "Which News Alerts are required:",
    placeholder="Please tell what data are you interested in?"
)

if question:
    url = f'http://{api_host}:{api_port}/'  # Ensure this matches your API endpoint
    data = {"query": question}

    response = requests.post(url, json=data)  # Send the question to the API

    if response.status_code == 200:
        st.write("### Answer")
        st.write(response.json())  # Display the response from the API
    else:
        st.error(f"Failed to send data to Pathway API. Status code: {response.status_code}")
