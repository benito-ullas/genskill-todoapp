from flask import Flask, g

def create_app():
        app = Flask(__name__)
        app.config.from_mapping(DATABASE = 'todo' )
        
        from . import routes, auth
        app.register_blueprint(routes.bp)
        app.register_blueprint(auth.bp)
                
        return app
