import os

import requests
import streamlit


BACKEND_URL = os.environ["BACKEND_URL"]

# Create a Streamlit app with a title, an input box, and a button
streamlit.title("Video summarizer")
link = streamlit.text_input("Enter a YouTube link")
button = streamlit.button("Summarize")

if button:
    # When the button is clicked, download the video from the link
    streamlit.write("Preparing the summary...")
    streamlit.write("This may take a few minutes... Please be patient.")
    # Call to EC2 instance
    response = requests.get(f"http://{BACKEND_URL}:5000/summarize?"
                            f"link={link}")
    # Display the summary
    streamlit.write("The summary of the video : \n", response.text)

