# syntax=docker/dockerfile:1
FROM python:3.9-alpine
RUN apk update && apk add git
WORKDIR /home/ubuntu/
RUN git clone https://github.com/Karthik-Ragunath/OIT-chat-model.git /home/ubuntu/OIT-chat-model
COPY . .
RUN cd /home/ubuntu/OIT-chat-model/
WORKDIR /home/ubuntu/OIT-chat-model/
RUN pip install -r requirements.txt
CMD ["python3", "./server.py"]
