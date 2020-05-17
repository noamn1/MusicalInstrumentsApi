
class Validators:

    __instrument_mandatory_properties = ['name', 'type']
    __link_request_mandatory_properties = ['instrument_id', 'link']
    __ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def validate_user(self, user_dict, users):
        for user_id in users:
            if users[user_id].email == user_dict['email']:
                raise ValueError("User email already exists")

    def validate_instrument(self, instrument_dict, instruments):
        for prop in self.__instrument_mandatory_properties:
            if prop not in instrument_dict:
                raise ValueError("Instrument missing mandatory property: " + prop)

        for inst_id in instruments:
            if instruments[inst_id].name.lower() == instrument_dict['name'].lower():
                raise ValueError("Instrument with the same name already exists: " + instrument_dict['name'])


    def validate_link_request(self, link_req_dict):
        for prop in self.__link_request_mandatory_properties:
            if prop not in link_req_dict:
                raise ValueError("Link request missing mandatory property: " + prop)

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.__ALLOWED_EXTENSIONS

    def validate_image(self, file, instrument):
        if file.filename == '':
            raise ValueError("No selected file: ")
        if not file or not self.allowed_file(file.filename):
            raise ValueError("Unsupported file type")

        if len(instrument.images) >= 2:
            raise ValueError("Cannot save more than 2 images")

    def validate_search_term(self, term):
        if not term or len(term) == 0:
            raise ValueError("Invalid search term:" + term)

    def __init__(self):
        pass

