import asyncio
import logging
from datetime import datetime

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp, call
from ocpp.v201 import call_result

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    async def get_log_request(self):
        request = call.GetLogRequestPayload(
            log_type='Diagnostics log',
            request_id=123456,
            log = {
                "remoteLocation": "The URL"
            }
        )
        response = await self.call(request)

        if response.status == 'Accepted':
            print("Connected to central system.")

    @on('LogStatusNotification')
    def on_log_status_notification(self, **kwargs):
        return call_result.LogStatusNotificationPayload(
            evse_id=12346,
            meter_value={
                'time_stamp':'current_time=datetime.utcnow().isoformat()',
                'sampled_value':[
                    {
                        'value':'12564356'
                    }
                ]
            }
        )

async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers[
            'Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. "
                     "Closing Connection")
        return await websocket.close()
        logging.error(
            "Client hasn't requested any Subprotocol. Closing Connection"
        )
        return await websocket.close()
    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        # In the websockets lib if no subprotocols are supported by the
        # client and the server, it proceeds without a subprotocol,
        # so we have to manually close the connection.
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    charge_point = ChargePoint(charge_point_id, websocket)

    await charge_point.start()


async def main():
    #  deepcode ignore BindToAllNetworkInterfaces: <Example Purposes>
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp2.0.1']
    )

    logging.info("Server Started listening to new connections...")
    await server.wait_closed()


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