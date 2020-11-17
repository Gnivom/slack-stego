# pip3 install slack_sdk

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

#SLACK_API_TOKEN = os.environ['SLACK_API_TOKEN']
SLACK_API_TOKEN = os.environ['ALICE_API_TOKEN']
assert(SLACK_API_TOKEN)

client = WebClient(token=SLACK_API_TOKEN)

def getChannelId(channel_name: str):
    try:
        response = client.conversations_list()
        allChannels = response['channels']
        for channel in allChannels:
            if channel['name'] == channel_name:
                return channel['id']
        assert False
        print(f"Couldn't find channel: {channel_name}")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
    return None

def sendMessage(channel_id: str, message: str):
    try:
        response = client.chat_postMessage(channel=channel_id, text=message)
        assert response['message']['text'] == message
        return response['message']['user'] # My own user
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
        return None

def getLastMessage(channel_id: str):
    try:
        response = client.conversations_history(channel=channel_id)
        messages = response['messages']
        if (len(messages) == 0):
            return None, None
        else:
            return messages[0]['user'], messages[0]['text']
        print(response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

channel_id = getChannelId('steganography-project')
my_user = sendMessage(channel_id, "Test1234")
user, text = getLastMessage(channel_id)
print(user, text)

