from model.entity import Entity


class User(Entity):

    def add_instrument(self, instrument_id):
        self.instrument_ids.append(instrument_id)


    def __init__(self, first_name, last_name, email, password, instrument_ids=[], is_deleted=False):
        super(User, self).__init__(is_deleted)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.instrument_ids = instrument_ids

