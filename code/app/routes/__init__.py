from flask_restful import Api
from app.resources.auth import Auth, Home
from app.routes.lstm import lstm_routes

def register_routes(app):
    api = Api(app)
    
    api.add_resource(Auth, '/auth')
    api.add_resource(Home, '/')
    lstm_routes(api)