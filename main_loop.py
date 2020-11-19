import ParlAI.parlai.scripts.steganography_api as stego
import slack_api

import time
import os

def run_loop(isAlice: bool):

    # Slack setup
    if isAlice:
        slack_api.setup(os.environ['ALICE_API_TOKEN'])
    else:
        slack_api.setup(os.environ['BOB_API_TOKEN'])
    channel_id = slack_api.getChannelId('steganography-project')
    my_user = None # Will be filled later

    # Stego setup
    stego.setup(open('settings.csv', 'r'))
    my_agent = 0
    other_agent = 0
    if isAlice:
        my_agent = stego.create_agent(True)
        other_agent = stego.create_agent(False)
    else:
        other_agent = stego.create_agent(False)
        my_agent = stego.create_agent(True)

    stego.post_secret(my_agent, b'This is the password')

    # Initial message
    if isAlice:
        text = stego.send_stegotext(my_agent)
        my_user = slack_api.sendMessage(channel_id, text)

    should_stop = False
    while(not should_stop):
        time.sleep(5.0)
        last_user, last_message = slack_api.getLastMessage(channel_id)
        if last_user == my_user:
            continue
        secret: bytes = stego.receive_stegotext(other_agent, last_message)
        if secret is not None:
            print("Received secret: ", secret)
        
        new_message = stego.send_stegotext(my_agent)
        my_user = slack_api.sendMessage(channel_id, new_message)

    stego.reset()
