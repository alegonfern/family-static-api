"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

jackson_family = FamilyStructure("Jackson")

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def get_all_members():
    try:
        members = jackson_family.get_all_members()
        
        if not isinstance(members, list):
            raise APIException('Internal server error', status_code=500)

        return jsonify(members), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/member', methods=['POST'])
def add_member():
    try:
        data = request.json

        if not data or "first_name" not in data or "age" not in data or "lucky_numbers" not in data:
            return jsonify({"error": "Invalid request data"}), 400

        new_member = {
            "first_name": data["first_name"],
            "age": data["age"],
            "lucky_numbers": data.get("lucky_numbers", []),
        }

        if "id" in data:
            new_member["id"] = data["id"]

        jackson_family.add_member(new_member)
        
        return jsonify({"message": "Member added successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@app.route('/member/<int:member_id>', methods=['GET'])
def get_member_by_id(member_id):
    member = jackson_family.get_member(member_id)

    if member is None:
        return jsonify({"error": "Member not found"}), 404

    return jsonify(member), 200

@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    try:
        deleted = jackson_family.delete_member(member_id)

        if deleted:
            return jsonify({"done": True}), 200
        else:
            return jsonify({"error": "Member not found"}), 400

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500




if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)