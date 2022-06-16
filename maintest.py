import asyncio, json, websockets
from tests import Auth, Data, Msg, Esb


ESB_ADDRESS = "ws://127.0.0.1:5000/"



async def mainLoop(ws):
    testfor = choiceForTest()
    if testfor is None:
        print("Wrong selection!!!\n\n")
        return "keepalive", ws
    elif testfor == "stop":
        return "stop", ws

    ws = await execTest(testfor,ws)
    return "keepalive", ws

def choiceForTest() -> str | None:
    inp = str(input("Test for ? ('auth','data','msg')(Use 'stop' to exit): ")).lower()

    match inp:  
        case "auth":
            return "auth"
        case "data":
            return "data"
        case "msg":
            return "msg"
        case "stop":
            return "stop"
        case _:
            return None
    pass

async def execTest(test, ws):
    # inp = str(input("Specific Test for module or all? ('specific','all'): ")).lower()

    match test:  # Need to implement Feature
        case "auth":
            inp = str(input("Which test ? (signup,login): ")).lower()

            if inp == "signup":
                out = await Auth.signUp(ws)
                print("Output of Signin:")
                print(out)
                return ws
            elif inp == "login":
                out1, out2 = await Auth.logIn(ws)
                print("Output of Login:")
                print(out1 + '\n' + "Delayed Messages:" + '\n' + out2)
                return ws
            else:
                print("Wrong Selection ")
                return ws
            pass

        case "data":
            inp = str(input("Which test? (getUserDetails,updateUserDetails):")).lower()

            if inp == "getuserdetails":
                out = await Data.getUserDetails(ws)
                print("Output of getUserDetails:")
                print(out)
                return ws
            elif inp == "updateuserdetails":
                out = await Data.updateUserDetails(ws)
                print("Output of updateUserDetails:")
                print(out)
                return ws
            elif inp == "deleteuserdetails":
                out = await Data.deleteUserDetails(ws)
                print("Output of deleteUserDetails:")
                print(out)
                return ws
            else:
                print("Wrong Selection ")
                return ws

        case "msg", "specific":
            inp = str(input("Which Test?(message):")).lower()

            match inp:
                case "message":
                    out = await Msg.sendMessage(ws)

                    print("Output of sendMessage:")
                    print(out)
                    return ws

                case _:
                    print("Wrong Selection!!!")
                    return ws

        case _:
            return ws




async def main():
    async with websockets.connect("ws://127.0.0.1:5000") as ws:
        while(True):
            shouldstop, ws = await mainLoop(ws)
            if shouldstop == "stop":
                break
        ws.close()


if __name__ == "__main__":
    asyncio.run(main())
    pass
