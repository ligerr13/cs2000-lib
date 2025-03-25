from src.instrument import Instrument as CS2000
import asyncio

@CS2000.connection
async def measure_test_1(protocol):

    """ 
    Successful test: 

    >> Sending data: b'MEAS,1' + b'\r\n'
    << Receiving data: OK00,...
    << Receiving data: OK00

    """

    await CS2000.Write(protocol, b'MEAS,1')
    measurement_time = await CS2000.Read(protocol)
    is_finished = await CS2000.Read(protocol)

async def measure_test_2(protocol):

    """ 
    Successful test: 

    >> Sending data: b'MEAS,1' + b'\r\n'
    << Receiving data: OK00,...
    >> Sending data: b'MEAS,1' + b'\r\n'
    << Receiving data: ER02
    Error: "Measurement in process, the received command cannot be processed because the instrument is currently taking a measurement."

    """

    await CS2000.Write(protocol, b'MEAS,1')
    measurement_time = await CS2000.Read(protocol)
    await CS2000.Write(protocol, b'MEAS,1')


def run_program(program, error_handler):
    try:
        asyncio.run(program())
    except Exception as e:
        error_handler(e)

def error_handler(e):
    print(f"An Error has happened: {e}")
    print("Shutting down...")


run_program(measure_test_1, error_handler)
# run_program(measure_test_2, error_handler)