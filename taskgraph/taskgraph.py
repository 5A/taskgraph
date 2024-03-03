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
# third party libs
import uuid
import networkx as nx
from pydantic import BaseModel


class TaskGraphProjectData(BaseModel):
    name: str
    DAG: Mapping
    metadata: dict[str, dict[str, str]]


class TaskGraphDataItem(BaseModel):
    id: str
    name: str


class TaskGraphData(BaseModel):
    projects: list[TaskGraphDataItem]


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
        self.metadata[self.task_root]["Name"] = "Root"
        self.dag.add_node(self.task_root)

    def add_task(self, parent: str) -> str:
        task_uuid = uuid.uuid4().__str__()
        self.metadata[task_uuid] = dict()
        self.dag.add_node(task_uuid)
        self.dag.add_edge(parent, task_uuid)
        return task_uuid

    def add_dependency(self, task_uuid: str, dep: str):
        self.dag.add_edge(dep, task_uuid)

    def remove_task(self, task_uuid: str):
        self.dag.remove_node(task_uuid)
        self.metadata.pop(task_uuid)

    def serialize(self) -> str:
        data_obj = TaskGraphProjectData(
            name=self.name,
            DAG=nx.node_link_data(self.dag),
            metadata=self.metadata
        )
        return data_obj.model_dump_json(indent=2)

    def serialize_to_file(self, path: str):
        with open(path, 'w') as f:
            f.write(self.serialize())

    def load(self, data: TaskGraphProjectData):
        self.name = data.name
        self.dag = nx.node_link_graph(data.DAG)
        self.metadata = data.metadata

    def load_from_file(self, path: str):
        with open(path, 'r') as f:
            r = json.load(f)
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
        data = []
        for project_id in self.projects:
            data_obj = TaskGraphDataItem(
                id=project_id,
                name=self.projects[project_id].name
            )
            data.append(data_obj)
        return TaskGraphData(projects=data)

    def serialize(self) -> str:
        data_obj = self.get_data()
        return data_obj.model_dump_json(indent=2)

    def serialize_to_file(self, file_path: str):
        with open(file_path, 'w') as f:
            f.write(self.serialize())

    def load_project_from_file(self, file_path: str, project_id: str | None = None) -> str:
        proj = TaskGraphProject()
        proj.load_from_file(file_path)
        if project_id is not None:
            proj_uuid = project_id
        else:
            proj_uuid = uuid.uuid4().__str__()
        self.projects[proj_uuid] = proj
        return proj_uuid
