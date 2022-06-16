from sys import stderr
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_sock import Sock
from simple_websocket import ConnectionClosed, ConnectionError
from marshmallow import Schema, fields
import socket, requests, json, datetime, os


app = Flask(__name__)
exiting = False

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://test:test@172.17.0.2:3306/auth' # Add your Database URI here
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval' : 25}

sock = Sock(app)
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




SERVICE_TOKENS = dict()
SERVICE_IPADDRESSES = dict()
SERVICE_PORTS = dict()
SERVICE_URIS = dict()


# List of user ids
online_userids = list()
# Dict containing UserID WebSocket pair
online_users = dict()




@sock.route('/')
def clientListener(ws):
    global online_userids
    global online_users
    client_userid : str = None
    connected = True

    while connected:
        try:
            datajson = ws.receive()
        except ConnectionClosed as cc:
            print("Connection with client: ",client_userid," is closed.",file=stderr)
            if client_userid is None:
                connected = False
                continue
            online_userids.remove(client_userid)
            online_users.pop(client_userid)
        except ConnectionError as ce:
            print("Error Occured with client: ",client_userid,". Coonection is closed.",file=stderr)
            if client_userid is None:
                connected = False
                continue
            online_userids.remove(client_userid)
            online_users.pop(client_userid)

        data = json.loads(datajson.decode('utf-8'))
        print(data,file=stderr)

        action = data.get('action')

        match action:
            case "signingup":
                response = requests.post(url=SERVICE_URIS["signup"],json=data).json()
                ws.send(json.dumps(response).encode('utf-8'))

                if response.get('data').get('status') != "successful":
                    connected = False
                    continue

                client_userid = data.get('data').get('userid')
                online_userids.append(client_userid)
                online_users[client_userid] = ws

            case "loggingin":
                response = requests.post(url=SERVICE_URIS["login"],json=data).json()
                ws.send(json.dumps(response).encode('utf-8'))

                if response.get('data').get('status') != "successful":
                    connected = False
                    continue

                client_userid = data.get('data').get('userid')
                online_userids.append(client_userid)
                online_users[client_userid] = ws

                # Request Delayed Messages if exist
                response = requests.get(url=( SERVICE_URIS["getdelayedmessages"] + '/' + client_userid ))
                ws.send(json.dumps(response).encode('utf-8'))

            case "gettinguserdetails" if client_userid is not None:
                custom_uri = SERVICE_URIS["getuserdetails"] + "/" + data.get('data').get('userid')
                response = requests.get(url=custom_uri).json()
                ws.send(json.dumps(response).encode('utf-8'))

            case "updatinguserdetails" if client_userid is not None:
                data["data"]["userid"] = client_userid
                response = requests.post(url=SERVICE_URIS["updateuserdetails"],json=data).json()
                ws.send(json.dumps(response).encode('utf-8'))

            case "deletinguserdetails" if client_userid is not None:
                data["data"]["userid"] = client_userid
                passwrd = data.get('data').get('password')
                response = requests.get(url=( SERVICE_URIS["verifypassword"]+'/'+client_userid+'/'+passwrd)).json()

                if response.get('data').get('status') != "successful":
                    ws.send(json.dumps(response).encode('utf-8'))
                    continue

                response = requests.post(url=SERVICE_URIS["deleteuserdetails"],json=data).json()

                if response.get('data').get('status') != "successful":
                    ws.send(json.dumps(response).encode('utf-8'))
                    continue

                online_userids.remove(client_userid)
                online_users.pop(client_userid)
                client_userid = None
                connected = False

            case "sendingmessage" if client_userid is not None:
                data['data']['sender'] = client_userid
                data['data']['date'] = str(datetime.datetime.now())

                # Stores Delayec messages
                if data.get('data').get('receiver') not in client_userid:
                    response = requests.post(url=SERVICE_URIS["storedelayedmessage"],json=data).json()

                    if response.get('data').get('status') != "successful":
                        ws.send(json.dumps({
                            "action" : "sendingmessage",
                            "data" : {
                                "status" : "failed",
                                "error_message" : response.get('data').get('error_message')
                            }
                        }))
                        continue

                    ws.send(json.dumps({
                        "action" : "sendingmessage",
                        "data" : {
                            "status" : "successful"
                        }
                    }))
                    continue
                
                # Sends the message by getting the websocket from the global dict
                recv_ws = online_users.get(data.get('data').get('receiver'))
                recv_ws.send(json.dumps(data))

                # ws.send(json.dumps(response).encode('utf-8'))

            # Used by Admins to stop Server
            case "stoppingservice" if data.get('data').get('stoptoken') == "stoptheserver":
                service = ServiceDetails.query.get("enterprise-service-bus")
                service.delete()

                try:
                    requests.post(url=('http://' + SERVICE_IPADDRESSES["authentication-service"] + ':' + SERVICE_PORTS["authentication-service"] + '/stopservice'))
                except Exception:
                    pass
                try:
                    requests.post(url=('http://' + SERVICE_IPADDRESSES["user-data-service"] + ':' + SERVICE_PORTS["user-data-service"] + '/stopservice'))
                except Exception:
                    pass
                try:
                    requests.post(url=('http://' + SERVICE_IPADDRESSES["user-messaging-service"] + ':' + SERVICE_PORTS["user-messaging-service"] + '/stopservice'))
                except Exception:
                    pass
                
                ws.send(json.dumps({
                    "action" : "stoppingservice",
                    "data" : {
                        "status" : "successful"
                    }
                }).encode('utf-8'))

                # Close all the websockets with a message json and then shutdown the server

                global exiting
                exiting = True

            case _ if client_userid is not None:
                response = {
                    "action" : action,
                    "data" : {
                        "status" : "failed",
                        "error_message" : "Provided action is not in the API"
                    }
                }
                ws.send(json.dumps(response).encode('utf-8'))

            case _:
                response = {
                    "data" : {
                        "error_message" : "Not authenticated to use the API"
                    }
                }
                connected = False
                ws.send(json.dumps(response).encode('utf-8'))
                ws.close()

        # Add a Log Out feature and also change active users if ping times out




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
        serviceid = "enterprise-service-bus",
        ipv4 = getIp(),
        port = "5000",
        token = ""
    )
    service.save()

    #Get all Netork Details of other Services
    serviceserializer = ServiceDetailsSchema(many=True)
    servicesobjlist = ServiceDetails.query.filter(ServiceDetails.serviceid != "enterprise-service-bus").all()
    serviceslist = serviceserializer.dump(servicesobjlist)
    for service in serviceslist:
        SERVICE_IPADDRESSES[service.get('serviceid')] = service.get('ipv4')
        SERVICE_PORTS[service.get('serviceid')] = service.get('port')
        print("Value of serv id: ",service.get('serviceid'),"\nValue of serv ip: ",service.get('ipv4'),"\nValue of serv port: ",service.get('port'),file=stderr)

    # Caching Service URIs
    SERVICE_URIS["signup"] = 'http://' + SERVICE_IPADDRESSES["authentication-service"] + ':' + SERVICE_PORTS["authentication-service"] + '/signup'
    SERVICE_URIS["login"] = 'http://' + SERVICE_IPADDRESSES["authentication-service"] + ':' + SERVICE_PORTS["authentication-service"] + '/login'
    SERVICE_URIS["verifypassword"] = 'http://' + SERVICE_IPADDRESSES["authentication-service"] + ':' + SERVICE_PORTS["authentication-service"] + '/verifypassword'
    SERVICE_URIS["getuserdetails"] = 'http://' + SERVICE_IPADDRESSES["user-data-service"] + ':' + SERVICE_PORTS["user-data-service"] + '/getuserdetails'
    SERVICE_URIS["updateuserdetails"] = 'http://' + SERVICE_IPADDRESSES["user-data-service"] + ':' + SERVICE_PORTS["user-data-service"] + '/updateuserdetails'
    SERVICE_URIS["deleteuserdetails"] = 'http://' + SERVICE_IPADDRESSES["user-data-service"] + ':' + SERVICE_PORTS["user-data-service"] + '/deleteuserdetails'
    SERVICE_URIS["sendmessage"] = 'http://' + SERVICE_IPADDRESSES["user-messaging-service"] + ':' + SERVICE_PORTS["user-messaging-service"] + '/sendmessage'
    SERVICE_URIS["storedelayedmessage"] = 'http://' + SERVICE_IPADDRESSES["user-messaging-service"] + ':' + SERVICE_PORTS["user-messaging-service"] + '/storedelayedmessage'
    SERVICE_URIS["getdelayedmessages"] = 'http://' + SERVICE_IPADDRESSES["user-messaging-service"] + ':' + SERVICE_PORTS["user-messaging-service"] + '/getdelayedmessages'

    print("Value of SERVICE_URIS[\"signup\"]: ",SERVICE_URIS["signup"],file=stderr)
    print("Value of SERVICE_URIS[\"login\"]: ",SERVICE_URIS["login"],file=stderr)

    try:
        app.run(port=5000)
    except RuntimeError as msg:
        if str(msg) != "Service is Shutting Down...":
            exit()