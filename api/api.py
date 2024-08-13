import datetime
import secrets
import hashlib

import redis

from flask import jsonify, request, Flask, url_for, redirect, session
from authlib.integrations.flask_client import OAuth

r = redis.Redis(host='localhost', port=6379, db=0)
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


class Announcement:
    def __init__(self, title, content, timestamp):
        """
        Initialize an Announcements object.

        :param title: Title of the announcement.
        :param content: Body of the announcement.
        :param timestamp: The time the announcement is created in Epoch time
        """

        self.title = title
        self.content = content
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp
        }


@app.route('/announcement/post', methods=['POST'])
def post_announcement():
    header = request.headers.get('APIKEY')
    if not check_auth(header):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    # Optional ttl field for the announcement
    args = request.args.get('ttl')
    # Epoch time
    date = datetime.datetime.now().timestamp()
    announcement = Announcement(data['title'], data['content'], date)

    r.hset(data['domain'], mapping=announcement.to_dict())

    if args and int(args) > 0:
        r.expire(data['domain'], int(args))

    return jsonify(announcement.to_dict()), 201


@app.route('/announcement/get', methods=['GET'])
def get_announcement():
    domain = request.args.get('domain')

    # No domain provided
    if domain is None:
        return jsonify({'error': 'No domain provided'}), 400

    announcement_data = r.hgetall(domain)
    announcement_dict = {}

    # No matching domain found in db
    if not announcement_data:
        return jsonify({'error': 'No announcements found'}), 404

    # Decode the key value pair that's hashed
    for k, v in announcement_data.items():
        key = k.decode("utf-8")
        val = v.decode("utf-8")
        announcement_dict[key] = val

    # Build Announcement object
    announcement = Announcement(
        announcement_dict['title'],
        announcement_dict['content'],
        announcement_dict['timestamp']
    )

    return jsonify(announcement.to_dict()), 200


@app.route('/announcement/delete')
def delete_announcement():
    header = request.headers.get('APIKEY')
    if not check_auth(header):
        return jsonify({'error': 'Unauthorized'}), 401

    domain = request.args.get('domain')

    if domain is None:
        return jsonify({'error': 'No domain provided'}), 400

    # No matching domain found in db
    if not r.exists(domain):
        return jsonify({'error': 'No announcements found'}), 404

    # Deleting the hash
    r.delete(domain)

    return jsonify({'success': True}), 200


def check_auth(api_key):
    # Checking if api key exists
    if api_key is not None:
        return r.hget('AUTH', 'api_key').decode("utf-8") == hashlib.sha256(api_key.encode('utf-8')).hexdigest()

    return False


@app.route('/announcement/api-key', methods=['GET'])
def get_api_key():
    # Initialize the admin if it's not set
    if not r.hgetall('AUTH'):
        return initialize_admin()

    email = session.get('email', None)
    # Redirect to login route
    if email is None:
        return redirect('/announcement/login')

    # Reject request if
    if r.hget('AUTH', 'email').decode("utf-8") != hashlib.sha256(email.encode('utf-8')).hexdigest():
        return jsonify({'error': 'Unauthorized'}), 401

    # Sets a new api key
    api_key = secrets.token_hex(16)
    r.hset('AUTH', 'api_key', hashlib.sha256(api_key.encode('utf-8')).hexdigest())

    return jsonify({'api_key': api_key, 'success': True}), 200


def initialize_admin():
    # Return if AUTH field is already initialized
    if r.hgetall('AUTH'):
        return jsonify({'error': 'Forbidden'}), 403

    email = session.get('email', None)
    # Redirect to login route
    if email is None:
        return redirect('/announcement/login')

    # Encode the email and api key
    r.hset('AUTH', 'email', hashlib.sha256(email.encode('utf-8')).hexdigest())
    api_key = secrets.token_hex(16)
    r.hset('AUTH', 'api_key', hashlib.sha256(api_key.encode('utf-8')).hexdigest())

    return jsonify({'email': email, 'api_key': api_key, 'success': True}), 200


@app.route('/announcement/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/announcement/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    return redirect('/announcement/api-key')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/')
def main():  # put application's code here
    email = dict(session).get('email', None)
    return f'Hello, you are logged in as {email}!'


if __name__ == '__main__':
    app.run(debug=True)
