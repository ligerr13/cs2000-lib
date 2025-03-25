import asyncio
from src.instrument import Instrument as CS2000

@CS2000.connection(port='COM4', baudrate=9600)
async def measure_and_read(protocol):
    """Performs the full measurement process"""

    await CS2000.Write(protocol, b'MEAS,1')
    measurement_time = await CS2000.Read(protocol)
    is_finished = await CS2000.Read(protocol) 
    
    await CS2000.Write(protocol, b'MEDR,1,0,1')
    spectral_irradiance_data_380nm_to_479nm = await CS2000.Read(protocol)

    await CS2000.Write(protocol, b'MEDR,1,0,2')
    spectral_irradiance_data_480nm_to_579nm = await CS2000.Read(protocol)

    await CS2000.Write(protocol, b'MEDR,1,0,3')
    spectral_irradiance_data_580nm_to_679nm = await CS2000.Read(protocol)

    await CS2000.Write(protocol, b'MEDR,1,0,4')
    spectral_irradiance_data_680nm_to_780nm = await CS2000.Read(protocol)

    await CS2000.Write(protocol, b'MEDR,2,0,0')
    colorimetric_data = await CS2000.Read(protocol)

    await CS2000.Write(protocol, b'MEDR,0,0,1')
    measurement_conditions = await CS2000.Read(protocol)


def run_program(program, error_handler):
    try:
        asyncio.run(program())
    except Exception as e:
        error_handler(e)

def error_handler(e):
    print(f"An Error has happened: {e}")
    print("Shutting down...")


run_program(measure_and_read, error_handler)