from flask import request, jsonify
from control_server.src.controller import controller
from control_server.src.database.database_collection import DatabaseCollection

def client():
    """
    Endpoint handing the client information request from admin GUI
    """
    client_id = request.args['id']
    if client_id is None:
        return '', 400

    # Get client information
    databaseCollection = DatabaseCollection()
    client_info = controller.db.get_one(databaseCollection.USERS, client_id)
    if client_info is None:
        return 'Wrong client id', 404