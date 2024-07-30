from flask import Flask, jsonify, request
from flask_restful import reqparse, Api
import datetime
app = Flask(__name__)


announcements = {}
curr_id = 0

announcement_args = reqparse.RequestParser(bundle_errors=True)
announcement_args.add_argument('title', type=str, help='Title of the announcement', required=True)
announcement_args.add_argument('content', type=str, help='Content of the announcement', required=True)


@app.route('/announcements', methods=['POST'])
def create_announcement():
    global curr_id
    data = announcement_args.parse_args()
    announcement = {
        'id': curr_id,
        'title': data['title'],
        'content': data['content'],
        'timestamp': datetime.datetime.now()
    }
    announcements[curr_id] = announcement
    curr_id += 1
    return jsonify(announcement), 201


@app.route('/announcements/<int:id>', methods=['GET'])
def get_announcement(id):
    global curr_id
    announcement = announcements[id]
    return jsonify(announcement), 200


@app.route('/')
def main():  # put application's code here
    return 'root'


if __name__ == '__main__':
    app.run(debug=True)
