import websockets, json

class Auth:

    @staticmethod
    async def signUp(ws):
        jsoncontents = {
            "action" : "signingup",
            "data" : {
                "userid" : "krizen8",
                "username" : "krizen",
                "email" : "krizenknoz@gmail.com",
                "description" : "True Genius",
                "password" : "zawarudo",
                "firstname" : "Krizen",
                "lastname" : "Knoz",
                "phoneno" : "8897024870"
            }
        }

        await ws.send(json.dumps(jsoncontents).encode('utf-8'))
        responsejson = await ws.recv()
        # websockets.web
        response = json.loads(responsejson.decode('utf-8')) #if type(responsejson)==type(bytes) else json.load(responsejson)

        return response, ws
    
    @staticmethod
    async def logIn(ws):
        jsoncontents = {
            "action" : "loggingin",
            "data" : {
              "userid" : "krizen8",
              "email" : "kri@gm.com",
              "password" : "zaworudo"
            } 
        }

        await ws.send(json.dumps(jsoncontents).encode('utf-8'))
        responsejson = await ws.recv()
        response1 = json.loads(responsejson.decode('utf-8'))
        responsejson = await ws.recv()
        response2 = json.loads(responsejson.decode('utf-8'))

        return response1, response2, ws
    
class Data:

    @staticmethod
    async def getUserDetails(ws):
        jsoncontents = {
            "action" : "gettinguserdetails",
            "data" : {
                "userid" : "krizen8"
            }
        }

        await ws.send(json.dumps(jsoncontents).encode('utf-8'))
        responsejson = await ws.recv()
        response = json.loads(responsejson.decode('utf-8'))

        return response, ws
    
    @staticmethod
    async def updateUserDetails(ws):
        jsoncontents = {
            "action" : "updatinguserdetails",
            "data" : {
                "userid" : "krizen8",
                "username" : "KrizenLOL",
                "email" : "krizee@gmail.com",
                "description" : "...",
                "firstname" : "Krizen",
                "lastname" : "Knoz",
                "phoneno" : "6897033332"
            }
        }

        await ws.send(json.dumps(jsoncontents).encode('utf-8'))
        responsejson = await ws.recv()
        response = json.loads(responsejson.decode('utf-8'))

        return response, ws

    @staticmethod
    async def deleteUserDetails(ws):
        jsoncontents = {
            "action" : "deletinguserdetails",
            "data" : {
                "password" : "zawarudo"
            }
        }

        await ws.send(json.dumps(jsoncontents).encode('utf-8'))
        responsejson = await ws.recv()
        response = json.loads(responsejson.decode('utf-8'))
        
        return response, ws

class Msg:

    @staticmethod
    async def sendMessage(ws):
        jsoncontents = {
            "action" : "sendingmessage",
            "data" : {
                "receiver" : "krizen88790",
                "message" : "Hello from the ESB Testing Module"
            }
        }

        await ws.send(json.dumps(jsoncontents).encode('utf-8'))
        responsejson = await ws.recv()
        response = json.loads(responsejson.decode('utf-8'))

        return response, ws

class Esb:

    @staticmethod
    async def stopService(ws):
        jsoncontents = {
            "action" : "stoppingservice",
            "data" : {
                "stoptoken" : "stoptheserver"
            }
        }

        await ws.send(json.dumps(jsoncontents).encode('utf-8'))
        responsejson = await ws.recv()
        response = json.loads(responsejson.decode('utf-8'))

        return response, ws