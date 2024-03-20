# -*- coding: utf-8 -*-

"""main.py:

"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240301"

# std libs
import logging
from typing import Annotated
from json import JSONDecodeError
from contextlib import asynccontextmanager
# third party libs
from websockets.exceptions import ConnectionClosedOK
from fastapi import Depends, FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect, WebSocketException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
# local libraries
from taskgraph import (
    TaskGraph, TaskGraphData,
    TaskGraphProjectData, TaskStatus, TaskGraphTaskMetadataItem,
    TaskGraphScheduler, TaskGraphEvents, EventTaskWakeUp
)
# this package
from .server_config import server_config, UserAccessLevel
from .auth import try_authenticate, create_access_token, validate_access_token, check_access_level
from .auth import Token, TokenData, AccessLevelException
from .ws import WebSocketConnectionManager
from .database import TaskGraphDatabaseManager
from .data_models import (
    ServerResourceNames,
    NewProjectData, DeleteProjectData, ProjectOperationReport,
    ModifyProjectData, ModifyProjectReport,
    TasksLookupReport
)

lg = logging.getLogger(__name__)


ws_mgr = WebSocketConnectionManager()
tg = TaskGraph()
tg_sch = TaskGraphScheduler(taskgraph=tg)
db_mgr = TaskGraphDatabaseManager(
    taskgraph=tg, scheduler=tg_sch,
    database_config=server_config.database)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before application start, load database and scheduler
    lg.info("Loading data from database.")
    db_mgr.load_database()
    lg.info("Loading events remaining from last session.")
    db_mgr.load_scheduler_database()
    lg.info("Starting up scheduler...")
    tg_sch.start_scheduler()
    lg.info("Starting up database manager...")
    db_mgr.start_scheduler()
    yield
    # Clean up resources and save database to file
    lg.info("Stopping database manager...")
    db_mgr.stop_scheduler()
    lg.info("Stopping scheduler...")
    tg_sch.stop_scheduler()
    lg.info("Saving remaining events to database file")
    db_mgr.save_scheduler_database()
    lg.info("Saving projects data to database file ")
    # Explicitly set check_hash to False to force overwriting files at exit.
    # This is nonsense if everything goes right, but if something went wrong 
    # this should be able to keep some data consistency at least.
    db_mgr.save_database(check_hash=False)


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
async def get_project_list(token_data: Annotated[TokenData, Depends(validate_access_token)]) -> TaskGraphData:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return tg.get_data()


@app.post("/projects")
async def create_project(project_data: NewProjectData,
                         token_data: Annotated[TokenData, Depends(validate_access_token)]) -> ProjectOperationReport:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    project_id = tg.new_project(name=project_data.name)
    project_name = tg.projects[project_id].name
    db_mgr.save_project(project_id=project_id)
    lg.info("Created new project \"{}\": {}".format(project_name, project_id))
    return ProjectOperationReport(id=project_id, name=project_name)


@app.delete("/projects")
async def delete_project(project_data: DeleteProjectData,
                         token_data: Annotated[TokenData, Depends(validate_access_token)]) -> ProjectOperationReport:
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    project_id = project_data.uuid
    project_name = tg.projects[project_id].name
    db_mgr.delete_project(project_id=project_id)
    lg.info("Deleted project \"{}\": {}".format(project_name, project_id))
    return ProjectOperationReport(id=project_id, name=project_name)


@app.get("/projects/{project_uuid}", response_model=TaskGraphProjectData, response_model_exclude_none=True)
async def read_project(project_uuid: str,
                       token_data: Annotated[TokenData, Depends(validate_access_token)],
                       format: str | None = None):
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    return tg.projects[project_uuid].get_data(dag_format=format)


@app.post("/projects/{project_uuid}")
async def modify_project(project_uuid: str, mod_data: ModifyProjectData,
                         token_data: Annotated[TokenData, Depends(validate_access_token)]):
    check_access_level(token_data.access_level, UserAccessLevel.standard)
    proj = tg.projects[project_uuid]
    if mod_data.add_sub_task is not None:
        meta = TaskGraphTaskMetadataItem()
        if mod_data.add_sub_task.name is not None:
            meta.name = mod_data.add_sub_task.name
        if mod_data.add_sub_task.detail is not None:
            meta.detail = mod_data.add_sub_task.detail
        proj.add_sub_task(mod_data.add_sub_task.parent, meta=meta)
    if mod_data.add_super_task is not None:
        meta = TaskGraphTaskMetadataItem()
        if mod_data.add_super_task.name is not None:
            meta.name = mod_data.add_super_task.name
        if mod_data.add_super_task.detail is not None:
            meta.detail = mod_data.add_super_task.detail
        proj.add_super_task(mod_data.add_super_task.child, meta=meta)
    if mod_data.modify_task is not None:
        if mod_data.modify_task.name is not None:
            proj.metadata[mod_data.modify_task.uuid].name = mod_data.modify_task.name
        if mod_data.modify_task.detail is not None:
            proj.metadata[mod_data.modify_task.uuid].detail = mod_data.modify_task.detail
    if mod_data.update_task_status is not None:
        data = mod_data.update_task_status
        if TaskStatus.done.value == data.status.value:
            proj.task_done(data.uuid)
    if mod_data.remove_task is not None:
        proj.remove_task(mod_data.remove_task.uuid)
    if mod_data.add_dependencies is not None:
        for uuid in mod_data.add_dependencies.dependencies:
            proj.add_dependency(mod_data.add_dependencies.uuid, uuid)
    if mod_data.remove_dependency is not None:
        proj.remove_dependency(
            task_uuid=mod_data.remove_dependency.uuid_super_task,
            dep_uuid=mod_data.remove_dependency.uuid_sub_task
        )
    if mod_data.snooze_task is not None:
        proj.task_snooze(mod_data.snooze_task.uuid,
                         mod_data.snooze_task.snooze_until)
        tg_sch.schedule(mod_data.snooze_task.snooze_until,
                        TaskGraphEvents.wake_up.value,
                        EventTaskWakeUp(
                            project_uuid=project_uuid,
                            task_uuid=mod_data.snooze_task.uuid
                        ))
    if mod_data.open_issue is not None:
        proj.task_open_issue(task_uuid=mod_data.open_issue.task_uuid,
                             title=mod_data.open_issue.title,
                             description=mod_data.open_issue.description)
    if mod_data.close_issue is not None:
        proj.task_close_issue(task_uuid=mod_data.close_issue.task_uuid,
                              issue_uuid=mod_data.close_issue.issue_uuid,
                              reason=mod_data.close_issue.reason)
    if mod_data.delete_issue is not None:
        proj.task_delete_issue(task_uuid=mod_data.delete_issue.task_uuid,
                               issue_uuid=mod_data.delete_issue.issue_uuid)

    return ModifyProjectReport(result="OK")


@app.get("/tasks/{status}", response_model_exclude_none=True)
async def get_tasks_list_by_status(
        status: TaskStatus,
        token_data: Annotated[TokenData, Depends(validate_access_token)]) -> TasksLookupReport:
    check_access_level(token_data.access_level, UserAccessLevel.readonly)
    result = tg.get_tasks_by_status(status=status)
    return TasksLookupReport(result=result)


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
