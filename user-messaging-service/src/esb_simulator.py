from sys import stderr
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_sock import Sock
from marshmallow import Schema, fields
import socket, requests, json, os


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://test:test@172.17.0.2:3306/auth' # Add your Database URI here
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)
exiting = False




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




@app.route('/sendmessage',methods=['POST'])
def sendMessage():
    rawrequest = request.get_json()
    requestdata = rawrequest if type(rawrequest) == type(dict()) else json.loads(rawrequest)
    userid = requestdata.get('data').get('receiver')

    print(requestdata.get('data').get('message'),file=stderr)

    if userid == "krizen88790":
        return jsonify({
            "action" : "sendingmessage",
            "data" : {
                "status" : "successful"
            }
        })
    elif userid == "krizen8879":
        return jsonify({
            "action" : "sendingmessage",
            "data" : {
                "status" : "successful"
            }
        })
    return jsonify({
        "action" : "sendingmessage",
        "data" : {
            "status" : "failed",
            "error_message" : "Client is offline"
        }
    })
    pass

@app.route('/stopservice',methods=['POST'])
def stopService():
    service = ServiceDetails.query.get("enterprise-service-bus")
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




if __name__ == "__main__":
    service = ServiceDetails(
        serviceid = "enterprise-service-bus",
        ipv4 = "127.0.0.1",
        port = "44500",
        token = ""
    )
    service.save()
    try:
        app.run(port=44500)
    except RuntimeError as msg:
        if str(msg) != "Service is Shutting Down...":
            exit()
