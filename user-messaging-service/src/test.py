import requests, json, datetime


MSG_SERVICE = "http://127.0.0.1:44503"
MSG_SERVICE_SENDMSG = MSG_SERVICE + "/sendmessage"
MSG_SERVICE_SENDDELAYEDMSG = MSG_SERVICE + "/sendelayedmessage"
MSG_SERVICE_STOPSERVICE = MSG_SERVICE + "/stopservice"
ESB_SERVICE_STOPSERVICE = "http://127.0.0.1:44500/stopservice"


def main():
    while True:
        if mainLoop() is None:
            break
    return


def mainLoop():
    inp = str(input("Enter which test? (msg,delayedmsg,stop): ")).lower()

    match inp:
        case "msg":
            jsoncontents = {
                "action" : "sendingmessage",
                "data" : {
                    "sender" : "krizen8879",
                    "receiver" : "krizen88790",
                    "message" : "Hello from test",
                    "date" : str(datetime.datetime.now())
                }
            }
            response = requests.post(url=MSG_SERVICE_SENDMSG,json=jsoncontents).json()
            print("Response Contents are: ")
            print(json.dumps(response))
            return 0
        case "delayedmsg":
            jsoncontents = {
                "action" : "sendingdelayedmessage",
                "data" : {
                    "userid" : "krizen8879"
                }
            }
            response = requests.post(url=MSG_SERVICE_SENDDELAYEDMSG,json=jsoncontents).json()
            print("Response Contents are: ")
            print(json.dumps(response))
            return 0
        case "stop":
            try: 
                requests.post(url=MSG_SERVICE_STOPSERVICE) 
            except Exception: 
                pass
            try:
                requests.post(url=ESB_SERVICE_STOPSERVICE)
            except Exception:
                pass
            return None
        case _:
            print("Wrong Option Selected!!!\n\n")
            return 0
    pass



if __name__ == "__main__":
    main()
