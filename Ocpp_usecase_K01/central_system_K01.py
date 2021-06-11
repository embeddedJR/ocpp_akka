import asyncio
import logging
from datetime import datetime

from ocpp import charge_point
import pickle
try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)

from ocpp.routing import on, after
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call
from ocpp.v201 import call_result


logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    async def set_charging_profile_request(self):
        request = call.SetChargingProfilePayload(
            evse_id=123456,
            charging_profile={
                "id": 86087905,
                "stackLevel": -42295823,
                "chargingProfilePurpose": "TxProfile",
                "chargingProfileKind": "Recurring",
                "chargingSchedule": [
                    {
                        "id": 10452648,
                        "chargingRateUnit": "A",
                        "chargingSchedulePeriod": [
                            {
                                "startPeriod": 91941227,
                                "limit": -27956571.491987333
                            }
                        ]
                    }
                ]
            }
        )

        response = await self.call(request)
        if response.status == 'Accepted':
            print("SetChargingProfile  accepted")
            with open('request.txt','wb') as outfile:
                pickle.dump(request,outfile)

            
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

    await asyncio.gather(charge_point.start(),
                         charge_point.set_charging_profile_request())

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
