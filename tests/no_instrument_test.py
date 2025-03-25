import asyncio
from src.instrument import Instrument as CS2000
from src.commands import Measure
import random


@CS2000.connection(port="COM3")
async def simulateApp(protocol):
    await CS2000.Write(protocol, b"MEAS,1")
    measurement_time = await CS2000.Read(protocol)
    is_finished = await CS2000.Read(protocol)

@CS2000.connection(port="COM4")
async def simulateCS2000(protocol):
    await CS2000.Read(protocol)
    await asyncio.sleep(0.1)
    rnd_ms_time = random.uniform(5.0, 10.0)
    rnd_ms_time_bytes = f"{rnd_ms_time:.2f}".encode('utf-8')
    await CS2000.Write(protocol, b"OK00," + rnd_ms_time_bytes)
    await asyncio.sleep(rnd_ms_time)
    await CS2000.Write(protocol, b"OK00")
    await asyncio.sleep(0.1)

async def no_instrument_test():
    
    
    """ 
    Successful test:

    >> Sending data: b'MEAS,1' + b'\r\n'
    << Receiving data: MEAS,1
    >> Sending data: b'OK00,...ms' + b'\r\n'
    << Receiving data: OK00,...ms
    >> Sending data: b'OK00' + b'\r\n'
    << Receiving data: OK00

    """

    a = asyncio.create_task(simulateCS2000())
    b = asyncio.create_task(simulateApp())
    
    await asyncio.gather(b, a)

def run_test(program, error_handler):
    try:
        asyncio.run(program())
    except Exception as e:
        error_handler(e)

def error_handler(e):
    print(f"An Error has happened: {e}")
    print("Shutting down...")

run_test(Measure, error_handler)
