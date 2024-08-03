import datetime
import json
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
    start_time = 0.0
    end_time = datetime.datetime.now().timestamp()

    announcements = []
    # use zrange(byscore=True): somehow doesnt work
    keys = r.zrangebyscore("announcements", start_time, end_time)

    for key in keys:
        announcement_data = r.hgetall(key)
        announcement_dict = {}

        # Decode the key value pair that's hashed
        for k, v in announcement_data.items():
            key = k.decode("utf-8")
            val = v.decode("utf-8")
            announcement_dict[key] = val
        # Build Announcement object
        announcement = Announcements(
            announcement_dict['title'],
            announcement_dict['content'],
            announcement_dict['timestamp'])

        announcements.append(announcement.to_dict())

    return jsonify(announcements), 200


@app.route('/')
def main():  # put application's code here
    return 'root'
