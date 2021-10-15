### This is a sample prototype of chat application which I have built for UTD OIT Help Desk

```
Server Details:
Asynchronous request handling Websocket server deployed behind Supervisord deployed on EC2 machine
Websocker Server is listening at port 7890

```

```
Tech Stack Involved

AWS EC2 Machine - t2.micro
Distributed Redis Clusters hosted on AWS
Apache Solr Search Engine Cluster
Redis Queues

```

### Working Modes
```
This chat system is designed to work in three modes:
1. For chatting with designated OIT help desh representatives
2. In automated text response mode
3. Generically broadcast messaging mode

```

### Working Mode Execution Details

# For chatting with designated OIT help desh representatives:

```
Requirements:
Postman App to make Websocket calls to hosted server
```


### Sample Executions Between Two Designated People (Servers)

## Person 1 - Karthik Ragunath Ananda Kumar
![alt text](https://drive.google.com/file/d/1TZJ_3qQeseDXiKwDtl52yK97iBOZXHD7/view?usp=sharing)


## Person 2 - Ananda Kumar
![alt text](https://drive.google.com/file/d/1euPaW2xRzPD2z0tkER5dcCcLPzQ4Qmqk/view?usp=sharing)


## Person 3 - Dhivya Nandhini
![alt text](https://drive.google.com/file/d/1TgVrzCcrtXzheJBUq0QVB-hA8f4waDqM/view?usp=sharing)


## Server 1

```

karthik_ragunath@Karthiks-MacBook-Pro ~ % python3 -m websockets ws://34.201.250.165:7890/
Connected to ws://34.201.250.165:7890/.
> {"register": true, "device_name": "Karthik Ragunath"}
< Device Successfully Registered. Note down your api_key: mCWtZJUic1Sj8JYK
> {"auth_key":"mCWtZJUic1Sj8JYK", "to_id": "Ananda Kumar", "message": "Hello there!!! Hope you are doing?!!!"}
< Ananda Kumar is not online yet
< Message: Hello there!!! Hope you are doing?!!! delivered to Ananda Kumar
< Message: Hello there!!! Hope you are doing?!!! delivered to Ananda Kumar
< Message from Ananda Kumar: I am doing fine. How about you???
> {"auth_key":"mCWtZJUic1Sj8JYK", "to_id": "Ananda Kumar", "message": "I am doing fine too. Thanks for asking!!!"}
> {"disconnect": true, "auth_key":"mCWtZJUic1Sj8JYK"}
> {"register": true, "device_name": "Karthik Ragunath"}
< Device Successfully Registered. Note down your api_key: qDlzcMSB3z5avAqI
< Message from Ananda Kumar: Howz UTD???

```

## Server 2

```
karthik_ragunath@Karthiks-MacBook-Pro ~ % python3 -m websockets ws://34.201.250.165:7890/
Connected to ws://34.201.250.165:7890/.
> {"register": true, "device_name": "Ananda Kumar"}
< Device Successfully Registered. Note down your api_key: iljEUkqklOuKae5c
< Message from Karthik Ragunath: Hello there!!! Hope you are doing?!!!
> {"auth_key":"iljEUkqklOuKae5c", "to_id": "Karthik Ragunath", "message": "I am doing fine. How about you???"}
< Message from Karthik Ragunath: I am doing fine too. Thanks for asking!!!
> {"auth_key":"iljEUkqklOuKae5c", "to_id": "Karthik Ragunath", "message": "Howz UTD???"}
< Karthik Ragunath is not online yet
< Message: Howz UTD??? delivered to Karthik Ragunath

```

### Sample Execution Automated Message Response Mode (Implmented with Apache Solr Search Engine hosted at 54.227.45.228)

## Client Server ()

```
karthik_ragunath@Karthiks-MacBook-Pro ~ % python3 -m websockets ws://34.201.250.165:7890/
Connected to ws://34.201.250.165:7890/.
> {"register": true, "device_name": "Karthik Ragunath"}
< Device Successfully Registered. Note down your api_key: FUCg6guD0l8jRfJH
> {"question": "oit-help-desk website", "auth_key":"FUCg6guD0l8jRfJH"}
< For link, refer http link attached in this document. Feel free to chat to us https://oit.utdallas.edu/helpdesk/
> {"question": "oit-help-desk on-campus location", "auth_key":"FUCg6guD0l8jRfJH"}
< For link, refer http link attached in this document. Feel free to chat to us https://oit.utdallas.edu/helpdesk/
> {"question": "on-campus location", "auth_key":"FUCg6guD0l8jRfJH"}
< It is located in SSB building opposite to Eugene McDermott Library. For map link, refer http link attached in this document https://map.concept3d.com/?id=1772#!sbc/?bm/?ct/42147
>

```


```
(venv) ubuntu@ip-172-31-87-206:~/oit-chat-search$ python ./server.py
Server listening on port: 7890
A client just connected
Message Info: {'is_valid': True, 'register': True, 'device_mapping': 'Karthik Ragunath', 'auth_key': 'FUCg6guD0l8jRfJH', 'auth_hash': 'jEPm0F4HrtoprnPRhdr8iSdcVX4kPgup'}
Message Info: {'is_valid': True, 'auth_key': 'FUCg6guD0l8jRfJH', 'auth_hash': 'jEPm0F4HrtoprnPRhdr8iSdcVX4kPgup', 'device_mapping': 'Karthik Ragunath', 'from_id': 'Karthik Ragunath', 'question': 'oit-help
-desk website'}
fq_query: question:oit-help-desk website
Top Result: {'id': '1', 'question': 'what is the website link for oit-help-desk?', 'answer': 'For link, refer http link attached in this document. Feel free to chat to us', 'http_link': 'https://oit.utdal
las.edu/helpdesk/', '_version_': 1713618829906542592}
Message Info: {'is_valid': True, 'auth_key': 'FUCg6guD0l8jRfJH', 'auth_hash': 'jEPm0F4HrtoprnPRhdr8iSdcVX4kPgup', 'device_mapping': 'Karthik Ragunath', 'from_id': 'Karthik Ragunath', 'question': 'oit-help
-desk on-campus location'}
fq_query: question:oit-help-desk on-campus location
Top Result: {'id': '1', 'question': 'what is the website link for oit-help-desk?', 'answer': 'For link, refer http link attached in this document. Feel free to chat to us', 'http_link': 'https://oit.utdal
las.edu/helpdesk/', '_version_': 1713618829906542592}
Message Info: {'is_valid': True, 'auth_key': 'FUCg6guD0l8jRfJH', 'auth_hash': 'jEPm0F4HrtoprnPRhdr8iSdcVX4kPgup', 'device_mapping': 'Karthik Ragunath', 'from_id': 'Karthik Ragunath', 'question': 'on-campu
s location'}
fq_query: question:on-campus location
Top Result: {'id': '2', 'question': 'where is the oit-help-desk located on-campus?', 'answer': 'It is located in SSB building opposite to Eugene McDermott Library. For map link, refer http link attached i
n this document', 'http_link': 'https://map.concept3d.com/?id=1772#!sbc/?bm/?ct/42147', '_version_': 1713619015365033984}
```