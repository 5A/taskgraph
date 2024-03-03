# -*- coding: utf-8 -*-

"""ws.py:
Websocket connection manager, parser and authenticator.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231205"

# std libs
import logging
import asyncio
# third-party libs
from fastapi import WebSocket
from websockets.exceptions import ConnectionClosedOK
# own package
from .auth import validate_token_ws, TokenData, check_access_level_ws, UserAccessLevel

lg = logging.getLogger(__name__)


class WSApplicationProtocol():
    """
    Application protocol defined on WebSocket connection.
    When connected to the websocket endpoint, the initialize method is called once.
    Then the run method is awaited.
    When disconnected, the stop method is called.
    """

    def __init__(self, websocket: WebSocket, access_level: UserAccessLevel = UserAccessLevel.readonly) -> None:
        self.websocket = websocket
        self.access_level = access_level

    def initialize(self):
        lg.debug(
            "User connected to WebSocket, new instance of WSApplication Protocol initialized.")

    async def run(self):
        while True:
            received = await self.websocket.receive_json()
            # check user priviledge satistied for this endpoint.
            check_access_level_ws(self.access_level,
                                  UserAccessLevel.standard)
            response = {"echo": received}
            if "id" in received:
                # if user specifies a id in command, then we response with the same id to indicate task finish.
                response["id"] = received["id"]
            await self.websocket.send_json(response)

    def stop(self):
        lg.debug(
            "User disconnected from WebSocket, WSApplicationProtocol instance shutdown.")


class WSManagerItem():
    def __init__(self, websocket: WebSocket, protocol: WSApplicationProtocol, token: TokenData) -> None:
        self.websocket = websocket
        self.protocol = protocol
        self.token = token


class WebSocketConnectionManager:
    def __init__(self):
        self.wsid_i = 0
        self.active_connections: dict[int, WSManagerItem] = {}

    async def connect(self, websocket: WebSocket) -> int:
        """
        Connect to a websocket and wait for authentication message.
        If authentication fails, closes connection with WebSocket 1008 Policy Violation
        If everything is OK, initializes the websocket application protocol, then 
        returns internal id of the websocket, which can be used to access the websocket form
        outside the manager later.
        """
        # register at manager, but not authorized yet.
        await websocket.accept()
        # After connection established, the first message must be an authentication message.
        auth_data: dict = await websocket.receive_json()
        token_data = validate_token_ws(auth_data.get("token"))
        await websocket.send_json({"auth_result": "success"})
        # create application protocol instance if authentication is successful.
        proto = WSApplicationProtocol(
            websocket=websocket, access_level=token_data.access_level)
        proto.initialize()
        # register this websocket at manager active_connections KV storage.
        self.wsid_i += 1
        wsid = self.wsid_i
        self.active_connections[wsid] = WSManagerItem(
            websocket=websocket, protocol=proto, token=token_data)
        return wsid

    async def run(self, wsid: int):
        """
        Run the application protocol on the websocket connection specified by wsid.
        """
        await self.active_connections[wsid].protocol.run()

    def disconnect(self, wsid: int):
        """
        When a websocket closes, remove it from manager.
        Please note that this function is intended to be called when connection is closed. 
        But this function does NOT close the connection.
        """
        if wsid in self.active_connections:
            self.active_connections[wsid].protocol.stop()
            self.active_connections.pop(wsid)
        else:
            lg.info(
                "Cannot disconnect ws:{} from manager because it is not connected to this manager.".format(wsid))

    async def broadcast(self, message: dict):
        """
        Send a message to all authenticated connections.
        [NOTE]: For async programs, it is possible that .connect or .disconnect is called while awaiting
            the broadcast, causing the size of .active_connections dict to change, resulting in a RuntimeError.
            To avoid such race conditions, we copy the dict just before iteration. 
        """
        for wsid in list(self.active_connections.keys()).copy():
            if self.active_connections[wsid].token:
                # only send message to authenticated clients
                try:
                    await self.active_connections[wsid].websocket.send_json(message)
                except ConnectionClosedOK:
                    lg.warning(
                        "Client {} closed connection to server while broadcasting, skipping this client".format(wsid))

