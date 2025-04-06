import asyncio
from src.instrument import Instrument as CS2000
from src.commands import Measure, MeasurementDataRead, MeasuringSwitchEnable, RemoteModeSelect
import pandas as pd
import numpy as np
import datetime

# @CS2000.connection(port='COM4', baudrate=9600)
# async def test(protocol):
#     RemoteModeSelect(protocol, 0)


# @CS2000.connection(port='COM4', baudrate=9600)
@CS2000.connection(port='/dev/cu.usbmodem12345678901', baudrate=9600)
async def _measure_read_store(protocol):
    """Performs the full measurement process"""

    # await CS2000.Write(protocol, b'MEAS,1')
    # measurement_time = await CS2000.Read(protocol)
    # is_finished = await CS2000.Read(protocol)

    await RemoteModeSelect(protocol, operation=1)
    await MeasuringSwitchEnable(protocol, operation=0)

    data = await Measure(protocol, operation=1)

    # spectral_irradiance_data_380nm_to_479nm = await MeasurementDataRead(protocol=protocol, data_mode=1, data_format=0, data_block_number_to_read=1)
    CS2000.Write(protocol, b'MEDR,1,0,1')
    spectral_irradiance_data_380nm_to_479nm = await CS2000.Read(protocol)

    # # spectral_irradiance_data_480nm_to_579nm = await MeasurementDataRead(protocol=protocol, data_mode=1, data_format=0, data_block_number_to_read=2)
    CS2000.Write(protocol, b'MEDR,1,0,2')
    spectral_irradiance_data_480nm_to_579nm = await CS2000.Read(protocol)

    # spectral_irradiance_data_580nm_to_679nm = await MeasurementDataRead(protocol=protocol, data_mode=1, data_format=0, data_block_number_to_read=3)
    CS2000.Write(protocol, b'MEDR,1,0,3')
    spectral_irradiance_data_580nm_to_679nm = await CS2000.Read(protocol)

    # spectral_irradiance_data_680nm_to_780nm = await MeasurementDataRead(protocol=protocol, data_mode=1, data_format=0, data_block_number_to_read=4)
    CS2000.Write(protocol, b'MEDR,1,0,4')
    spectral_irradiance_data_680nm_to_780nm = await CS2000.Read(protocol)

    # # colorimetric_data = await MeasurementDataRead(protocol=protocol, data_mode=0, data_format=0, data_block_number_to_read=1)
    CS2000.Write(protocol, b'MEDR,2,0,0')
    colorimetric_data = await CS2000.Read(protocol)

    CS2000.Write(protocol, b'MEDR,0,0,1')
    measurement_conditions = await CS2000.Read(protocol)

    await RemoteModeSelect(protocol, operation=0)

    print(len(spectral_irradiance_data_380nm_to_479nm.response))
    print(len(spectral_irradiance_data_480nm_to_579nm.response))
    print(len(spectral_irradiance_data_580nm_to_679nm.response))
    print(len(spectral_irradiance_data_680nm_to_780nm.response))

    spectral_data = np.concatenate(
        [
            spectral_irradiance_data_380nm_to_479nm.response,
            spectral_irradiance_data_480nm_to_579nm.response,
            spectral_irradiance_data_580nm_to_679nm.response,
            spectral_irradiance_data_680nm_to_780nm.response
        ]
    )

    wavelengths = np.arange(380, 781, 1)

    values = colorimetric_data.response

    colorimetric_dict = {
        key: float(value) for key, value in zip(CS2000.COLORIMETRIC_KEYS, values)
    }

    print("DEBUG: ", len(values), len(spectral_data), len(wavelengths))

    f = pd.DataFrame({
        "Wavelength (nm)": wavelengths,
        "Spectral Irradiance": spectral_data
    })

    for key, value in colorimetric_dict.items():
        f[key] = value

    # _ct = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    f.to_csv(f"measurement_data.csv", index=False)


def run_program(program, error_handler):
    try:
        asyncio.run(program())
    except Exception as e:
        error_handler(e)

def error_handler(e):
    print(f"An Error has happened: {e}")
    print("Shutting down...")



run_program(_measure_read_store, error_handler)