#!/bin/bash
cron

while true; do
    python FeedCLI.py --settings settings-mongo.json
    sleep 1
    echo > feed_processor.log 
done
