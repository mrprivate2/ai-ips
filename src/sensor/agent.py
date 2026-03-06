import requests
import json

class SensorAgent:

    def __init__(self, server):

        self.server = server

    def send_event(self, event):

        try:

            requests.post(
                f"{self.server}/event",
                json=event,
                timeout=2
            )

        except:
            pass