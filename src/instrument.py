import asyncio
import functools
import logging
import enum
from typing import Union
from dataclasses import dataclass
import json

import serial_asyncio 

logging.basicConfig(level=logging.DEBUG)

class Delimiter(enum.Enum):
    CRLF = b'\r\n'
    CR = b'\r'
    LF = b'\n'

class SerialProtocol(asyncio.Protocol):
    def __init__(self):
        self.ready_event = asyncio.Event()
        self.rBuffer = asyncio.Queue()
        self.transport = None
        self.timeout = 10.0

    def connection_lost(self, exc) -> None:
        logging.error("Connection: lost.")
        return super().connection_lost(exc)

    def connection_made(self, transport) -> None:
        """called when  the serial connection is established."""
        self.transport = transport
        logging.debug("Connection: connected.")
        self.ready_event.set()

    def data_received(self, data) -> None:
        """Handle incoming data."""
        try:
            data = data.decode('utf-8').rstrip('\r\n')
            if data:
                logging.debug(f"<< Receiving data: {data}")
                self.rBuffer.put_nowait(data)
                
        except UnicodeDecodeError as e:
            logging.error(f"Failed to decode data: {e}")
            return None

    def write_command(self, command: bytes, delimiter: Delimiter = Delimiter.CRLF) -> None:
        """Write command to the instrument as a byte string."""
        if not isinstance(command, (bytes)):
            logging.error("Data must be of type bytes")
            return None
        
        if self.transport is None or self.transport.is_closing():
            logging.warning("Connection: lost.")
            return None
        
        try:
            logging.debug(f">> Sending data: {command} + {delimiter.value}")
            self.transport.write(command + delimiter.value)
        except Exception as e:
            logging.error(f"Error while sending data: {e}")
            return None

    async def read_line(self) -> tuple[str, Union[str, None]]:
        """Read a line from the buffer with a timeout."""
        if self.transport is None or self.transport.is_closing():
            logging.error("Connection: lost.")
            return 'ER100', None

        try:
            line = await asyncio.wait_for(self.rBuffer.get(), timeout=self.timeout)

            if line is None:
                self.transport.close()
                logging.error("Connection error: No response received.")
                return 'ER101', None

            parts = line.split(',', 1)
            if len(parts) > 1:
                return parts[0], parts[1]
            else:
                return parts[0], None

        except asyncio.TimeoutError:
            if self.transport:
                self.transport.close()
            return 'ER101', None
        
        except Exception as e:
            if self.transport:
                self.transport.close()
            return 'ER99', None


class Instrument:

    @dataclass
    class ReadData:
        response: str
        code: int
        info: str
    
    async def Write(protocol: SerialProtocol, command: bytes):
        """Write to the instrument."""

        protocol.write_command(command)

    async def Read(protocol: SerialProtocol) -> ReadData:
        """Read response and check for errors."""

        err, response = await protocol.read_line()
        code, info = Instrument.check_error_code(err)

        if code != 0:
            print(f"Error: {info}")
            return Instrument.ReadData(None, code, info)

        return Instrument.ReadData(response, code, info)

    def connection(port: str ="COM4", baudrate: int=9600, protocol: asyncio.Protocol = SerialProtocol):
        """Decorator to handle serial connection."""

        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                loop = asyncio.get_running_loop()
                _transport, _protocol = await serial_asyncio.create_serial_connection(
                    loop, protocol, port, baudrate
                )
                try:
                    await _protocol.ready_event.wait()
                    return await func(_protocol, *args, **kwargs)
                finally:
                    _transport.close()

            return wrapper
        return decorator
    
    @staticmethod
    def check_error_code(error_code: str) -> tuple[int, str]:
        """Check the error code, raise an exception if it starts with 'ER'"""
        try:
            with open('./src/error_codes.json', 'r') as file:
                error_codes = json.load(file)

            meaning = error_codes.get(error_code, "Unknown error code.")

            if error_code.startswith("ER"):
                return 1, meaning
                
            return 0, meaning
                    
        except Exception as e:
            return 1, f'{e}'
