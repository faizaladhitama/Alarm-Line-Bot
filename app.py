from multiprocessing import Process, Manager
import time, asyncio
from datetime import datetime as dt, time as t
# encoding: utf-8
import requests
import os
import json
import jsonpickle

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

line_bot_api = LineBotApi('gDlOWWB4P5ipCtw8mQL7ddrrmizXFweCzmJaUQetWyiiDfX8aZI2bT7qpRfovIBEoG8/F62POMjSGkS4MG1jweCKdX1/R30FESvl8OKxLmhO/2i1A/Pa/5TRbEm/O7ek7xo+IW7lhj+dxAvhJD3ZVQdB04t89/1O/w1cDnyilFU=') #Your Channel Access Token
handler = WebhookHandler('193fcdbc69d64b2ef4419c5aa542702c') #Your Channel Secret


m = Manager()
db = m.dict()

def watcher(d):
    while True:
        try:
            for key, value in d.items() :
                future = [date - dt.now() for date in value]
                future.sort()

                if (len(future) > 0 and future[0].total_seconds()) < 0:
                    temp = db[key]
                    item = temp.pop(0)                          
                    db[key] = temp
                    print("Alarm menyala")
                    line_bot_api.push_message(key, TextSendMessage(text='Alarm menyala !'))
        except Exception as e:
            print(e)
        time.sleep(3)


p = Process(name='p1', target=watcher, args=(db, ))
p.start()

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#User send text
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text #message from user
    reply = ""
    print(event)
    print(event.message)
    print(event.source)
    print(event.source['userId'])
    inp = text.split(" ")   
    inp.insert(0,event.source.userId)
    print(inp)    
    try:
        time_set = None
        in_length = len(inp)
        if in_length == 2:
            inp_time = inp[1].split(":")
            try:
                hour = int(inp_time[0])
                minute = 0
                if len(inp_time) == 2:         
                    minute=int(inp_time[1])
                time_set = dt.now().replace(hour=hour,minute=minute,second=0)
                reply = "Alarm telah berhasil di set"
            except Exception:
                reply = "Jam hanya bisa dari 00-23 dan menit hanya bisa dari 00-59"
        elif in_length == 3:
            inp_date = inp[1].split("-")
            inp_time = inp[2].split(":")
            try:
                day = int(inp_date[0])
                month = int(inp_date[1])
                year = int(inp_date[2])
                hour = int(inp_time[0])
                minute = 0
                if len(inp_time) == 2:         
                    minute=int(inp_time[1])
                time_set = dt(year=year,month=month,day=day,hour=hour,minute=minute)
            except Exception:
                reply = "Format waktunya dd-mm-yyy, jam hanya bisa dari 00-23, dan menit hanya bisa dari 00-59"
        else:
            reply = "Kurang tanggal dan/ jam"
        
        if time_set is not None:    
            try:
                db[inp[0]]
            except:
                db[inp[0]] = []
            if (time_set - dt.now()).total_seconds() > 0:
                db[inp[0]] = db[inp[0]] + [time_set]
                reply = "Alarm telah berhasil di set"            
            else:
                reply = "Alarm tidak berhasil di set karena waktu nya lampau"
    except ValueError:
        reply = "Jam hanya bisa dari 00-23 dan menit hanya bisa dari 00-59"
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=reply),timeout=10) #reply the same message from user

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)  
