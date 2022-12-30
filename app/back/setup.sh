#!/usr/bin/env bash

# Make sure to have an AWS CentOS Distribution before executing this script
sudo yum install curl git python3-pip -y
git clone https://github.com/WxMAMADIANxW/5IABD_Summarizer_NLP

# Install ffmpeg
cd /usr/local/bin
sudo mkdir ffmpeg

cd ffmpeg
sudo wget https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-4.2.1-amd64-static.tar.xz
sudo tar xvf ffmpeg-4.2.1-amd64-static.tar.xz
sudo mv ffmpeg-4.2.1-amd64-static/ffmpeg .

sudo ln -s /usr/local/bin/ffmpeg/ffmpeg /usr/bin/ffmpeg

cd ~/5IABD_Summarizer_NLP/app/back; pip3 install -r requirements.txt

# Configure AWS CLI
aws configure
# Put your AWS credentials in the prompt

python3 main.py
