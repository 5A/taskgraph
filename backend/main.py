# -*- coding: utf-8 -*-

"""main.py:

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240301"

# std libs
import logging
import os
import json
from typing import Annotated, Optional
from json import JSONDecodeError
from contextlib import asynccontextmanager
# third party libs
from websockets.exceptions import ConnectionClosedOK
from fastapi import Depends, FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError, Field
# local libraries
from taskgraph import TaskGraph, TaskGraphData, TaskGraphProjectData
# this package
from .server_config import server_config, UserAccessLevel
from .auth import try_authenticate, create_access_token, validate_access_token, check_access_level
from .auth import Token, TokenData, AccessLevelException
from .ws import WebSocketConnectionManager
from .database import TaskGraphDatabaseManager

lg = logging.getLogger(__name__)


class ServerResourceNames(BaseModel):
    resources: list[str]


class NewProjectData(BaseModel):
    name: Optional[str] = Field(
        None, description="Name of the new project, if not specified, empty string will be used."
    )


ws_mgr = WebSocketConnectionManager()
tg = TaskGraph()
db_mgr = TaskGraphDatabaseManager(
    taskgraph=tg, database_config=server_config.database)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before application start, load database
    lg.info("Loading data from database.")
    db_mgr.load_database()
    yield
    # Clean up resources and save database to file
    lg.info("Saving data to database file ")
    db_mgr.save_database()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=server_config.CORS.origins,
    allow_credentials=server_config.CORS.allow_credentials,
    allow_methods=server_config.CORS.allow_methods,
    allow_headers=server_config.CORS.allow_headers,
)


@app.get("/")
async def get_resource_names() -> ServerResourceNames:
    r = [
        'token',
        'projects',
        'ws(ws://)']
    return ServerResourceNames(resources=r)


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    authenticate_result, user = try_authenticate(
        server_config.auth.users, form_data.username, form_data.password)
    if (authenticate_result is False) or (user is None):
        # don't tell the user if it is the username or the password that is wrong.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # authentication successful, create token
    access_token = create_access_token(user=user)
    return Token(**{"access_token": access_token, "token_type": "bearer"})


@app.get("/projects")
async def get_projects(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> TaskGraphData:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return tg.get_data()


@app.post("/projects")
async def create_project(project_data: NewProjectData,
                         token_data: Annotated[TokenData, Depends(validate_access_token)]) -> TaskGraphData:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    project_id = tg.new_project(name=project_data.name)
    lg.info("Created new project {}".format(project_id))
    return tg.get_data()


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    wsid = None
    try:
        wsid = await ws_mgr.connect(websocket)
        await ws_mgr.run(wsid)
    except (WebSocketDisconnect, ConnectionClosedOK) as e:
        # user disconnected from client side.
        lg.debug(
            "User disconnected from WebSocket connection, normal disconnection: {}".format(e))
    except JSONDecodeError:
        # user sent non-json message, probably wrong client, disconnect right away.
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    except ValidationError:
        # user input lack required field or malformed, report error to user and disconnect right away.
        await websocket.send_json({"error": "Invalid Operation"})
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    except AccessLevelException:
        # user input is legal and the user is good, but the user does not have the permission to perform the operation.
        await websocket.send_json({"error": "Insufficient Access Level"})
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    finally:
        if wsid is None:
            lg.info(
                "Client disconnected from websocket before authentication and protocol initialization finish.")
        else:
            # clear websocket and application protocol stored in manager as well as its auth info.
            ws_mgr.disconnect(wsid)
