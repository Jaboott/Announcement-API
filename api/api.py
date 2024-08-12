import datetime
import json
import secrets

import redis

from flask import jsonify, request, Flask, url_for, redirect, session
from authlib.integrations.flask_client import OAuth

r = redis.Redis(host='localhost', port=6379, db=0)
app = Flask(__name__)


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
    data = request.get_json()
    header = request.headers.get('APIKEY')
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
    domain = request.args.get('domain')

    if domain is None:
        return jsonify({'error': 'No domain provided'}), 400

    announcement_data = r.hgetall(domain)

    # No matching domain found in db
    if not announcement_data:
        return jsonify({'error': 'No announcements found'}), 404

    # Deleting the hash
    r.delete(domain)

    return jsonify({'success': True}), 200


@app.route('/')
def main():  # put application's code here
    return 'root'


if __name__ == '__main__':
    app.run(debug=True)
