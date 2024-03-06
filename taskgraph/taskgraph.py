# -*- coding: utf-8 -*-

"""taskgraph.py:
This module defines the data model and operations of taskgraph.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240301"

# std libs
import json
from typing import Mapping
from enum import Enum
# third party libs
import uuid
import networkx as nx
from pydantic import BaseModel


class TaskStatus(Enum):
    """
    Tasks have multiple status:
        Done: marks that task has been done
        Active: the task is currently under working
        Pending: the task is waiting for its dependency to be resolved
        Snoozed: the task is waiting for an appropriate time to start
    """
    done = "Done"
    active = "Active"
    pending = "Pending"
    snoozed = "Snoozed"


class TaskGraphProjectData(BaseModel):
    name: str
    DAG: Mapping
    metadata: dict[str, dict[str, str]]


class TaskGraphDataItem(BaseModel):
    name: str


class TaskGraphData(BaseModel):
    # projects: dict[uuid -> {meta: data}]
    projects: dict[str, TaskGraphDataItem]


class TaskGraphProject:
    def __init__(self, name: str | None = None) -> None:
        if name is not None:
            self.name = name
        else:
            self.name = ""
        self.dag = nx.DiGraph()
        self.metadata: dict[str, dict[str, str]] = dict()
        self.__add_root()

    def __add_root(self):
        self.task_root = uuid.uuid4().__str__()
        self.metadata[self.task_root] = dict()
        self.metadata[self.task_root]["Name"] = "Finish"
        self.metadata[self.task_root]["Status"] = "Active"
        self.dag.add_node(self.task_root)

    def __analyze_status(self, task_uuid: str):
        """
        Analyzes status of a given task in the project DAG to resolve dependency
        """
        # rule 1: if all predecessors of the task are done, then the task is not pending.
        # it becomes active or snoozed
        # [TODO] snooze
        all_dependency_resolved = True
        for node in self.dag.predecessors(task_uuid):
            if self.metadata[node]["Status"] == "Done":
                pass
            else:
                all_dependency_resolved = False
                break
        if all_dependency_resolved:
            self.metadata[task_uuid]["Status"] = TaskStatus.active.value
        else:
            self.metadata[task_uuid]["Status"] = TaskStatus.pending.value

    def add_sub_task(self, parent: str, meta: dict[str, str] | None = None) -> str:
        """
        Adds a sub-task for a given parent task, marks the new task as active and
        the parent task as pending.
        """
        # create node for the task
        task_uuid = uuid.uuid4().__str__()
        self.metadata[task_uuid] = dict()
        self.dag.add_node(task_uuid)
        # record its metadata in project.metadata
        #  we will simply overwrite data because this is a new node with no data
        if meta is not None:
            self.metadata[task_uuid] = meta
        # add dependency for the task, the parent task will depend on the new sub-task
        self.add_dependency(parent, dep=task_uuid)
        # mark status of tasks
        self.metadata[task_uuid]["Status"] = TaskStatus.active.value
        return task_uuid

    def add_super_task(self, child: str, meta: dict[str, str] | None = None) -> str:
        """
        Adds a super-task for a given child task, marks the new task as pending.
        """
        # create node for the task
        task_uuid = uuid.uuid4().__str__()
        self.metadata[task_uuid] = dict()
        self.dag.add_node(task_uuid)
        # record its metadata in project.metadata,
        #  we will simply overwrite data because this is a new node with no data
        if meta is not None:
            self.metadata[task_uuid] = meta
        # add dependency for the task, the new super-task will depend on the child task
        self.add_dependency(task_uuid, dep=child)
        return task_uuid

    def add_dependency(self, task_uuid: str, dep: str):
        """
        Adds an existing task as sub-task for a given parent task.
        Marks the parent task as pending.
        """
        dependency_uuid = uuid.uuid4().__str__()
        self.metadata[dependency_uuid] = dict()
        self.dag.add_edge(dep, task_uuid, id=dependency_uuid)
        # mark status of task
        self.metadata[task_uuid]["Status"] = TaskStatus.pending.value

    def remove_dependency(self, task_uuid: str, dep_uuid: str):
        """
        Removes dep_uuid from task_uuid's dependency
        """
        dependency_uuid = self.dag.edges[dep_uuid, task_uuid]['id']
        self.metadata.pop(dependency_uuid)
        self.dag.remove_edge(dep_uuid, task_uuid)
        self.__analyze_status(task_uuid=task_uuid)

    def remove_task(self, task_uuid: str):
        self.dag.remove_node(task_uuid)
        self.metadata.pop(task_uuid)

    def task_done(self, task_uuid: str):
        """
        Marks a task as done, resolving its children's dependency
        """
        self.metadata[task_uuid]["Status"] = TaskStatus.done.value
        for node in self.dag.successors(task_uuid):
            self.__analyze_status(node)

    def get_data(self, dag_format: str | None = None) -> TaskGraphProjectData:
        if dag_format == "cytoscape":
            dag_data = nx.cytoscape_data(self.dag)
        else:
            # default data format
            dag_data = nx.node_link_data(self.dag)
        data_obj = TaskGraphProjectData(
            name=self.name,
            DAG=dag_data,
            metadata=self.metadata
        )
        return data_obj

    def serialize(self) -> str:
        data_obj = self.get_data()
        return data_obj.model_dump_json(indent=2)

    def serialize_to_file(self, path: str):
        with open(path, 'wb') as f:
            f.write(self.serialize().encode("utf-8"))

    def load(self, data: TaskGraphProjectData):
        self.name = data.name
        self.dag = nx.node_link_graph(data.DAG)
        self.metadata = data.metadata

    def load_from_file(self, path: str):
        with open(path, 'rb') as f:
            r = f.read().decode("utf-8")
            r = json.loads(r)
        data = TaskGraphProjectData(**r)
        return self.load(data)


class TaskGraph:
    def __init__(self) -> None:
        self.projects: dict[str, TaskGraphProject] = dict()

    def new_project(self, name: str | None = None) -> str:
        proj_uuid = uuid.uuid4().__str__()
        proj = TaskGraphProject(name=name)
        self.projects[proj_uuid] = proj
        return proj_uuid

    def get_data(self) -> TaskGraphData:
        data = {}
        for project_id in self.projects:
            data_obj = TaskGraphDataItem(
                name=self.projects[project_id].name
            )
            data[project_id] = data_obj
        return TaskGraphData(projects=data)

    def serialize(self) -> str:
        data_obj = self.get_data()
        return data_obj.model_dump_json(indent=2)

    def serialize_to_file(self, file_path: str):
        with open(file_path, 'wb') as f:
            f.write(self.serialize().encode("utf-8"))

    def load_project_from_file(self, file_path: str, project_id: str | None = None) -> str:
        proj = TaskGraphProject()
        proj.load_from_file(file_path)
        if project_id is not None:
            proj_uuid = project_id
        else:
            proj_uuid = uuid.uuid4().__str__()
        self.projects[proj_uuid] = proj
        return proj_uuid

    def remove_project(self, project_id: str) -> TaskGraphProject:
        return self.projects.pop(project_id)
