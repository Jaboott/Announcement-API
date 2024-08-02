from datetime import datetime
from app.models import Announcements
from app import app
from flask import jsonify, request

# Dict as test database
r = {}
id = 0


@app.route('/announcements/post', methods=['POST'])
def create_announcement():
    global id
    data = request.get_json()

    announcement = Announcements(data['title'], data['content'], datetime.now())

    r[id] = announcement
    id = id + 1

    return jsonify(announcement.to_dict()), 201


@app.route('/announcements/get/<int:id>', methods=['GET'])
def get_announcement(id):
    announcement = r.get(id)
    print(type(announcement))
    if announcement:
        return jsonify(announcement.to_dict()), 200
    else:
        return jsonify({'error': 'Announcement not found'}), 404


@app.route('/')
def main():  # put application's code here
    return 'root'
