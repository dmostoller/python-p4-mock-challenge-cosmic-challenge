#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientist_list = [scientist.to_dict(rules = ('-missions', )) for scientist in Scientist.query.all()]
        response = make_response(scientist_list, 200)
        
        return response
    
    def post(self):
        try:
            form_json = request.get_json()
            new_scientist = Scientist(
                name=form_json['name'],
                field_of_study=form_json['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            response = make_response(new_scientist.to_dict(), 201)
        except ValueError:
            response = make_response({"errors" : ["validation errors"]}, 400)

        return response
    
api.add_resource(Scientists, '/scientists')

class ScientistsById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            response = make_response(scientist.to_dict(), 200)
        else:
            response = make_response({"error" : "Scientist not found"}, 404)
        return response
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try:
                for attr in request.get_json():
                    setattr(scientist, attr, request.get_json()[attr])
                db.session.add(scientist)
                db.session.commit()
                response = make_response(scientist.to_dict(), 202)
            except ValueError:
                response = make_response({"errors" : ["validation errors"]}, 400)

        else:
            response = make_response({"error" : "Scientist not found"}, 404)
        
        return response
    
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            response = make_response({}, 204)
        else:
            response = make_response({"error" : "Scientist not found"}, 404)
        return response
        
api.add_resource(ScientistsById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets_list = [planet.to_dict(rules = ('-missions', )) for planet in Planet.query.all()]
        response = make_response(planets_list, 200)
        return response
api.add_resource(Planets, '/planets')    


class Missions(Resource):
    def post(self):
        try:
            form_json = request.get_json()
            new_mission = Mission(
                name=form_json['name'],
                scientist_id=form_json['scientist_id'],
                planet_id=form_json['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            response = make_response(new_mission.to_dict(), 201)
        except ValueError:
            response = make_response({"errors" : ["validation errors"]}, 400) 

        return response
    
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
