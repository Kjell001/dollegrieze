#!/usr/bin/env python3

# Basic
import os
import random
from math import ceil
import tweepy
from PIL import Image
# Timekeeping and scheduling
import schedule
from pytz import timezone
from time import sleep
from datetime import datetime, timedelta


AVATAR_INTERVAL = 5  # Minutes interval in which avatar is updated
GRUNN_TZ = timezone('Europe/Amsterdam')
BELLS = ('DING', 'DANG', 'DONG')

# Set up Twitter connection
consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def ring_bells(dttm):
    times = (dttm.hour - 1) % 12 + 1
    ind_possible = list(range(len(BELLS)))
    # Seed ensures bell sounds are consistent throughout day half
    seed = 2 * dttm.toordinal() + int(dttm.hour > 11)
    random.seed(seed)
    # Don't allow same sounds in a row
    indices = [seed % len(BELLS)]
    for _ in range(times - 1):
        ind = ind_possible.copy()
        ind.remove(indices[-1])
        indices += [random.choice(ind)]
    return ' '.join(BELLS[index] for index in indices)


def timely_tweet(twitter_api):
    sleep(5)  # Sleep shortly to guarantee tweet timestamp at :00
    tweet = ring_bells(datetime.now(GRUNN_TZ))
    twitter_api.update_status(tweet)


def timely_avatar(twitter_api):
    # Round current time to chosen interval
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


# Schedule jobs
schedule.every().hour.at(':00').do(timely_tweet, twitter_api=api)
offset = ceil(AVATAR_INTERVAL / 2)
for i in range(offset, 60, AVATAR_INTERVAL):
    schedule.every().hour.at(f':{i:02.0f}').do(timely_avatar, twitter_api=api)
# Run scheduler
while True:
    schedule.run_pending()
    sleep(1)
