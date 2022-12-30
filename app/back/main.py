import os
from pytube import YouTube as yt
import whisper
import torch
from starlette.responses import JSONResponse
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from fastapi import FastAPI
import uvicorn
import boto3

app = FastAPI()


@app.get("/summarize")
def index(link: str):
    audio_path = download_youtube_video_to_mp3(link)
    text = convert_speech_to_text(audio_path)
    summary = summarize(text)
    return JSONResponse(summary)


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
    print("file uploaded")
    os.remove(f"/tmp/{video_id}.mp3")
    return f"audio-{video_id}.mp3"


def convert_speech_to_text(object_name):
    WhispBase = whisper.load_model('base')
    s3 = boto3.client('s3')
    path = f"/tmp/{object_name}"
    try:
        s3.download_file("video-summarizer-bucket", object_name, path)
    except Exception as e:
        raise e
    print("file downloaded")
    text = WhispBase.transcribe(path, fp16=False)
    print("text:", text)
    return text['text']


def summarize(text_to_summarize):
    tokenizer = AutoTokenizer.from_pretrained("ccdv/lsg-bart-base-4096-booksum",
                                              trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained("ccdv/lsg-bart-base-4096-booksum",
                                                  trust_remote_code=True)
    pipe = pipeline("text2text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if torch.cuda.is_available() else -1)

    params = {
        "truncation": True,
        "max_length": 450,
        "no_repeat_ngram_size": 3,
        "num_beams": 4,
        "early_stopping": True
    }  # parameters for text generation out of model

    generated_text = pipe(text_to_summarize, **params)
    return generated_text[0]["generated_text"]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
