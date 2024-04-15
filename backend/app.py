import os
from bson import ObjectId
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from pymongo import ReturnDocument
from pymongo.mongo_client import MongoClient

load_dotenv()  # This loads the environment variables from the .env file.

# MongoDB URI setup
uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
db = client.ChoreScheduler
chores_collection = db.chores

# Creating instance of the Flask class. The name of the application is the argument.
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "<p> Hello, World! </p>"

@app.route('/chores', methods=['POST'])
def create_chore():
    chore_data = request.json
    chore_data['completed'] = chore_data.get('completed', False)  # Ensure 'completed' is set, default to False
    result = chores_collection.insert_one(chore_data)
    chore_data['_id'] = str(result.inserted_id)  # Convert ObjectId to string
    return jsonify(chore_data), 201
    

@app.route('/chores', methods=['GET'])
def get_all_chores():
    chores = list(chores_collection.find({}))
    for chore in chores:
        chore['_id'] = str(chore['_id'])  # Convert ObjectId to string for JSON compatibility
    return jsonify(chores), 200

@app.route('/chores/<chore_id>', methods=['GET'])
def get_chore(chore_id):
    chore = chores_collection.find_one({"_id": ObjectId(chore_id)})
    if chore:
        chore['_id'] = str(chore['_id'])
        return jsonify(chore), 200
    else:
        return jsonify({'error': 'Chore not found'}), 404

@app.route('/chores/<chore_id>', methods=['PUT'])
def update_chore(chore_id):
    update_data = request.json
    result = chores_collection.find_one_and_update(
        {"_id": ObjectId(chore_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )
    if result:
        result['_id'] = str(result['_id'])
        return jsonify(result), 200
    else:
        return jsonify({'error': 'Chore not found'}), 404

@app.route('/chores/<chore_id>', methods=['DELETE'])
def delete_chore(chore_id):
    result = chores_collection.delete_one({"_id": ObjectId(chore_id)})
    if result.deleted_count == 1:
        return jsonify({'message': 'Chore deleted successfully'}), 200
    else:
        return jsonify({'error': 'Chore not found'}), 404

    
if __name__ == '__main__' :
    app.run(debug=True)
