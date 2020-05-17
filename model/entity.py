from util import random_string
import json


class Entity:

    def set_deleted(self, is_deleted=True):
        self.is_deleted = is_deleted

    def get_deleted(self):
        return self.is_deleted

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def __init__(self, is_deleted=False):
        self.id = random_string()
        self.is_deleted = is_deleted

