
__author__ = "Numerical Analysis Intelligence (NumbersAI) Group"

import sys,re
import datetime as dt
from datetime import timedelta

from ircchat import chat_frame

"""
    IRC Chat Processing of collected chat.log

    1. loads in an existing collected chat.log 
    2. repairs any lines missing a timestamp. This is usually caused by embedded ^M characters
    3. uses an established spinnyKitty machine learning model to find Spinny Kitty events from chat

"""

def main():

    print("*** Loading Data")
    chat_log_file = './logs/chat.log'
    with open(chat_log_file) as f:
        lines = f.readlines()
    print("*** Loading Complete")

    frame = chat_frame()
    previous_timestamp = ""
    regex_time_stamp = '^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}-\d{4})'
    timestamp_format = '%Y-%m-%dT%H:%M:%S%z'
    time_threshold = timedelta(seconds=300)

    latch_timestamp = None

    # there are log lines that get a carriage return in them this causes the next chat message to be missing timestamp
    # we use the previous message timestamp to fill it in
    # aditionally we use a 5 minute time window from the first chat event the model identifies at Spinny Kitty
    # this lets us just output timestamps of the event vs all chat lines that contribute to a frame that matches the model

    for line in lines:
        try:
            timestamp = re.search(regex_time_stamp, line).groups()
            previous_timestamp = timestamp[0]
            repaired_line = line
        except Exception as e:
            if line is not None or line!="":
                repaired_line = "{0} — {1}".format(previous_timestamp,line)
            else:
                continue

        processed_line = frame.process_line(repaired_line)
        frame.add_message(processed_line)
        prediction = frame.model.predict(frame.frame_features)
        if 'hermitSpinnyKitty' in line and (prediction[0]):
            event_timestamp = processed_line.get('time')
            if latch_timestamp is None or event_timestamp >= (latch_timestamp+time_threshold): 
                latch_timestamp = event_timestamp
                print(latch_timestamp)

if __name__ ==  "__main__":

    main()


