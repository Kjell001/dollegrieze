#!/usr/bin/env python3

import os
import tweepy
from datetime import datetime, timedelta
from time import sleep
from pytz import timezone
import schedule
from PIL import Image

AVATAR_INTERVAL = 5
GRUNN_TZ = timezone('Europe/Amsterdam')

consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def timely_avatar(twitter_api):
    # Round current time
    dttm = datetime.now(GRUNN_TZ)
    dttm += timedelta(minutes=AVATAR_INTERVAL / 2)
    dttm -= timedelta(minutes=dttm.minute % AVATAR_INTERVAL)
    # Create clock face image
    angle_hour = (dttm.hour + dttm.minute / 60 % 12) / 12 * -360 + 90
    angle_minute = (dttm.minute % 60) / 60 * -360 + 90
    img_face = Image.open('assets/clock_face.png')
    img_hour = Image.open('assets/hand_hour.png').rotate(angle_hour)
    img_minute = Image.open('assets/hand_minute.png').rotate(angle_minute)
    img_face.paste(img_minute, (0, 0), img_minute)
    img_face.paste(img_hour, (0, 0), img_hour)
    img_face.save('assets/avatar.png')
    # Update avatar of profile
    twitter_api.update_profile_image('assets/avatar.png')


def timely_tweet(twitter_api):
    # Sleep shortly to guarantee whole hour timestamp
    sleep(5)
    hour = datetime.now(GRUNN_TZ).hour
    bongs = (hour - 1) % 12 + 1
    tweet = 'BONG' + ' BONG' * (bongs - 1)
    twitter_api.update_status(tweet)


schedule.every().hour.at(':00').do(timely_tweet, twitter_api=api)
for i in range(0, 60, AVATAR_INTERVAL):
    schedule.every().hour.at(f':{i:02.0f}').do(timely_avatar, twitter_api=api)
schedule.every(5).minutes.do(timely_avatar, twitter_api=api)
while True:
    schedule.run_pending()
    sleep(1)
