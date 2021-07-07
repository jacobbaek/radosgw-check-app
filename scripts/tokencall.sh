#!/bin/bash

URL="http://192.168.56.20/api/v4/posts" # localdev
BOTTOKEN="gnitmbt873rkdy9tdnps6kn3xa" # localdev bot
CHANNELID="j9m1fx3ktb8e8mzzokmqc7iora" # mattermost channel ID

set -x
curl -i -X POST \
 -H "authorization: Bearer $BOTTOKEN" \
 -H 'Content-Type: application/json' \
 -d '{"message": "test message by bot token", "channel_id":"'$CHANNELID'"}' \
 $URL
