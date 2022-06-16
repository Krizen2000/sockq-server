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




@app.route('/getuserdetails/<string:userid>',methods=['GET'])
def getUserDetails(userid):
    querydataobj = UserDetails.query.get(userid)
    serializer = UserDetailsSchema()
    querydata = serializer.dump(querydataobj)

    return jsonify(
        {
            "action" : "gettinguserdetails",
            "data" : {
                "userid" : querydata.get('userid'),
                "username" : querydata.get('username'),
                "email" : querydata.get('email'),
                "description" : querydata.get('description'),
                "firstname" : querydata.get('firstname'),
                "lastname" : querydata.get('lastname'),
                "phoneno" : querydata.get('phoneno')
            }
        }
    ), 200

@app.route('/updateuserdetails',methods=['PUT'])
def updateUserDetails():
    rawrequest = request.get_json()
    requestdata = rawrequest if type(rawrequest) == type(dict()) else json.loads(rawrequest)

    # requestdata = dict()
    # for data in ["userid", "username", "email", "description", "firstname", "lastname", "phoneno"]:
        # requestdata[data] = requestdata.get("data").get(data)
    
    user = UserDetails.query.get(requestdata.get('data').get('userid'))
    user.username = requestdata.get('data').get('username')
    user.email = requestdata.get('data').get('email')
    user.description = requestdata.get('data').get('description')
    user.firstname = requestdata.get('data').get('firstname')
    user.lastname = requestdata.get('data').get('lastname')
    user.phoneno = requestdata.get('data').get('phoneno')
    user.save()
    return jsonify(
        {
            "action" : "updatinguserdetails",
            "data" : {
                "status" : "successful"
            }
        }
    ), 204

@app.route('/deleteuserdetails',methods=['POST'])
def deleteUserDetails():
    rawrequest = request.get_json()
    requestdata = rawrequest if type(rawrequest) == type(dict()) else json.loads(rawrequest)

    user : any
    try:
        user = UserDetails.query.get(requestdata.get('data').get('userid'))
    except Exception as err:
        print(err.args())
        return jsonify({
            "action" : "deletinguserdetails",
            "data" : {
                "status" : "failed",
                "error_message" : "User doesn't exist to delete"
            }
        })
    try:
        user.delete()
    except Exception as err:
        print(err.args(),file=stderr)
        return jsonify({
            "action" : "deletinguserdetails",
            "data" : {
                "status" : "failed",
                "error_message" : str(err.args())
            }
        })
    
    return jsonify({
        "action" : "deletinguserdetails",
        "data" : {
            "status" : "successful"
        }
    })

@app.route('/stopservice',methods=['POST'])
def stopService():
    service = ServiceDetails.query.get("user-data-service")
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
        serviceid = "user-data-service",
        ipv4 = getIp(),
        port = "44502",
        token = ""
    )
    service.save()

    serializer = ServiceDetailsSchema()

    try:
        app.run(port=44502)
    except RuntimeError as msg:
        if str(msg) == "Service Shutting Down...":
            print("Service has been Shutdown by ESB")
