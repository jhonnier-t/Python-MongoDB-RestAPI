from flask import Flask, json, request, jsonify, Response
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import json_util
from bson.objectid import ObjectId
from vars import Username, Password

app = Flask(__name__)

conn = "mongodb://localhost:27017"
client = MongoClient(conn, serverSelectionTimeoutMS=5000)   # set a 5-second connection timeout
try:
    db = client.RESTAPIDB
    crudDB = db.datesDB
    print("Connect with the server.", client.server_info)
except Exception:
    print("Unable to connect to the server.")

@app.route('/users', methods=['POST'])
def createUser():
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    
    if username and email and password:
        hashed_password = generate_password_hash(password)
        crudDB.insert_one(
            {'username':username, 'password':hashed_password,'email':email})

        id = str(ObjectId(crudDB.find_one(username)))
        
        response = {
            'id' : id,
            'username' : username,
            'password': hashed_password,
            'email': email
        }
        return response
    else:
        return not_found()

@app.route('/users', methods=['GET'])
def getUsers():
    users = crudDB.find()
    response = json_util.dumps(users)
    return Response(response, mimetype='application/json')

@app.route('/users/<id>', methods=['GET'])
def getUser(id):
    user  = crudDB.find_one({'_id': ObjectId(id)})
    response = json_util.dumps(user)
    return Response(response, mimetype='application/json')

@app.route('/users/<id>', methods=['DELETE'])
def deleteUser(id):
    crudDB.delete_one({'_id': ObjectId(id)})
    response =  jsonify({'msg:':'user' + id + 'was deleted sucessfully'})
    return response

@app.route('/users/<id>', methods=['PUT'])
def updatedUser(id):
    crudDB.replace_one({'_id': ObjectId(id)}, 
    {'username': request.json['username'],
    'password' : request.json['password'],
    'email' : request.json['email']
    })

    response =  jsonify({'msg:':'user' + id + 'was updated sucessfully'})
    return response

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
    'message': 'Resource Not Found' + request.url,
    'status': 404})

    response.status_code = 404
    return response

if __name__ == "__main__":
    app.run(debug=True)
