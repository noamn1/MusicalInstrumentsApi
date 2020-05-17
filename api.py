from flask import Flask, send_file, jsonify, json, request, render_template, abort, escape
from model.user import User
from model.instrument import Instrument
from model.dataStore import DataStore
from validations.validators import Validators
from validations.RegistrationForm import RegistrationForm
import os.path
import io
import threading
import time


app = Flask(__name__)

data_store = None
validators = Validators()

lock = None
USERS_BACKUP_FILE='data/users.json'
INSTRUMENTS_BACKUP_FILE='data/instruments.json'

@app.route("/instrument", methods=["POST"])
def add_instrument():
    instrument_content = request.json
    try:
        instruments = data_store.get_all_instruments()
        validators.validate_instrument(instrument_content, instruments)
    except ValueError as err:
        response = app.response_class(
            response=json.dumps({"err": str(err)}),
            status=400,
            mimetype='application/json'
        )
        return response

    instrument = Instrument(instrument_content['name'], instrument_content['type'], instrument_content['links'])
    data_store.set_instrument(instrument)
    response = app.response_class(
        response=json.dumps({"instrument": instrument.to_json()}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/instruments")
def get_instruments():
    instruments = data_store.get_all_instruments()
    json_instruments = []

    for inst_id in instruments:
        json_instruments.append(instruments[inst_id].to_json())

    response = app.response_class(
        response=json.dumps(json_instruments),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/instrument/<string:instrument_id>")
def get_instrument_by_id(instrument_id):
    instrument = data_store.get_instrument(instrument_id)
    if instrument is None:
        abort(400)

    response = app.response_class(
        response=json.dumps(instrument.to_json()),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/instrument/user/<string:user_id>")
def get_instruments_by_user(user_id):
    user = data_store.get_user(user_id)
    if user is None:
        abort(400)

    instruments = []
    for inst_id in user.instrument_ids:
        instruments.append(data_store.get_instrument(inst_id).to_json())

    response = app.response_class(
        response=json.dumps({"instruments": instruments}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/instrument/<string:instrument_id>/user/<string:user_id>", methods=["PUT"])
def assign_instrument_to_user(instrument_id, user_id):
    user = data_store.get_user(user_id)
    instrument = data_store.get_instrument(instrument_id)
    if user is None or instrument is None:
        abort(400)

    user.add_instrument(instrument_id)
    lock.acquire()
    data_store.set_user(user)
    lock.release()
    response = app.response_class(
        response=json.dumps({"user": user.to_json()}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/instrument/link", methods=["PUT"])
def add_link():
    instrument_content = request.json
    try:
        validators.validate_link_request(instrument_content)
    except ValueError as err:
        response = app.response_class(
            response=json.dumps({"err": str(err)}),
            status=400,
            mimetype='application/json'
        )
        return response

    instrument = data_store.get_instrument(instrument_content['instrument_id'])
    if instrument is None:
        abort(400)

    link = escape(instrument_content['link'])
    instrument.links.append(link)
    lock.acquire()
    data_store.set_instrument(instrument)
    lock.release()

    response = app.response_class(
        response=json.dumps(instrument.to_json()),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST':
        all_users = data_store.get_all_users()
        try:
            validators.validate_user(request.form, all_users)
        except Exception as e:
            return redirect('error.html')
        if  form.validate():
            user = User(form.first_name.data, form.last_name.data,
                        form.email.data, form.password.data)

            lock.acquire()
            data_store.set_user(user)
            lock.release()
            return app.response_class(
                response=json.dumps({"user": user.to_json()}),
                status=200,
                mimetype='application/json'
            )
    return render_template('register.html', form=form)


@app.route('/instrument/image', methods=['POST'])
def upload_img():
    if 'instrument_id' not in request.form:
        abort(400)

    instrument = data_store.get_instrument(request.form['instrument_id'])
    image_file = request.files['data']
    validators.validate_image(image_file, instrument)
    try:
        image_file.save('images/'+image_file.filename)
        instrument.add_image(image_file.filename)
        lock.acquire()
        data_store.set_instrument(instrument)
        lock.release()
        response = app.response_class(
            response=json.dumps({"status": "ok"}),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        response = app.response_class(
            response=json.dumps({"err": "Unable to save image"}),
            status=400,
            mimetype='application/json'
        )
        return response

@app.route('/instrument/<string:instrument_id>/image/<int:image_num>')
def get_image(instrument_id, image_num):
    if image_num > 2 or image_num < 1:
        abort(400)

    instrument = data_store.get_instrument(instrument_id)
    if instrument is None:
        abort(400)

    img_name = instrument.images[image_num-1]

    try:
        with open(os.path.join('images', img_name), "rb") as bites:

            mime = img_name.split('.')
            return send_file(
                io.BytesIO(bites.read()),
                attachment_filename=img_name,
                mimetype='image/'+mime[1]
            )

    except Error as err:
        response = app.response_class(
            response=json.dumps({"err": "Unable to load image"}),
            status=400,
            mimetype='application/json'
        )
        return response


@app.route('/instrument/<string:instrument_id>/user/<string:user_id>', methods=['DELETE'])
def delete_instrument(instrument_id, user_id):
    user = data_store.get_user(user_id)
    instrument = data_store.get_instrument(instrument_id)
    if user is None or instrument is None:
        abort(400)

    for inst_id in user.instrument_ids:
        if inst_id == instrument_id:
            user.instrument_ids.remove(inst_id)
            break

    lock.acquire()
    data_store.set_user(user)
    lock.release()
    response = app.response_class(
        response=json.dumps({"user": user.to_json()}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/user/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = data_store.get_user(user_id)
    if user is None:
        abort(400)

    lock.acquire()
    data_store.delete_user(user_id)
    lock.release()
    response = app.response_class(
        response=json.dumps({"status": "deleted"}),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/instrument/search')
def search():
    term = request.args.get('term')
    try:
        validators.validate_search_term(term)
    except ValueError as err:
        response = app.response_class(
            response=json.dumps({"err": str(err)}),
            status=400,
            mimetype='application/json'
        )
        return response

    instruments = data_store.get_all_instruments()
    search_results = []
    for inst_id in instruments:
        if term.lower() in instruments[inst_id].name.lower():
            search_results.append(instruments[inst_id].to_json())

    response = app.response_class(
        response=json.dumps(search_results),
        status=200,
        mimetype='application/json'
    )
    return response

def restore_backup():
    try:
        with open(USERS_BACKUP_FILE, 'r') as json_file:
            users = json.load(json_file)
            user_objs = {}
            for user_id in users:
                user_dict = json.loads(users[user_id])
                u = User(user_dict['first_name'], user_dict['last_name'], user_dict['email'],
                         user_dict['password'], user_dict['instrument_ids'], user_dict['is_deleted'])
                user_objs[user_id] = u
            lock.acquire()
            data_store.set_users(user_objs)
            lock.release()

    except FileNotFoundError:
        print('no users file to load from backup')

    try:
        with open(INSTRUMENTS_BACKUP_FILE, 'r') as json_file:
            instruments = json.load(json_file)
            instruments_objs = {}
            for inst_id in instruments:
                inst_dict = json.loads(instruments[inst_id])
                i = Instrument(inst_dict['name'], inst_dict['type'], inst_dict['links'], inst_dict['images'])
                instruments_objs[inst_id] = i
            data_store.set_instruments(instruments_objs)

    except FileNotFoundError:
        print('no instruments file to load from backup')

def do_back_up(lock):
    while True:
        lock.acquire()
        all_users = data_store.get_all_users()
        users = {}
        for user_id in all_users:
            users[user_id] = all_users[user_id].to_json()

        with open(USERS_BACKUP_FILE, 'w') as fp:
            json.dump(users, fp)

        all_instruments = data_store.get_all_instruments()
        instruments = {}
        for inst_id in all_instruments:
            print(all_instruments[inst_id].to_json())
            instruments[inst_id] = all_instruments[inst_id].to_json()

        with open(INSTRUMENTS_BACKUP_FILE, 'w') as fp:
            json.dump(instruments, fp)

        lock.release()
        time.sleep(60)


@app.before_first_request
def before_first_request_func():
    global data_store
    data_store = DataStore({}, {})
    global lock
    lock = threading.Lock()
    restore_backup()

    t1 = threading.Thread(target=do_back_up, args=(lock,))
    t1.start()



if __name__ == "__main__":
    app.run()

