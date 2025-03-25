from dataclasses import dataclass
from src.instrument import Instrument, Delimiter

PORT = 'COM4'
BAUDRATE = 9600


@Instrument.connection(port=PORT, baudrate=BAUDRATE)
async def Measure(protocol, operation: int = 1):
    """
        `Performs measurement or cancels measurement in progress.`
        
        :param `protocol`: The protocol object used for communication.
        :param `operation`:

            - **0** - Cancel the current measurement.

            - **1** - Start a new measurement.
            
        :rtype: MeasureData
        :return: `MeasureData` containing the measurement time, completion status, and information.

    """

    @dataclass
    class MeasureData:
        measurement_time: str
        complete: int

    input_byte: bytes = b'MEAS,' + bytes([operation])

    await Instrument.Write(protocol, input_byte)

    measurement_time: str = await Instrument.Read(protocol)
    complete: str = await Instrument.Read(protocol)

    return MeasureData(measurement_time, complete)

@Instrument.connection(port=PORT, baudrate=BAUDRATE)
async def MeasuringSwitchEnable(protocol, operation: int = 1) -> None:
    """
       `Enables/disables the measuring button in remote mode.`
        
        :param `protocol`: The protocol object used for communication.
        :param `operation`:

            - **0** - Enable.

            - **1** - Disable.

        :rtype: None
        :return: None
        
    """

    input_byte: bytes = b'MSWE,' + bytes([operation])

    await Instrument.Write(protocol, input_byte)

    _: str = Instrument.Read()

@Instrument.connection(port=PORT, baudrate=BAUDRATE)
async def MeasurementDataRead(protocol, data_mode: int, data_format: int, data_block_number_to_read: int):
    """
        `Reads measurement data from instrument.`

        :param `data mode`: The protocol object used for communication.
        :param `data format`:
        :param `data block number to read`: 

    """
    
    input_byte: bytes = b'MEDR,' \
        + bytes([data_mode]) \
        + bytes([data_format]) \
        + bytes([data_block_number_to_read])

    await Instrument.Write(input_byte) 

    measurement_data = await Instrument.Read()

    return measurement_data

@Instrument.connection(port=PORT, baudrate=BAUDRATE)
async def SpectralIrradianceData(protocol, block_number: int):
    """
        `Reads spectral irradiance data from the instrument.`

        This function sends different commands to the instrument for spectral ranges (380-479 nm, 480-579 nm, 580-679 nm, and 680-780 nm).
        The data is retrieved from the instrument, and it is returned in a structured format as a list of values.
        
        :param `protocol`: The communication protocol used for the instrument (asyncio.Protocol).
        :param `block number`: The block number to determine which range to read (integer 1-4).
        
        :return: A `SpectralData` object containing a list of the measured spectral data for the different ranges.
    """

    @dataclass
    class SpectralData:
        data: list

    spectral_data = SpectralData(data=[])

    for block in range(1, 5):
        input_byte: bytes = b'MEDR,1,0,' + bytes([block])
        
        await Instrument.Write(protocol, input_byte)
        block_data = await Instrument.Read(protocol)

        spectral_data.data.append(block_data)

    return spectral_data

@Instrument.connection(port=PORT, baudrate=BAUDRATE)
async def ColorimetricData(protocol, block_number: int):
    """
        Reads colorimetric data from the instrument.
        
        This function sends different commands to the instrument based on the colorimetric data block number parameter.
        The data is retrieved from the instrument and returned.

        :param `protocol`: The communication protocol used for the instrument (asyncio.Protocol).
        :param `data_type`: The colorimetric data type to fetch (e.g., '01' for X,Y,Z).

        :return: The colorimetric data corresponding to the requested `block number`.
    """

    input_byte: bytes = b'MEDR,2,0,' + bytes(str(block_number), 'utf-8')
        
    await Instrument.Write(protocol, input_byte)
    block_data = await Instrument.Read(protocol)

    return block_data
