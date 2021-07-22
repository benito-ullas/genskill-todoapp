from flask import Blueprint, g, request, render_template, jsonify
from . import db
import psycopg2

bp = Blueprint('todo', __name__, url_prefix='/')


@bp.route('/todo')
def get_all():
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select * from data order by id;")
        data =  cur.fetchall()
        cur.close()
        conn.close()
        
        if data == []:
                return jsonify({"message":"no todos to show"})
        
        output = []
        for i in data:
                output.append({"id":i[0],"description":i[1], "completed":i[2]})
        return jsonify({"todos": output})
        
@bp.route('/todo/<id>', methods = ['GET'])
def get_one(id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("select * from data where id = (%s);",(id,))
        data =  cur.fetchone()
        cur.close()
        conn.close()
        
        if data == None:
                output={"message": "no such todo exist"}
        else:
                output = {"id":data[0],"description":data[1],"completed":data[2]}
        return jsonify(output)
        
@bp.route('/todo/<id>', methods = ['PUT'])
def complete_todo(id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("update data set completed = 1 where id = (%s);",(id,))
        conn.commit()
        cur.close()
        conn.close()
        
        output = {"message" : "the task has been completed"}
        return jsonify(output)
        
@bp.route('/todo/<id>', methods = ['DELETE'])
def delete_todo(id):
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("delete from data where id = (%s);",(id,))
        conn.commit()
        cur.close()
        conn.close()
        
        output = {"message" : "the task has been removed"}
        return jsonify(output)
        
@bp.route('/todo', methods = ['POST'])
def add_todo():
        data = request.get_json()
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("insert into data (list) values (%s);",(data['description'],))
        conn.commit()
        cur.close()
        conn.close()
        
        output = {"message": "the task has been added"} 
        return jsonify(output)

@bp.route('/')
def f():
        return "<h1>This is a Webapi for a Todo App</h1>"        
        
