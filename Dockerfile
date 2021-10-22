# syntax=docker/dockerfile:1
FROM python:3.9-alpine
RUN git clone https://github.com/Karthik-Ragunath/OIT-chat-model.git && cd OIT-chat-model
RUN pip install -r requirements.txt
CMD ["python3", "-m", "websockets", "ws://34.201.250.165:7890/"]