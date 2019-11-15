import scraper
import time

class User():
    def __init__(self, messenger_id=None):
        self.portal_id = None
        self.portal_password = None
        self.messenger_id = messenger_id
        self.last_href = None
        self.thread = None
        self.stop = False


    def get_id(self):
        return self.portal_id


    def get_password(self):
        return self.portal_password


    def update_id(self, new_id):
        self.portal_id = new_id


    def update_password(self, new_password):
        self.portal_password = new_password


    def check_credentials(self):
        return scraper.try_login(self.portal_id, self.portal_password)