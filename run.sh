#!/bin/bash
cron

while true; do
    python FeedCLI.py --settings settings.json
    sleep 1
    echo > feed_processor.log 
done
