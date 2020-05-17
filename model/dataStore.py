
class DataStore:

    def set_user(self, user):
        self.__users[user.id] = user

    def set_instrument(self, instrument):
        self.__instruments[instrument.id] = instrument

    def get_user(self, id):
        if id in self.__users and not self.__users[id].get_deleted():
            return self.__users[id]
        else:
            return None

    def get_instrument(self, id):
        if id in self.__instruments:
            return self.__instruments[id]
        else:
            return None

    def get_all_instruments(self):
        return self.__instruments

    def get_all_users(self):
        results = []
        for user_id in self.__users:
            if not self.__users[user_id].get_deleted():
                results.append(self.__users[user_id])

        return self.__users

    def delete_user(self, user_id):
        self.__users[user_id].set_deleted(True)

    def set_users(self, users):
        self.__users = users

    def set_instruments(self, instrument):
        self.__instruments = instrument

    def __init__(self, users, instruments):
        self.__users = users
        self.__instruments = instruments
