from sys import stderr
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import json, socket, os


app = Flask(__name__)
exiting = False

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://test:test@172.17.0.2:3306/auth' # Add your Database URI here
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)



class ServiceDetails(db.Model):
    _disableactivity = False
    serviceid = db.Column(db.String(30),primary_key=True)
    ipv4 = db.Column(db.String(20),nullable=False)
    port = db.Column(db.String(10),nullable=False)
    token = db.Column(db.String(30),nullable=False)

    def __repr__(self) -> str:
        if self._disableactivity:
            return
        return self.serviceid
    
    def save(self):
        if self._disableactivity:
            return
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        if self._disableactivity:
            return
        db.session.delete(self)
        db.session.commit()

class ServiceDetailsSchema(Schema):
    serviceid = fields.String()
    ipv4 = fields.String()
    port = fields.String()
    token = fields.String()




class UserDetails(db.Model):
    _disableactivity = False
    userid = db.Column(db.String(255),primary_key=True)
    username = db.Column(db.String(255),nullable=False)
    email = db.Column(db.String(255),nullable=False)
    description = db.Column(db.String(255),nullable=True)
    password = db.Column(db.String(255),nullable=False)
    firstname = db.Column(db.String(125),nullable=False)
    lastname = db.Column(db.String(125),nullable=False)
    phoneno = db.Column(db.String(20),nullable=False)

    def __repr__(self) -> str:
        if self._disableactivity:
            return
        return (self.firstname + ' ' + self.lastname)

    def save(self):
        if self._disableactivity:
            return
        db.session.add(self)
        db.session.commit()

    def delete(self):
        if self._disableactivity:
            return
        db.session.delete(self)
        db.session.commit()


class UserDetailsSchema(Schema):
    userid = fields.String()
    username = fields.String()
    email = fields.String()
    description = fields.String()
    password = fields.String()
    firstname = fields.String()
    lastname = fields.String()
    phoneno = fields.String()



@app.route('/signup',methods=['POST'])
def signUp():
    rawrequest = request.get_json()
    requestdata = rawrequest if type(rawrequest) == type(dict()) else json.loads(rawrequest)


    datamap = dict()
    for data in ["userid", "username", "email", "description", "password", "firstname", "lastname", "phoneno"]:
        datamap[data] = requestdata.get('data').get(data)

    newuser = UserDetails(
        userid = datamap["userid"],
        username = datamap["username"],
        email = datamap["email"],
        description = datamap["description"],
        password = datamap["password"],
        firstname = datamap["firstname"],
        lastname = datamap["lastname"],
        phoneno = datamap["phoneno"]
    )
    newuser.save()

    return jsonify(
        {
            "action" : "signingup",
            "data" : {
                "status" : "successful"
            }
        }
    ), 201

@app.route('/login',methods=['POST'])
def logIn():
    print("Fuc begining",file=stderr)
    rawrequest = request.get_json()
    requestdata = rawrequest if type(rawrequest) == type(dict()) else json.loads(rawrequest)

    print("Got json data",file=stderr)
    print("Json:",rawrequest,file=stderr)
    datamap = dict()
    for item in ["userid", "email", "password"]:
        datamap[item] = requestdata.get("data").get(item)

    # Check whether user exists
    # if UserDetails.query.get(datamap["userid"]).count() <= 0:
    #     return jsonify(
    #         {
    #             "action" : "loggingin",
    #             "data" : {
    #                 "status" : "failed",
    #                 "error_message" : "User does not exist" 
    #             }
    #         }
    #     ), 404

    serializer = UserDetailsSchema() 

    dbdata : any
    print("Before Xompare",file=stderr)
    if datamap["email"] is not None:
        print("Started getting user",file=stderr)
        user = UserDetails.query.filter_by(email=datamap["email"]).first()
        dbdata = serializer.dump(user)
        print("Working till getting db query",file=stderr)
    else:
        user = UserDetails.query.get(datamap["userid"])
        dbdata = serializer.dump(user)

    if datamap["password"] == dbdata.get('password'):
        print("Working till password match",file=stderr)
        return jsonify(
            {
                "action" : "loggingin",
                "data" : {
                    "status" : "successful",
                }
            }
        ), 200
    else:
        return jsonify(
            {
                "action" : "loggingin",
                "data" : {
                    "status" : "failed",
                    "error_message" : "Userid or password didn't matched"
                }
            }
        ), 403


@app.route('/verifypassword/<str:userid>/<str:passwrd>',methods=['GET'])
def verifyPassword(userid,passwrd):
    serializer = UserDetailsSchema()
    user : any
    try:
        user = serializer(UserDetails.query.get(userid))
    except Exception as err:
        print(err.args(),file=stderr)

    if user.get('password') != passwrd:
        return jsonify({
            "action" : "verifypassword",
            "data" : {
                "status" : "incorrect",
                "error_message" : "Password didn't match"
            }
        })
    
    return jsonify({
        "action" : "verifypassword",
        "data" : {
            "status" : "successful"
        }
    })


@app.route('/stopservice',methods=['POST'])
def stopService():
    service = ServiceDetails.query.get("authentication-service")
    service.delete()

    global exiting
    exiting = True

    return jsonify(
        {
            "action" : "stoppingservice",
            "data" : {
                "status" : "successful"
            }
        }
    )

@app.teardown_request
def teardown(exception):
    if exiting:
        os._exit(0)
    



def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(("8.8.8.8",80))
        ipv4 = s.getsockname()[0]
    except Exception:
        ipv4 = "127.0.0.1"
    finally:
        s.close()
    return ipv4


if __name__ == "__main__":
    service = ServiceDetails(
        serviceid = "authentication-service",
        ipv4 = getIp(),
        port = "44501",
        token = ""
    )
    service.save()

    serializer = ServiceDetailsSchema()
    # response = serializer.dump(ServiceDetails.query.get("enterprise-service-bus"))
    
    # ESB_TOKEN = response["token"]

    try:
        app.run(port=44501,debug=False)
    except RuntimeError as msg:
        if str(msg) == "Service is Shutting Down...":
            print("Service was shutdown by ESB")