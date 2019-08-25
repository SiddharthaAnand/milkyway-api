from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message


app = Flask(__name__)


app.config['JWT_SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
mail = Mail(app)


########################################################
#                     Database                         #
#                                                      #
########################################################

db = SQLAlchemy(app)
ma = Marshmallow(app)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'planets.db')

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
#              Database Models                         #
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


########################################################
#               Marshmallow usage                      #
#         serialization/deserialization of data        #
########################################################

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


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists'), 409
    else:
        name = request.form['name']
        password = request.form['password']
        user = User(name=name,
                    password=password,
                    email=email)
        db.session.add(user)
        db.session.commit()
        return jsonify(message='User created successfully!'), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']

    else:
        email = request.form['email']
        password = request.form['password']

    test = User.query.filter_by(email=email, password=password).first()

    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message='Login succeeded!', access_token=access_token)
    else:
        return jsonify(message='Bad email or password'), 401


@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("your MilkyWay API password is " + user.password,
                      sender='admin@planetary.com',
                      recipients=[email])
        mail.send(msg)
        return jsonify(message='Password sent to ' + email)
    else:
        return jsonify(message="That email doesnt exist"), 401


@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result.data)
    else:
        return jsonify(message='Planet does not exist!'), 404


if __name__ == '__main__':
    app.run()