#!/usr/bin/env python

# referenced following API page
# * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#id221

import json
import boto3
from botocore.exceptions import ClientError

import requests
from urllib import request, error

_RED="#FF2D00"
_GREEN="009D31"

with open('config.json', 'r') as fd:
    cred = json.loads(fd.read())

def send_alarm_exit(message, color):
    headers = {'Content-Type': 'application/json'}
    values = '{ \
        "username": "pybot", \
        "channel": "' + cred["mattermost_webhook_channel"] + '", \
        "icon_url": "https://img.icons8.com/fluent/200/000000/binoculars.png", \
        "attachments": [{ \
            "color": "' + color + '", \
            "title": "radosgw healthcheck result", \
            "title_link": "http://localhost/", \
            "author_name": "rook healthcheck bot", \
            "author_icon": "https://img.icons8.com/fluent/200/000000/binoculars.png", \
            "text": "' + message + '" \
        }] \
    }'
    response = requests.post(cred["mattermost_webhook_url"], headers=headers, data=values)
    # print(response.request.body)
    # print(response.status_code)
    # print(response.content)
    if color == _RED:
        exit(False)
    else:
        exit(True)

def main():

    alarm_message = ""

    # Retrieve the list of existing buckets
    conn = boto3.client('s3',
        aws_access_key_id = cred["access_key"],
        aws_secret_access_key = cred["secret_key"],
        endpoint_url = cred["endpoint_url"],
        region_name = cred["region_name"]
    )
    
    # Create bucket for test
    try:
        bucket = conn.create_bucket(
            ACL='public-read',
            Bucket=cred["bucket_name"]
        )
        conn.put_bucket_website(
            Bucket=cred["bucket_name"],
            WebsiteConfiguration={
                'ErrorDocument': {
                    'Key': 'error.html'
                },
                'IndexDocument': {
                    'Suffix': 'index.html'
                }
            }
        )
    except ClientError as e:
        alarm_message = alarm_message + "\n - [ ] bucket creation"
        print(e)
        send_alarm_exit(alarm_message, _RED)

    alarm_message = alarm_message + "\n - [x] bucket creation"

    # Download test image file
    try:
        request.urlretrieve(cred["image_url"], cred["upload_file_name"])
        request.urlretrieve(cred["index_url"], "index.html")
    except error.URLError as e:
        alarm_message = alarm_message + "\n - failed to download image file"
        print(e)
        send_alarm_exit(alarm_message, _RED)

    # Upload test image file
    try:
        _objname = cred["upload_file_name"]
        conn.upload_file(cred["upload_file_name"], cred["bucket_name"], _objname)
        conn.upload_file("index.html", cred["bucket_name"], "index.html")
    except ClientError as e:
        alarm_message = alarm_message + "\n - [ ] image file uploading"
        print(e)
        send_alarm_exit(alarm_message, _RED)

    alarm_message = alarm_message + "\n - [x] image file uploading"

    # Download test image file from s3 
    try:
        conn.download_file(cred["bucket_name"], cred["upload_file_name"], "fromCeph" + cred["upload_file_name"])
    except ClientError as e:
        alarm_message = alarm_message + "\n - [ ] image file downloading"
        print(e)
        send_alarm_exit(alarm_message, _RED)

    alarm_message = alarm_message + "\n - [x] image file downloading"

    # Config object permission
    try:
        conn.put_object(
            ACL='public-read',
            Bucket=cred["bucket_name"],
            Key=cred["upload_file_name"]
        )
    except ClientError as e:
        alarm_message = alarm_message + "\n - [ ] bucket permission configuration"
        print(e)
        send_alarm_exit(alarm_message, _RED)

    alarm_message = alarm_message + "\n - [x] bucket permssion configuration"

    # Print and delete objects in test bucket
    try:
        objs = conn.list_objects_v2(
            Bucket=cred["bucket_name"],
            MaxKeys=5
        )["Contents"]
        for obj in objs:
            conn.delete_object(Bucket=cred["bucket_name"], Key=obj["Key"])
            #print("Deleted " + obj["Key"] + " object.")
    except ClientError as e:
        alarm_message = alarm_message + "\n - [ ] object deletion"
        print(e)
        send_alarm_exit(alarm_message, _RED)

    alarm_message = alarm_message + "\n - [x] object deletion"

    # Print bucket list
    # try:
    #     bucketlst = conn.list_buckets()
    #     # Output the bucket names
    #     print('Existing buckets:')
    #     for bucket in bucketlst['Buckets']:
    #         print(f'  {bucket["Name"]}')
    # except ClientError as e:
    #     alarm_message = alarm_message + "\n - failed to print bucket list"
    #     print(e)
    #     send_alarm_exit(alarm_message, _RED)

    # Delete bucket for test
    try:
        conn.delete_bucket(
            Bucket=cred["bucket_name"]
        )
    except ClientError as e:
        alarm_message = alarm_message + "\n - [ ] bucket deletion"
        print(e)
        send_alarm_exit(alarm_message, _RED)

    alarm_message = alarm_message + "\n - [x] bucket deletion"

    send_alarm_exit(alarm_message, _GREEN)

if __name__ == '__main__':
    main()
