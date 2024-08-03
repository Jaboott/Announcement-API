import datetime
import uuid

import redis

from app.models import Announcements
from app import app
from flask import jsonify, request

r = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/announcements/post', methods=['POST'])
def create_announcement():
    data = request.get_json()
    # Epoch time
    date = datetime.datetime.now().timestamp()
    announcement = Announcements(data['title'], data['content'], date)
    announcement_id = str(uuid.uuid4())

    r.hset(announcement_id, mapping=announcement.to_dict())
    r.zadd("announcements", {announcement_id: date})

    return jsonify(announcement.to_dict()), 201


@app.route('/announcements/get', methods=['GET'])
def get_announcement():
    announcement = r.get(id)
    print(type(announcement))
    if announcement:
        return jsonify(announcement.to_dict()), 200
    else:
        return jsonify({'error': 'Announcement not found'}), 404


@app.route('/')
def main():  # put application's code here
    return 'root'
