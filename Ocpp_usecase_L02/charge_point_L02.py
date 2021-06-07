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


from ocpp.v20 import call
from ocpp.v20 import call_result
from ocpp.v20 import ChargePoint as cp

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    @on('UpdateFirmware')
    def on_update_firmware(self, **kwargs):
        print('Got a UpdateFirmwareRequest!')
        return call_result.UpdateFirmwarePayload(
            status = 'Accepted'
        )

    async def send_firmware_status_notification(self):
        await asyncio.sleep(10)
        for i in ['Downloading', 'Downloaded', 'Installing', 'Installed']:
             request = call.FirmwareStatusNotificationPayload(
                request_id=123,
                status=i)
             await self.call(request)
             await asyncio.sleep(5)

async def main():
    async with websockets.connect(
            'ws://localhost:9000/CP_1',
            subprotocols=['ocpp2.0.1']
    ) as ws:

        charge_point = ChargePoint('EVA_1', ws)
        await asyncio.gather(charge_point.start(),
                             charge_point.send_firmware_status_notification()
                             )


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
