import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

IB_HOST = '127.0.0.1'
IB_PORT = 7497
IB_CLIENT_ID = 5026904


def fetch_managed_accounts():
    class ibkr_app(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.error_messages = pd.DataFrame(columns=[
                'reqId', 'errorCode', 'errorString'
            ])
            self.managed_accounts = []

        def error(self, reqId, errorCode, errorString):
            print("Error: ", reqId, " ", errorCode, " ", errorString)

        def managedAccounts(self, accountsList):
            self.managed_accounts = [i for i in accountsList.split(",") if i]

    app = ibkr_app()

    app.connect(IB_HOST, IB_PORT, IB_CLIENT_ID)
    while not app.isConnected():
        time.sleep(0.5)

    print('connected')

    def run_loop():
        app.run()

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while len(app.managed_accounts) == 0:
        time.sleep(0.5)

    print('handshake complete')
    app.disconnect()

    return app.managed_accounts


def req_historical_data(tickerId, contract, endDateTime, durationStr,
                        barSizeSetting, whatToShow, useRTH):
    class ibkr_app(EWrapper, EClient):
        def __init__(self):
            EClient.__init__(self, self)
            self.error_messages = pd.DataFrame(columns=[
                'reqId', 'errorCode', 'errorString'
            ])
            self.historical_data = pd.DataFrame(columns=[
                'date', 'value'
            ])
            self.setServerLogLevel(5)
            self.nextValidOrderId = None

        def error(self, reqId, errorCode, errorString):
            if errorCode < 2100 or errorCode >= 2200:
                print("Error: ", reqId, " ", errorCode, " ", errorString)

        def disconnect(self):
            super().disconnect()
            print('DISCONNECT triggered')

        def nextValidId(self, orderId: int):
            print(f"Received nextValidId={orderId}")
            self.nextValidOrderId = orderId
            self.start()

        def start(self):
            print('Triggering historical data request...')
            self.reqHistoricalData(tickerId, contract, endDateTime, durationStr,
                                   barSizeSetting, whatToShow, 1,
                                   1, False, [])
            print('Finished triggering historical data request')

        def historicalData(self, reqId, bar):
            # YOUR CODE GOES HERE: Turn "bar" into a pandas dataframe, formatted
            #   so that it's accepted by the plotly candlestick function.
            # Take a look at candlestick_plot.ipynb for some help!
            # assign the dataframe to self.historical_data.
            test = pd.DataFrame([['abc', 1], ['def', 2]],
                                columns=['date', 'value'])
            self.historical_data = pd.concat([self.historical_data, test])
            print(reqId, bar)

        def historicalDataEnd(self, reqId: int, start: str, end: str):
            print(f"Finished receiving historical data for reqId={reqId} from={start} to={end}")
            self.disconnect()

    app = ibkr_app()
    app.connect(IB_HOST, IB_PORT, IB_CLIENT_ID)
    while not app.isConnected():
        print("Waiting for connection...")
        time.sleep(0.5)
    print('connected')

    def run_loop():
        app.run()

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # As long as the historical data instance variable has no rows, wait
    #  until you receive it from the socket:
    while app.historical_data.empty:
        print("Waiting for historical data...")
        time.sleep(1)

    # When you've got it, return it:
    return app.historical_data


eurusd_contract = Contract()
eurusd_contract.symbol = 'EUR'
eurusd_contract.secType = 'CASH'
eurusd_contract.exchange = 'IDEALPRO'
eurusd_contract.currency = 'USD'
