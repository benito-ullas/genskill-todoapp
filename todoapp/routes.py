from flask import Blueprint, g, request, render_template, jsonify, make_response,current_app
from . import db
import psycopg2
from werkzeug.security import check_password_hash 
import jwt
import datetime
from functools import wraps


bp = Blueprint('todo', __name__, url_prefix='/')

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

@bp.route('/todo')
@token_required
def get_all(current_user):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select id from users where public_id = (%s)",(current_user,))
        u =  cur.fetchone()
        cur.execute("select * from data where user_id = (%s)",(u[0],))
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        if data == []:
                return jsonify({"message":"no todos to show"})
        
        output = []
        for i in data:
                output.append({"id":i[0],"description":i[1], "completed":i[2]})
        return jsonify({"todos": output})
        
@bp.route('/todo/<id>', methods = ['GET'])
@token_required
def get_one(current_user,id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select id from users where public_id = (%s)",(current_user,))
        u =  cur.fetchone()
        cur.execute("select * from data where id = (%s) and user_id = (%s);",(id,u[0]))
        data =  cur.fetchone()
        cur.close()
        conn.close()
        
        if data == None:
                output={"message": "no such todo exist"}
        else:
                output = {"id":data[0],"description":data[1],"completed":data[2]}
        return jsonify(output)
        
@bp.route('/todo/<id>', methods = ['PUT'])
@token_required
def complete_todo(current_user, id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select user_id from data where id = (%s);",(id,))
        u = cur.fetchone()[0]
        cur.execute("select public_id from users where id = (%s)",(u,))
        p_id = cur.fetchone()[0]
        if p_id != current_user:
                output = {"message" : "no such todo exist"}
        else:
                cur.execute("update data set completed = 1 where id = (%s);",(id,))
                conn.commit()
                output = {"mesaage" : "todo has been completed"}          
        cur.close()
        conn.close()

        return jsonify(output)
        
@bp.route('/todo/<id>', methods = ['DELETE'])
@token_required
def delete_todo(current_user, id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select user_id from data where id = (%s);",(id,))
        u = cur.fetchone()[0]
        cur.execute("select public_id from users where id = (%s)",(u,))
        p_id = cur.fetchone()[0]
        if p_id != current_user:
                output = {"message" : "no such todo exist"}
        else:
                cur.execute("delete from data where id = (%s);",(id,))
                conn.commit()
                output = {"mesaage" : "todo has been deleted"}  
        cur.close()
        conn.close()
        
        
        return jsonify(output)
        
@bp.route('/todo', methods = ['POST'])
@token_required
def add_todo(current_user):
        data = request.get_json()
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select id from users where public_id = (%s);",(current_user,))
        u = cur.fetchone()[0]
        cur.execute("insert into data (list,user_id) values (%s, %s);",(data['description'],u))
        conn.commit()
        cur.close()
        conn.close()
        
        output = {"message": "the task has been added"} 
        return jsonify(output)
        
@bp.route('/login')
def login():
        auth = request.authorization
        
        if not auth or not auth.username or not auth.password:
                return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})
        
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select * from users where username = (%s);",(auth.username,))
        user =  cur.fetchone()
        cur.close()
        conn.close()
        
        if not user:
                return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})
        if check_password_hash(user[3],auth.password):
                token = jwt.encode({'public id' : user[1], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, current_app.config['SECRET_KEY'])
                return jsonify({"token" : token})
                
        return make_response('Could not verify! username and password not matching', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})


@bp.route('/')
def f():
        return "<h1>This is a Webapi for a Todo App</h1>"        
        
