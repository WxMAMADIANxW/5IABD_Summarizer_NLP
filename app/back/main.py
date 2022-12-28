import os
import youtube_dl
from pytube import YouTube as yt
import whisper
import torch
from starlette.responses import JSONResponse
from transformers import pipeline
from docx import Document
from fpdf import FPDF
from fastapi import FastAPI
import uvicorn
import boto3

app = FastAPI()


@app.get("/summarize")
def summarize(link: str):
    audio_path = download_youtube_video_to_mp3(link)
    text = whisper_process(audio_path)
    summary = hugging_face(text)
    txt_to_pdf(summary)
    return JSONResponse(summary)


##Pytube
def download_youtube_video_to_mp3(link: str):
    audio = yt(link).streams.filter(only_audio=True).first()
    video_id = link.split("=")[-1]
    audio.download(f"/tmp/")
    print("audio default filename: ", audio.default_filename)
    os.rename(f"/tmp/{audio.default_filename}", f"/tmp/{video_id}.mp3")
    # Download to S3 bucket
    s3 = boto3.client('s3')
    try:
        s3.upload_file(f"/tmp/{video_id}.mp3", "video-summarizer-bucket", f"audio-{video_id}.mp3")
    except Exception as e:
        raise e
    os.remove(f"/tmp/{video_id}.mp3")
    return f"audio-{video_id}.mp3"


##Whisper
def whisper_process(object_name):
    WhispBase = whisper.load_model('base')
    s3 = boto3.client('s3')
    path = f"/tmp/{object_name}"
    try:
        s3.download_file("video-summarizer-bucket", object_name, path)
    except Exception as e:
        raise e
    text = WhispBase.transcribe(path, fp16=False)
    print(text)
    return text['text']


##HuggingFace
def hugging_face(text_to_summarize):
    summarizer = pipeline(
        "summarization",
        "pszemraj/long-t5-tglobal-base-16384-book-summary",
        device=0 if torch.cuda.is_available() else -1,
    )

    params = {
        "max_length": 1000,
        "min_length": 258,
        "no_repeat_ngram_size": 3,
        "early_stopping": True,
        "repetition_penalty": 3.5,
        "length_penalty": 0.3,
        "encoder_no_repeat_ngram_size": 3,
        "num_beams": 4,
    }

    result = summarizer(text_to_summarize, **params)
    return result[0]["summary_text"]


##FPDF
def txt_to_pdf(text_to_sum):
    pdf = FPDF()
    pdf.set_font("Arial", size=15)
    pdf.add_page()
    pdf.cell(200, 10, txt="Summary : ",
             ln=1, align='C')
    pdf.multi_cell(0, 5, txt=text_to_sum, align='L')

    pdf.output("resume.pdf")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
