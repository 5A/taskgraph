# std
from typing import Optional
# third party
from pydantic import BaseModel, Field
# this project
from taskgraph import TaskStatus

class ServerResourceNames(BaseModel):
    resources: list[str]


class NewProjectData(BaseModel):
    name: Optional[str] = Field(
        None, description="Name of the new project, if not specified, empty string will be used."
    )


class DeleteProjectData(BaseModel):
    uuid: str


class ProjectOperationReport(BaseModel):
    id: str
    name: str


class NewSubTaskData(BaseModel):
    parent: str
    name: Optional[str] = Field(
        None, description="Name of the new task, if not specified, the task will be created without a name"
    )
    detail: Optional[str] = Field(
        None, description="Detail of the new task, if not specified, the task will be created without a detail"
    )


class NewSuperTaskData(BaseModel):
    child: str
    name: Optional[str] = Field(
        None, description="Name of the new task, if not specified, the task will be created without a name"
    )
    detail: Optional[str] = Field(
        None, description="Detail of the new task, if not specified, the task will be created without a detail"
    )


class UpdateTaskStatusData(BaseModel):
    uuid: str
    status: TaskStatus


class RemoveTaskData(BaseModel):
    uuid: str


class AddDependenciesData(BaseModel):
    uuid: str
    dependencies: list[str]


class RemoveDependencyData(BaseModel):
    uuid_sub_task: str
    uuid_super_task: str


class SnoozeTaskData(BaseModel):
    uuid: str
    snooze_until: float


class ModifyProjectData(BaseModel):
    add_sub_task: Optional[NewSubTaskData] = Field(
        None, description=""
    )
    add_super_task: Optional[NewSuperTaskData] = Field(
        None, description=""
    )
    update_task_status: Optional[UpdateTaskStatusData] = Field(
        None, description=""
    )
    remove_task: Optional[RemoveTaskData] = Field(
        None, description=""
    )
    add_dependencies: Optional[AddDependenciesData] = Field(
        None, description=""
    )
    remove_dependency: Optional[RemoveDependencyData] = Field(
        None, description=""
    )
    snooze_task: Optional[SnoozeTaskData] = Field(
        None, description=""
    )

class ModifyProjectReport(BaseModel):
    result: str