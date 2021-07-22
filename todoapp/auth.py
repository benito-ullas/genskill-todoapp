from flask import Blueprint, g, request, render_template, jsonify
from . import db
import jwt
import psycopg2
import uuid
from werkzeug.security import generate_password_hash, check_password_hash 

bp = Blueprint('auth', __name__, url_prefix='/auth')

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
def get_all_users():
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select * from users order by id;")
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        
        
        if data == []:
                output = {"message": "no users available"}
                return jsonify(output)
        else:
                output = []
                for i in data:
                        output.append({"public_id": i[1], "username": i[2], "password": i[3], "admin": i[4]})
        return jsonify({"users": output})
                
@bp.route('/user/<public_id>', methods = ['GET'])
def get_one_user(public_id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select id from users where public_id = (%s);",(public_id,))
        id = cur.fetchone()
        
        if id == None:
                output = {"message":"no such user! Enter valid id"}
        else:
                cur.execute("select * from users where id = (%s);",(id,))
                data = cur.fetchone()
                if data == None:
                        output = {"message": "user doesnt exist"}
                
                else:
                        output = {"public_id": data[1], "username": data[2], "password": data[3], "admin": data[4] }
                
        cur.close()
        conn.close()
        
        
        return jsonify(output)
        
@bp.route('/user/<public_id>', methods = ['PUT'])
def make_admin(public_id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select id from users where public_id = (%s);",(public_id,))
        id = cur.fetchone()
        
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
def delete_user(public_id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select id from users where public_id = (%s);",(public_id,))
        uid = cur.fetchone()
        
        if uid == None:
                output = {"message":"no such user! Enter valid id"}
        else:
                cur.execute("delete from users where public_id = (%s);",(uid,))
                conn.commit()
                output = {"message": "user has been deleted"}
        cur.close()
        conn.close()

        return jsonify(output)
        

