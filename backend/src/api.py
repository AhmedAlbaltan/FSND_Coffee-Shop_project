import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink,db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]
    return jsonify({
        'success':True,
        'drinks':drinks
    }),200


@app.route('/drinks-detail')
@requires_auth(permission='get:drinks-detail')
def get_drinks_details(payload):
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        'success':True,
        'drinks':drinks
    }),200
    
    



@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def create_drink(payload):
    body = request.get_json()
    
    if 'title' not in body  or 'recipe' not in body:
        abort(400)
    try:
        req_title= body['title']
        req_recipe= json.dumps(body['recipe'])
        drink = Drink(title=req_title, recipe=req_recipe)
        drink.insert()
        
        return jsonify({
            'success':True,
            'drinks':drink.long()
        }),200
    except:
    
        abort(500)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.get(id)
    
    if drink:
        try:
            
            body = request.get_json()
            drink.title = body['title'] if 'title' in body else drink.title
            drink.recipe = json.dumps(body['recipe']) if 'recipe' in body  else drink.recipe
            drink.update()
            return jsonify({
                'success':True,
                'drinks':drink.short() #can be drink.long too
            })
        except:
            # db.session.rollback()
            abort(500)
    else:
        abort(404)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def remove_drink(payload, id):
    drink = Drink.query.get(id)
    
    if drink:
        try:
            drink.delete()
            return jsonify({
                'success':True,
                'delete':id
            })
        except:
            
            # db.session.rollback()
            abort(500)
    else:
        abort(404)
        
        

## Error Handling


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405 
@app.errorhandler(400)
def badrequest(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400
    
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def resource_not_found(error):
     jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success':False,
        'error':500,
        'message':'Inernal Server Error'
    }),500
    
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(AuthError)
def authError(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error.get('description')
    }), error.status_code


if __name__ == '__main__':
    app.run(port=8000, debug=True)