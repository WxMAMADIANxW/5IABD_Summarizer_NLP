import requests
import streamlit

# Create a Streamlit app with a title, an input box, and a button
streamlit.title("Video summarizer")
link = streamlit.text_input("Enter a YouTube link")
button = streamlit.button("Summarize")

if button:
    # When the button is clicked, download the video from the link
    streamlit.write("Downloading video...")
    # Call to EC2 instance
    response = requests.get("http://ec2-3-15-206-10.us-east-2.compute.amazonaws.com:5000/summarize",
                            params={"link": link})
    # Display the summary
    streamlit.write("The summary of the video : ", response.text)

