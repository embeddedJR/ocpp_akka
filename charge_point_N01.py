import asyncio
import logging

from ocpp.routing import on

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)


from ocpp.v201 import call, call_result
from ocpp.v201 import ChargePoint as cp

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    @on('GetLogRequest')
    def on_get_log_request(self, action, **kwargs):
        return call_result.GetLogRequestPayload(
            status='Accepted',
            filename='Logfile'
        )


    async def log_status_notification(self):
        request = call.LogStatusNotificationPayload(
             status='Uploading',
             request_id=123
    )


async def main():
    async with websockets.connect(
            'ws://localhost:9000/EVA_1',
            subprotocols=['ocpp2.0.1']
    ) as ws:

        charge_point = ChargePoint('EVA_1', ws)
        await asyncio.gather(charge_point.start())


if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
