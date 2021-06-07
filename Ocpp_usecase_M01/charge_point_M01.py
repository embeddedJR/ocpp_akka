import asyncio
import logging

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

    async def get_15118_ev_certificate(self):
        request = call.Get15118EVCertificatePayload(
            exi_request='Required. Raw CertificateInstallationReq request from EV, Base64 encoded',
            action='Install',
            iso15118_schema_version='urn:iso:15118:2:2013:MsgDef'
        )
        response = await self.call(request)

        if response.status == 'Accepted':
            print("Connected to central system.")


async def main():
    async with websockets.connect(
            'ws://localhost:9000/EVA_1',
            subprotocols=['ocpp2.0.1']
    ) as ws:

        charge_point = ChargePoint('EVA_1', ws)
        await asyncio.gather(charge_point.start(),
                             charge_point.get_15118_ev_certificate())


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
