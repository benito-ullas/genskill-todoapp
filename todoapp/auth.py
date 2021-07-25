from flask import Blueprint, g, request, render_template, jsonify, current_app
from . import db
import jwt
import psycopg2
import uuid
from werkzeug.security import generate_password_hash
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')

def token_required(f): 
        @wraps(f)
        def decorated(*args,**kwargs):
                token = None
                
                if 'x-access-token' in request.headers:
                        token = request.headers['x-access-token']
                if not token:
                        return jsonify({"message":"Token is missing"}),401
                        
                try:
                        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                        current_user = data['public id']                      
                                              
                except:
                        return jsonify({"message": "token is invalid"}),401
                return f(current_user,*args,**kwargs)
       
        return decorated
                        
@bp.route('/user', methods = ["POST"])
def create_user():
        data = request.get_json()
        
        hashed_password = generate_password_hash(data['password'], method='sha256')
        public_id = str(uuid.uuid4())
        
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("insert into users (public_id, username, password) values (%s, %s, %s);",(public_id, data['username'],hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"message": f"new user {data['username']} added"})
        
@bp.route('/user', methods = ['GET'])
@token_required
def get_all_users(current_user):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select admin from users where public_id = (%s);",(current_user,))
        is_admin = cur.fetchone()
        cur.execute("select * from users order by id;")
        data = cur.fetchall()
        cur.close()
        conn.close()
       
        if not is_admin[0]:
                return jsonify({'message':'cannot perform this task'}) 

        if data == []:
                output = {"message": "no users available"}
                return jsonify(output)
        else:
                output = []
                for i in data:
                        output.append({"public_id": i[1], "username": i[2], "password": i[3], "admin": i[4]})
        return jsonify({"users": output})
                
@bp.route('/user/<public_id>', methods = ['GET'])
@token_required
def get_one_user(current_user,public_id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select * from users where public_id = (%s);",(current_user,))
        data = cur.fetchone()
        cur.execute("select id from users where public_id = (%s);",(public_id,))
        id = cur.fetchone()
        
        if data[4] == 0 and data[1] != public_id:
                return jsonify({'message':'cannot view this page'}) 
        
        if id == None:
                output = {"message":"no such user! Enter valid id"}
        else:
                cur.execute("select * from users where id = (%s);",(id,))
                data = cur.fetchone()
                output = {"public_id": data[1], "username": data[2], "password": data[3], "admin": data[4] }
                
        cur.close()
        conn.close()
        
        
        return jsonify(output)
        
@bp.route('/user/<public_id>', methods = ['PUT'])
@token_required
def make_admin(current_user,public_id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select * from users where public_id = (%s);",(current_user,))
        data = cur.fetchone()
        cur.execute("select id from users where public_id = (%s);",(public_id,))
        id = cur.fetchone()
        
        if data[4] == 0:
                return jsonify({'message':'cannot perform this task'}) 
        
        if id == None:
                output = {"message":"no such user! Enter valid id"}
        else:
                cur.execute("update users set admin = 1 where id = (%s);",(id,))
                conn.commit()
                output = {"message": "user now has admin privilages"}
        cur.close()
        conn.close()
        
        return jsonify(output)
        
@bp.route('/user/<public_id>', methods = ['DELETE'])
@token_required
def delete_user(current_user,public_id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select * from users where public_id = (%s);",(current_user,))
        data = cur.fetchone()
        cur.execute("select id from users where public_id = (%s);",(public_id,))
        uid = cur.fetchone()
        
        if data[4] == 0 and data[1] != public_id:
                return jsonify({'message':'cannot perform this task'}) 
        
        if uid == None:
                output = {"message":"no such user! Enter valid id"}
        else:
                cur.execute("delete from users where id = (%s);",(uid,))
                conn.commit()
                output = {"message": "user has been deleted"}
        cur.close()
        conn.close()

        return jsonify(output)
        

