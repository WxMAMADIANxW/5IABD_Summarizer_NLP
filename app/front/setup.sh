#!/usr/bin/env bash

# Make sure to have an AWS CentOS Distribution before executing this script
sudo yum install curl git python3-pip -y
git clone https://github.com/WxMAMADIANxW/5IABD_Summarizer_NLP
cd 5IABD_Summarizer_NLP/app/front; pip3 install -r requirements.txt
streamlit run main.py
