import ParlAI.parlai.scripts.steganography_api as stego
import slack_api

import time
import os

class StegoSlackApp:
    def __init__(self, is_alice: bool):
        self.is_alice = is_alice
        self.secret_queue = []
        # Slack setup
        if is_alice:
            slack_api.setup(os.environ['ALICE_API_TOKEN'])
        else:
            slack_api.setup(os.environ['BOB_API_TOKEN'])
        self.channel_id = slack_api.getChannelId('steganography-project')
        self.my_user = None # Will be filled later

        # Stego setup
        stego.setup(open('settings.csv', 'r'))
        self.my_agent = 0
        self.other_agent = 0
        if is_alice:
            self.my_agent = stego.create_agent(True)
            self.other_agent = stego.create_agent(False)
        else:
            self.other_agent = stego.create_agent(False)
            self.my_agent = stego.create_agent(True)

        # Initial message
        if is_alice:
            text = stego.send_stegotext(self.my_agent)
            self.my_user = slack_api.sendMessage(self.channel_id, text)
    
    def __del__(self):
        if stego:
            stego.reset()

    def post_secret(self, secret: bytes):
        self.secret_queue.append(secret)

    def update(self):
        last_user, last_message = slack_api.getLastMessage(self.channel_id)
        if last_user == self.my_user:
            return
        secret: bytes = stego.receive_stegotext(self.other_agent, last_message)

        if len(self.secret_queue) > 0 and not stego.has_pending_message(self.my_agent):
            stego.post_secret(self.my_agent, self.secret_queue[0])
            self.secret_queue = self.secret_queue[1:]

        new_message = stego.send_stegotext(self.my_agent)
        self.my_user = slack_api.sendMessage(self.channel_id, new_message)
        return secret

