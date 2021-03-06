from sys import stderr
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import requests, socket, json, os


app = Flask(__name__)
exiting = False

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://test:test@172.17.0.2:3306/auth' # Add your Database URI here
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy(app)

#Changed after getting values from Database
ESB_ADDRESS_v4 = None
ESB_PORT = None
ESB_TOKEN = None
ESB_URI = None
ESB_SEND_MESSAGE_URI = None



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
    desciption = db.Column(db.String(255),nullable=True)
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




class DelayedUserMessagingQueue(db.Model):
    _disableactivity = False
    id = db.Column(db.Integer(),primary_key=True)
    sender = db.Column(db.String(255),db.ForeignKey('user_details.userid'))
    receiver = db.Column(db.String(255),db.ForeignKey('user_details.userid'))
    message = db.Column(db.Text(),nullable=False)
    date = db.Column(db.DateTime(),nullable=False)

    def __repr__(self) -> str:
        if self._disableactivity:
            return
        return self.id

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


class DelayedUserMessagingQueueSchema(Schema):
    id = fields.Integer()
    sender = fields.String()
    receiver = fields.String()
    message = fields.String()
    date = fields.DateTime()




# ! The functionatity should be changed to check the contents of message for some dangerous stuff
# @app.route('/sendmessage',methods=['POST'])
# def sendMessage():
#     if ESB_SEND_MESSAGE_URI is None:
#         setESBInfo()

#     rawrequest = request.get_json()
#     requestdata = rawrequest if type(rawrequest) == type(dict()) else json.loads(rawrequest)
#     receiverid = requestdata.get("data").get("receiver")

#     response = requests.post(url=ESB_SEND_MESSAGE_URI,json=requestdata).json()

#     if response.get('data').get('status') != "successful":
#         delayedmessage = DelayedUserMessagingQueue(
#             receiver = receiverid,
#             sender = requestdata.get("data").get("sender"),
#             message = requestdata.get("data").get("message"),
#             date = requestdata.get("data").get("date")
#         )
#         delayedmessage.save()
#         return jsonify(
#             {
#                 "action" : "sendingmessage",
#                 "data" : {
#                     "status" : "pending"
#                 }
#             }
#         ), 102

#     return jsonify(
#         {
#             "action" : "sendingmessage",
#             "data" : {
#                 "status" : "sent"
#             }
#         }, 200
#     )


@app.route('/getdelayedmessages/<string:userid>',methods=["GET"])
def getDelayedMessages(userid):

    serializer = DelayedUserMessagingQueueSchema(many=True)
    delayedmessageentities : any
    try:
        delayedmessageentities = DelayedUserMessagingQueue.query.filter_by(receiver=userid)
    except Exception as e:
        print(e.args(),file=stderr)
        return jsonify({
            "action" : "getdelayedmessages",
            "data" : {
                "status" : "failed",
                "error_message" : "Some error occured while retrieving delayed messages"
            }
        })

    delayedmessages = serializer.dump(delayedmessageentities)
    print("DelayedMessages: ",delayedmessages,file=stderr)
    for message in delayedmessageentities:
        message.delete()
    
    return jsonify({
        "action" : "getdelayedmessages",
        "data" : {
            "status" : "successful",
            "messages" : delayedmessages
        }
    })

# ? Can store single message not list of them
@app.route('/storedelayedmessage',methods=['POST'])
def storeDelayedMessages():
    rawrequest = request.get_json()
    requestdata = rawrequest if type(rawrequest) == type(dict()) else json.loads(rawrequest)

    delayedmessage = DelayedUserMessagingQueue(
        sender = requestdata.get('data').get('sender'),
        receiver = requestdata.get('data').get('receiver'),
        message = requestdata.get('data').get('message'),
        date = requestdata.get('data').get('date')
    )

    try:
        delayedmessage.save()
    except Exception as err:
        print(err.args(),file=stderr)
        return jsonify({
            "action" : "storingdelayedmessage",
            "data" : {
                "status" : "failed",
                "error_message" : "Couldn't save the delayed message"
            }
        })

    return jsonify({
        "action" : "storingdelayedmessage",
        "data" : {
            "status" : "successful"
        }
    })

@app.route('/stopservice',methods=['POST'])
def stopService():
    service = ServiceDetails.query.get("user-messaging-service")
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

def setESBInfo():
    serializer = ServiceDetailsSchema()
    data = serializer.dump(ServiceDetails.query.get('enterprise-service-bus'))

    global ESB_ADDRESS_v4, ESB_PORT, ESB_URI, ESB_SEND_MESSAGE_URI
    ESB_ADDRESS_v4 = data.get('ipv4')
    ESB_PORT = data.get('port')
    ESB_URI = "http://" + ESB_ADDRESS_v4 + ":" + ESB_PORT
    ESB_SEND_MESSAGE_URI = ESB_URI + "/sendmessage"
    pass


if __name__ == "__main__":
    service = ServiceDetails(
        serviceid = "user-messaging-service",
        ipv4 = getIp(),
        port = "44503",
        token = ""
    )
    service.save()

    try:
        app.run(port=44503)
    except RuntimeError as msg:
        if str(msg) == "Service Shutting Down...":
            print("Service has been Shutdown by ESB")
