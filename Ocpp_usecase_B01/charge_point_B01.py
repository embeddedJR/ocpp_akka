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


from ocpp.v201 import call
from ocpp.v201 import ChargePoint as cp

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):

    async def send_heartbeat(self, interval):
        request = call.HeartbeatPayload()
        while True:
            await self.call(request)
            await asyncio.sleep(interval)

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charging_station={
                'model': 'EVAcharge nG',
                'vendor_name': 'AKKA Germany GmbH',
                'firmware_version': 'SE-1.2.6',
                'serialNumber': '1234567890'
            },
            reason="PowerUp"
        )
        response = await self.call(request)

        if response.status == 'Accepted':
            print("Connected to central system.")
            await self.send_status_notification(response.interval)

    async def send_status_notification(self, interval):
        request = call.StatusNotificationPayload(
            timestamp=datetime.utcnow().isoformat(),
            connector_status='Available',
            evse_id=1234,
            connector_id=1
        )
        response = await self.call(request)
        await self.send_heartbeat(interval)


async def main():
    async with websockets.connect(
            'ws://localhost:9000/EVA_1',
            subprotocols=['ocpp2.0.1']
    ) as ws:

        charge_point = ChargePoint('EVA_1', ws)
        await asyncio.gather(charge_point.start(),
                             charge_point.send_boot_notification())


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
