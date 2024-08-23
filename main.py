import yfinance as yf
from time import sleep
import json
import datetime
import os
from platform import system

# Setup
startFromFile = (False, None)  # A tuple with the format of (T/F, file path), file path defaults to ./save.json

# Global Variables
stock_name = "AMZN"
memory = []  # History of previous directions
choice = None
direction = None  # Direction of stock, -1 or 1 for down and up respectively.
total_cash = 0
stocks_owned = 0
os_name = system()
stock_value = None
stock = None


def clearScreen() -> None:
    if os_name == 'Windows':  # Windows and Linux have different clear commands
        os.system('cls')
    else:
        os.system('clear')


def isOpen() -> bool:
    dateModule = datetime.datetime.now()
    currentTime = int(dateModule.strftime("%H%M"))
    currentDay = dateModule.isoweekday() % 7

    if currentDay <= 5:
        daySpan = "Weekday"
    else:
        daySpan = "Weekend"

    if 1600 > currentTime >= 930 and daySpan == "Weekday":  # Is between 9:30 AM and 4 PM on a weekday.
        return True

    return False


def logic(currValue: int, prevValue: int) -> str:
    global choice, direction
    if currValue > prevValue:
        choice = "Sell?"
    elif currValue < prevValue:
        choice = "Buy?"
    else:
        choice = "Hold"

    if choice == "Sell?":
        operation = memory[-1] * -1
        if operation == direction:
            choice = "Sell"
        else:
            choice = "Hold"
    elif choice == "Buy?":
        operation = memory[-1] * -1
        if operation == direction:
            choice = "Buy"
        else:
            choice = "Hold"

    return choice


def file(operation: str, file_path: str = "./save.json") -> None:
    global stock_name, memory, total_cash, stocks_owned
    try:
        if operation == "read":
            data = json.load(fp=file_path)
            stock_name = data["data"]["stock"]
            memory = data["data"]["memory"]
            total_cash = data["data"]["total"]
            stocks_owned = data["data"]["owned"]
        elif operation == "write":
            store = {
                "data": {
                    "stock": stock_name,
                    "memory": memory,
                    "total": total_cash,
                    "owned": stocks_owned
                }
            }
            json.dump(store, file_path)
        else:
            raise SyntaxError(f"{operation} is not a valid operation.")
    except (FileNotFoundError, IOError) as e:
        print(f"There was a problem with a {operation} operation.")
        exit(e)


def init(checkRate: int = 60, firstCheck: bool = True) -> None:
    global stock
    while not isOpen():
        print("You are outside of stock trading hours.")
        sleep(checkRate)
        clearScreen()

    if firstCheck:
        print("Initializing stock framework...")
        stock = yf.Ticker(stock_name)
    stock_value = stock.history(period="1d")["Close"].iloc[-1]
    print(f"{stock_name} is currently at ${stock_value}")


def main(fileStart: tuple[bool, str]) -> None:
    global stocks_owned, total_cash, choice, direction
    sleepTime: int = 60

    if fileStart[0]:
        file("read", startFromFile[1] if startFromFile[1] is not None else None)
        # If you have no idea what this line above does,
        # then look up ternary operators in Python. :shrug:
    init(sleepTime, True)

    while True:
        if len(memory) > 10:  # Get some data first
            logic(stock_value, memory[-1])
            if choice == "Buy":
                stocks_owned += 1
                total_cash -= stock_value
            elif choice == "Sell" and stocks_owned >= 1:
                stocks_owned -= 1
                total_cash += stock_value
            else:
                choice = "Hold"

            print(f"""\nThe bot chose to {choice}.
You have {stocks_owned} stocks that are worth ${stocks_owned * stock_value}.
Your profit is ${total_cash}.\n""")

        if len(memory) > 1000:
            while len(memory) != 10:  # Declutter
                memory.pop(0)
        sleep(sleepTime)
        init(firstCheck=False)
        if stock_value > memory[-1]:
            direction = 1
        elif stock_value < memory[-1]:
            direction = -1
        else:
            direction = 0


if __name__ == "__main__":
    main(startFromFile)
