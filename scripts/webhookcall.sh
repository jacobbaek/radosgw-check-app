#!/bin/bash

WEBHOOKURL="http://192.168.56.20/hooks/q4d3ikpupfbidkuo9uh8j8za5h"
CHANNELNAME="staging" # mattermost channel name
MESSAGE="send a test message :tada:"

# for message with attachments
curl -i -X POST -H "Content-Type: application/json" \
 -d '{"username": "pythonbot", "channel":"'$CHANNELNAME'", "attachments": [{"text":"'$MESSAGE'"}]}' \
 $WEBHOOKURL
