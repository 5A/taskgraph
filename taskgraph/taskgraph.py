# -*- coding: utf-8 -*-

"""taskgraph.py:
This module defines the data model and operations of taskgraph.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240301"

# std libs
import json
import time
from typing import Mapping, Optional
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


class TaskGraphMetadataItem(BaseModel):
    """
    Stores any metadata attached to a given task(node) or dependency(edge)
    """
    # Common for both task and dependency
    name: Optional[str] = None
    detail: Optional[str] = None
    # Task metadata
    status: Optional[str] = None
    wake_after: Optional[float] = None


class TaskGraphProjectData(BaseModel):
    name: str
    DAG: Mapping
    metadata: dict[str, TaskGraphMetadataItem]

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
        self.metadata: dict[str, TaskGraphMetadataItem] = dict()
        self.__add_root()

    def __add_root(self):
        self.task_root = uuid.uuid4().__str__()
        self.metadata[self.task_root] = TaskGraphMetadataItem()
        self.metadata[self.task_root].name = "Finish"
        self.metadata[self.task_root].status = "Active"
        self.dag.add_node(self.task_root)

    def __check_snoozed(self, task_uuid: str) -> bool:
        meta = self.metadata[task_uuid]
        if TaskStatus.snoozed.value == meta.status:
            if meta.wake_after is None:
                # no wake_after time set, this should not happen
                raise ValueError(
                    "No wake_after is set for snoozed task {}".format(task_uuid))
            elif time.time() > meta.wake_after:
                # it is time to wake
                return False
            else:
                # continue snooze
                return True
        else:
            # currently not snoozed
            return False

    def __analyze_status(self, task_uuid: str):
        """
        Analyzes status of a given task in the project DAG to resolve dependency / wake task
        """
        # rule 1: if task is currently snoozed, it remains snoozed until WakeAfter is passed.
        if self.__check_snoozed(task_uuid=task_uuid):
            return
        # rule 2: else: if the task is not snoozed, and if all predecessors of the task are done,
        #   then the task becomes active
        # rule 3: else: if the task is not snoozed, and it still has dependency not done, it is pending.
        all_dependency_resolved = True
        for node in self.dag.predecessors(task_uuid):
            if TaskStatus.done.value == self.metadata[node].status:
                pass
            else:
                all_dependency_resolved = False
                break
        if all_dependency_resolved:
            self.metadata[task_uuid].status = TaskStatus.active.value
        else:
            self.metadata[task_uuid].status = TaskStatus.pending.value

    def add_sub_task(self, parent: str, meta: TaskGraphMetadataItem | None = None) -> str:
        """
        Adds a sub-task for a given parent task, marks the new task as active and
        the parent task as pending.
        """
        # create node for the task and record its metadata in project.metadata
        task_uuid = uuid.uuid4().__str__()
        if meta is not None:
            self.metadata[task_uuid] = meta
        else:
            self.metadata[task_uuid] = TaskGraphMetadataItem()
        self.dag.add_node(task_uuid)
        # add dependency for the task, the parent task will depend on the new sub-task
        self.add_dependency(parent, dep=task_uuid)
        # mark status of tasks
        self.metadata[task_uuid].status = TaskStatus.active.value
        return task_uuid

    def add_super_task(self, child: str, meta: TaskGraphMetadataItem | None = None) -> str:
        """
        Adds a super-task for a given child task, marks the new task as pending.
        """
        # create node for the task and record its metadata in project.metadata,
        task_uuid = uuid.uuid4().__str__()
        if meta is not None:
            self.metadata[task_uuid] = meta
        else:
            self.metadata[task_uuid] = TaskGraphMetadataItem()
        self.dag.add_node(task_uuid)
        # add dependency for the task, the new super-task will depend on the child task
        self.add_dependency(task_uuid, dep=child)
        return task_uuid

    def add_dependency(self, task_uuid: str, dep: str):
        """
        Adds an existing task as sub-task for a given parent task.
        Marks the parent task as pending.
        """
        dependency_uuid = uuid.uuid4().__str__()
        self.metadata[dependency_uuid] = TaskGraphMetadataItem()
        self.dag.add_edge(dep, task_uuid, id=dependency_uuid)
        # mark status of task
        self.metadata[task_uuid].status = TaskStatus.pending.value

    def remove_dependency(self, task_uuid: str, dep_uuid: str):
        """
        Removes dep_uuid from task_uuid's dependency
        """
        dependency_uuid = self.dag.edges[dep_uuid, task_uuid]['id']
        self.metadata.pop(dependency_uuid)
        self.dag.remove_edge(dep_uuid, task_uuid)
        self.__analyze_status(task_uuid=task_uuid)

    def remove_task(self, task_uuid: str):
        """
        Removes a task, checks every super-task to see if its dependency has been resolved.
        """
        # save a list of successors before removing
        super_tasks = self.dag.successors(task_uuid)
        # remove the task
        self.dag.remove_node(task_uuid)
        self.metadata.pop(task_uuid)
        # resolve dependencies for super-tasks after the task is removed
        for node in super_tasks:
            self.__analyze_status(task_uuid=node)

    def task_done(self, task_uuid: str):
        """
        Marks a task as done, resolving its children's dependency
        """
        self.metadata[task_uuid].status = TaskStatus.done.value
        for node in self.dag.successors(task_uuid):
            self.__analyze_status(node)

    def task_snooze(self, task_uuid: str, snooze_until: float):
        """
        Marks a task as snoozed, removing it from active task list and do not resolve its
        children's dependency.
        Once snooze_until (timestamp) is passed, snoozed tasks will be re-set to active
        in the next analyze.
        """
        self.metadata[task_uuid].status = TaskStatus.snoozed.value
        self.metadata[task_uuid].wake_after = snooze_until

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
        return data_obj.model_dump_json(indent=2, exclude_none=True)

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
        return data_obj.model_dump_json(indent=2, exclude_none=True)

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
