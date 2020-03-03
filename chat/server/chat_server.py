import sys
import time
import argparse
from chat.shared.configuration import MSG_TERMINATOR
import asyncio
from chat.shared.message import ChatMessage, Serializable, LogMessage, IntroductionMessage
import os
import logging
import dataclasses
import json
logger = logging.getLogger('basic')
logger.setLevel(logging.DEBUG)


class Connection:

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.incoming = asyncio.Queue()
        self.outcoming = asyncio.Queue()
        self.log = asyncio.Queue()
        self.is_open = True
        self.reader_task = None
        self.writer_task = None
        self.nickname = None

    async def handle_read(self):
        try:
            while self.is_open:
                data: bytes = await self.reader.readuntil(separator=MSG_TERMINATOR)
                data = data.strip(MSG_TERMINATOR)
                msg = Serializable.from_bytes(data)
                if type(msg) is LogMessage:
                    await self.log.put(msg)
                else:
                    logger.debug(f"got message: {ChatMessage.from_bytes(data)}")
                    await self.outcoming.put(data)
                    await self.log.put(LogMessage(msg.sender, "MESSAGE", msg.text, msg.timestamp))
        except ConnectionResetError as e:
            if e.args[0] == "Connection lost":  # linux error
                pass
            elif e.args[0] == 10054:  # win error
                pass
            else:
                raise  # raise any other case
        finally:
            self.close()

    async def handle_write(self):
        while self.is_open:
            try:
                message = await self.incoming.get()
                logger.info(f"Sending {ChatMessage.from_bytes(message)}")
                self.writer.write(message + MSG_TERMINATOR)
                await self.writer.drain()
            except Exception as e:
                logger.critical(e)

    async def start_handlers(self):
        try:
            self.reader_task = asyncio.create_task(self.handle_read())
            self.writer_task = asyncio.create_task(self.handle_write())
            await self.reader_task
            await self.writer_task
        except Exception as e:  # TODO: Fixme
            logger.critical(e)
            # if str(e) == "Task exception was never retrieved":
            #     pass
            # elif e.args[0] == "0 bytes read on a total of None expected bytes":
            #     pass
            # else:
            #     raise
        finally:
            self.close()

    def close(self):
        if self.is_open:
            self.is_open = False
            if self.reader_task:
                self.reader_task.cancel()
            if self.writer_task:
                self.writer_task.cancel()

    async def get_introduction_data(self):
        if not self.is_open:
            raise Exception("Connection has to be open")
        data: bytes = await self.reader.readuntil(separator=MSG_TERMINATOR)
        print(IntroductionMessage.from_bytes(data))
        return IntroductionMessage.from_bytes(data)


class Server:
    def __init__(self, host, port, output):
        self.start_time = time.time()
        self.host = host
        self.port = port
        self.connections = {}
        self.queue_handler = None
        self.log = asyncio.Queue()
        self.output = output

    async def run(self):
        server = await asyncio.start_server(self.open_connection, self.host, self.port)
        addr = server.sockets[0].getsockname()
        logger.info(f'Serving on {addr}')
        async with server:
            await server.serve_forever()

    async def handle_log(self, source, introduction: IntroductionMessage):
        base = os.path.join(self.output, introduction.name)
        os.makedirs(base, exist_ok=True)
        with open(os.path.join(base, 'info.json'), 'w') as jsonfile:
            json.dump(dataclasses.asdict(introduction), jsonfile)
        with open(os.path.join(base, "log.csv"), "w") as logfile:
            while True:
                obj: LogMessage = await source.get()
                obj.data = obj.data.replace("\n", "\\n")
                logger.info(obj)
                local = time.localtime(obj.timestamp)
                relative = obj.timestamp - self.start_time
                timestamp = time.strftime("%H:%M:%S", local) + "{:.4f}".format(obj.timestamp-int(obj.timestamp))[1:]
                logfile.write(f"{timestamp}, {relative}, {obj.type}, {obj.data}\n")
                if obj.type == "CLOSED":
                    return

    async def get_incoming_message_loop(self, connection):
        message = await self.connections[connection]["incoming"].get()
        logger.debug(f"Number of connections {len(self.connections)}")
        if len(self.connections.keys()) > 1:
            await asyncio.wait(list(self.connections[connection]["outcoming"].put(message) for connection in self.connections.keys() - {connection}), return_when=asyncio.ALL_COMPLETED)
        await self.get_incoming_message_loop(connection)

    async def open_connection(self, reader, writer):
        connection = Connection(reader, writer)
        introduction = await connection.get_introduction_data()
        connection.nickname = introduction.nickname
        await connection.log.put(LogMessage("server", "CONNECTED", "", time.time()))
        logger.info(f"Connection open with {introduction.nickname}")
        self.connections[connection] = {"incoming": connection.outcoming, "outcoming": connection.incoming}
        connection_handlers = asyncio.create_task(connection.start_handlers())
        logger_task = asyncio.create_task(self.handle_log(connection.log, introduction))
        queue_handling = asyncio.create_task(self.get_incoming_message_loop(connection))
        await connection_handlers
        await connection.log.put(LogMessage("server", "CLOSED", "", time.time()))
        queue_handling.cancel()
        await logger_task
        del self.connections[connection]
        logger.info(f"Connection closed with {introduction.nickname}")


def main(address, port, output):
    server = Server(address, port, output)
    asyncio.run(server.run())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default=os.path.dirname(__file__), help="Path to root folder of logs.")
    parser.add_argument("-a", "--addr", default="127.0.0.1", help="Address on which server will serve.")
    parser.add_argument("-p", "--port", default=5000, help="Port on which server will accept incoming connections.")
    args = parser.parse_args()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    main(address=args.addr, port=args.port, output=args.output)
