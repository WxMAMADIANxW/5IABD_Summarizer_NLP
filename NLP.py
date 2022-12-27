import youtube_dl
from pytube import YouTube as yt
import whisper
import torch
from transformers import pipeline
from docx import Document
from fpdf import FPDF
from fastapi import FastAPI





##Pytube

def py_tube(link):
    audio = yt(link).streams.filter(only_audio=True).all()
    return audio[0].download("/content/mp3")



##Whisper

def whisper_process(filename):
    WhispBase = whisper.load_model('base')
    Text = WhispBase.transcribe(filename,  fp16=False)
    return Text['text']



##HuggingFace

def hugging_face(Text_to_summarize):
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

    result = summarizer(Text_to_summarize, **params)
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
