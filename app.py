import streamlit as st
from txtai.pipeline import Summary,Textractor
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

st.set_page_config(layout="wide")

# Load environment variables
load_dotenv()

# Configure Google Gemini Pro
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt="""You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

# Function to summarize text using txtai
#@st.cache(allow_output_mutation=True)
@st.cache_resource
def text_summary(text, maxlength=None):
    summary = Summary()
    text = (text)
    result = summary(text)
    return result

# Function to extract text from a PDF document
def extract_text_from_pdf(file_path):
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        page = reader.pages[0]
        text = page.extract_text()
    return text

# Function to extract transcript details from a YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e

# Function to generate detailed notes from transcript text using Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt+transcript_text)
    return response.text

# Sidebar with choices
choice = st.sidebar.selectbox("Select your choice", ["Summarize Text", "Summarize Document", "Summarize YouTube Video"])

# Summarize Text
if choice == "Summarize Text":
    st.subheader("Summarize Text using txtai")
    input_text = st.text_area("Enter your text here")
    if input_text is not None:
        if st.button("Summarize Text"):
             col1, col2 = st.columns([1,1])
             with col1:
                st.markdown("**Your Input Text**")
                st.info(input_text)
             with col2:
                st.markdown("**Summary Result**")
                result = text_summary(input_text)
                st.success(result)


# Summarize Document
elif choice == "Summarize Document":
    st.subheader("Summarize Document using txtai")
    input_file = st.file_uploader("Upload your document here", type=['pdf'])
    if input_file is not None:
        if st.button("Summarize Document"):
            with open("doc_file.pdf", "wb") as f:
                f.write(input_file.getbuffer())
            col1, col2 = st.columns([1,1])
            with col1:
                st.info("File uploaded successfully")
                extracted_text = extract_text_from_pdf("doc_file.pdf")
                st.markdown("**Extracted Text is Below:**")
                st.info(extracted_text)
            with col2:
                st.markdown("**Summary Result**")
                text = extract_text_from_pdf("doc_file.pdf")
                doc_summary = text_summary(text)
                st.success(doc_summary)
                
# Summarize YouTube Video
elif choice == "Summarize YouTube Video":
    st.subheader("Summarize YouTube Video using Google Gemini Pro")
    youtube_link = st.text_input("Enter YouTube Video Link:")
    if youtube_link:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    if st.button("Get Detailed Notes"):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            summary = generate_gemini_content(transcript_text,prompt)
            st.markdown("## Detailed Notes:")
            st.write(summary)
