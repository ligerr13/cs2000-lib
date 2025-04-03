import asyncio
from src.instrument import Instrument as CS2000
from src.commands import Measure
import random

@CS2000.connection(port='COM4', baudrate=9600)
async def _test_1(protocol):
    data = await Measure(protocol)

    CS2000.Write(protocol, b'MEDR,1,0,1')
    spectral_irradiance_data_380nm_to_479nm = await CS2000.Read(protocol)

    CS2000.Write(protocol, b'MEDR,1,0,2')
    spectral_irradiance_data_480nm_to_579nm = await CS2000.Read(protocol)

    print(len(spectral_irradiance_data_480nm_to_579nm.response) == 8)

def run_test(program, error_handler):
    try:
        asyncio.run(program())
    except Exception as e:
        error_handler(e)

def error_handler(e):
    print(f"An Error has happened: {e}")
    print("Shutting down...")

run_test(_test_1, error_handler)
