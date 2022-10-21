import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    drinks = [drink.short() for drink in drinks]

    return jsonify({
        'code':200,
        'success': True,
        'drinks':drinks
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-details')
def get_drinks_detail(payload):
    alldrinks = Drink.query.all()
    print(alldrinks)
    drinks = [drink.long() for drink in alldrinks]
    return jsonify({
        'code':200,
        'success': True,
        'drinks': drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    body = request.get_json()
    title = body.get("title", None)
    recipe = body.get("recipe", None)
    
    well_formatted_recipe = json.dumps(recipe)
    

    try:
        drink = Drink(title=title, recipe=well_formatted_recipe)
        drink.insert()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
        
    except:
        raise AuthError({
            'code': 'invalid_request',
            'description': 'Unable to post to database.'
        }, 405)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_a_drink(jwt, id):

    try:
        #get the drink from db 
        a_drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        # if not found raise error
        if not a_drink :
            raise AuthError({
                'code': 'not_found',
                'description': 'The drink with this id is not found in the database.'
            }, 404)
        
        #else: get data to update the drink
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)
        
        # avoid single quote problems
        well_formatted_recipe = json.dumps(recipe)
        
        #update the drink with data
        if title:
            a_drink.title = title
            
        if recipe:
            a_drink.recipe = well_formatted_recipe
        a_drink.update()
        
        return jsonify({
            "success": True,
            "drinks": [a_drink.long()]
        }), 200
        
    except Exception:
        raise AuthError({
            'code': 'invalid_request',
            'description': 'Unable to query the database.'
        }, 400)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_a_drink(jwt, id):

    try:
        #get the drink from db 
        a_drink = Drink.query.filter(Drink.id == id).one_or_none()
        
        # if not found raise error
        if not a_drink :
            raise AuthError({
                'code': 'not_found',
                'description': 'The drink with this id is not found in the database.'
            }, 404)
        
        
        #delete the drink 
        a_drink.delete()
        
        return jsonify({
            "success": True,
            "delete": id
        }), 200
        
    except Exception:
        raise AuthError({
            'code': 'invalid_request',
            'description': 'Unable to query the database.'
        }, 400)
# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def not_authenticated(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error
    }), error.status_code   