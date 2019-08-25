from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow

app = Flask(__name__)

########################################################
#                     Database                         #
#                                                      #
########################################################

db = SQLAlchemy(app)
ma = Marshmallow(app)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir) + 'planets'

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print 'Database created!'

@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(id=1,
                     name='Mercury',
                     distance=120000,
                     radius=1200,
                     home_star="Sun",
                     mass=1900000000,
                     )
    venus = Planet(id=2,
                     name='Venus',
                     distance=120000,
                     radius=1200,
                     home_star="Sun",
                     mass=1900000000,
                     )

    db.session.add(mercury)
    db.session.add(venus)

    test_user = User(id=1,
                     name="Siddhartha",
                     email='sido@gmail.com',
                     password='abcde')

    db.session.add(test_user)
    db.session.commit()
    print 'Database seeded!'


@ app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print 'Database dropped!'

########################################################
#               ORM SQLAlchemy                         #
#                                                      #
########################################################


class Planet(db.Model):
    __tablename__ = 'planets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    distance = Column(Float)
    radius = Column(Float)
    mass = Column(Float)
    home_star = Column(String)


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'password')


class PlanetSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'distance', 'radius', 'mass', 'home_star')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

########################################################
#                Custom Routes                         #
#                                                      #
########################################################


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result.data)

if __name__ == '__main__':
    app.run()