from flask import Flask, g
from flask_cors import CORS

def create_app():
        app = Flask(__name__)
        CORS(app,resources={r"/*": {"origins": "*"}})
        app.config.from_mapping(DATABASE = 'todo' )
        app.config['SECRET_KEY'] = 'thisisthesecretkey'
        
        from . import routes, auth
        app.register_blueprint(routes.bp)
        app.register_blueprint(auth.bp)
                
        return app
        

