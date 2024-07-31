import datetime
import redis
import json

from flask import Flask, jsonify
from flask_restful import reqparse

app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

announcement_args = reqparse.RequestParser(bundle_errors=True)
announcement_args.add_argument('title', type=str, help='Title of the announcement', required=True)
announcement_args.add_argument('content', type=str, help='Content of the announcement', required=True)


@app.route('/announcements/post', methods=['POST'])
def create_announcement():
    id = int(r.get('id'))
    data = announcement_args.parse_args()
    announcement = {
        'title': data['title'],
        'content': data['content'],
        'timestamp': datetime.datetime.now().isoformat()
    }
    r.set(id, json.dumps(announcement))
    r.set('id', id + 1)
    return jsonify(announcement), 201


@app.route('/announcements/get/<int:id>', methods=['GET'])
def get_announcement(id):
    announcement = r.get(id)
    if announcement:
        announcement = json.loads(announcement)
        announcement['timestamp'] = datetime.datetime.fromisoformat(announcement['timestamp'])
        return jsonify(announcement), 200
    else:
        return jsonify({'error': 'Announcement not found'}), 404


@app.route('/')
def main():  # put application's code here
    return 'root'


if __name__ == '__main__':
    app.run(debug=True)
