import asyncio, datetime, sys, random
from vulcan import Keystore, Account, VulcanHebe

async def setup():
    try:
        with open("keystore.json", 'r') as file:
            keystore = Keystore.load(file.read())
    except FileNotFoundError:
        print("No keystore found! Creating")
        keystore = Keystore.create()
    
    try:
        with open("account.json", 'r') as file:
            account = Account.load(file.read())
    except FileNotFoundError:
        print("No account registered!")
        token = input("Please, tell me your token: ")
        symbol = input("Next is your symbol: ")
        pin = input("And lastly, pin: ")
    
        account = await Account.register(keystore, token, symbol, pin)
        with open("account.json", 'w') as file:
            file.write(account.as_json)
    
    with open("keystore.json", "w") as file:
        file.write(keystore.as_json)

    client = VulcanHebe(keystore, account)
    await client.select_student()
    return client
