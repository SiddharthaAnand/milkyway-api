from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os

app = Flask(__name__)

########################################################
#                     Database                         #
#                                                      #
########################################################

db = SQLAlchemy(app)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir) + 'planets'

@app.cli.db_create
def db_create():
    pass

@app.cli.db_seed
def db_seed():
    pass

@ app.cli.db_drop
def db_drop():
    pass

########################################################
#               ORM SQLAlchemy                         #
#                                                      #
########################################################

class Planets(db.Model):
    pass

class User(db.Model):
    pass

########################################################
#                Custom Routes                         #
#                                                      #
########################################################

@app.route('/planets', methods=['GET'])
def planets():
    pass