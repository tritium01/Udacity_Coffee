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
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    formated_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formated_drinks
    })

'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    formated_drinks = [drink.long() for drink in drinks]
    return jsonify({
        'success': True,
        'drinks': formated_drinks
    })


'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    data = request.get_json()
    try:
        drink= Drink(
            title = data.get('title'),
            recipe= json.dumps(data.get('recipe'))
        )
        drink.insert()
        new_drink = Drink.query.filter_by(title = data.get('title')).one_or_none()  

        return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
        })
    except:
        abort(422)



'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def change_drink(jwt, drink_id):
    data = request.get_json()
    
    try:
        drink = Drink.query.filter_by(id= drink_id).one_or_none()
        drink.title = data.get('title')
        drink.recipe = json.dumps(data.get('recipe'))
        drink.update()
        
        return jsonify({
            'success': True,
            'drinks' : [drink.long()]
        })
    except:
        abort(422)

'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.filter_by(id= drink_id).one_or_none()
    try:
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except:
        abort(422)


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
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with appropriate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "Bad Request"
                    }), 400
    

@app.errorhandler(403)
def forbidden(error):
    return jsonify({
                    "success": False, 
                    "error": 403,
                    "message": "Forbidden"
                    }), 403
    
    
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
                    "success": False, 
                    "error": 500,
                    "message": "Internal Error"
                    }), 500
    
@app.errorhandler(AuthError)
def auth_error(ex):
  return jsonify({
                    "success": False,
                    "error": ex.status_code,
                    "message": ex.error['code']
                }),  ex.status_code

'''
@DONE implement error handler for 404
    error handler should conform to general task above 
'''


'''
@DONE implement error handler for AuthError
    error handler should conform to general task above 
'''
