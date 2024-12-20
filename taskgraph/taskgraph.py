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
import heapq
import asyncio
import logging
import hashlib
from typing import Mapping, Optional, Tuple
from enum import Enum
# third party libs
import uuid
import networkx as nx
from pydantic import BaseModel

lg = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """
    Projects have multiple status:
        Done: marks that the project has been finished
        Active: the project still has tasks active
        Snoozed: the project has tasks not done, but all available tasks are snoozed
    """
    done = "Done"
    active = "Active"
    snoozed = "Snoozed"


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


class IssueStatus(Enum):
    """
    Issues have multiple status:
        Open: issue to be resolved
        Closed: issue finished or cannot be finished anymore
    """
    open = "Open"
    closed = "Closed"


class TaskGraphIssue(BaseModel):
    """
    Stores issue item data
    """
    title: str
    status: str
    description: Optional[str] = None
    labels: Optional[list[str]] = None
    close_reason: Optional[str] = None
    time_close: Optional[float] = None  # Timestamp, unit in seconds
    last_modify: Optional[float] = None  # Timestamp, unit in seconds


class TaskGraphTaskMetadataItem(BaseModel):
    """
    Stores any metadata attached to a given task(node)
    """
    name: Optional[str] = None
    detail: Optional[str] = None
    status: Optional[str] = None
    wake_after: Optional[float] = None  # Timestamp, unit in seconds
    snooze_reason: Optional[str] = None
    remind_after: Optional[float] = None  # Timestamp, unit in seconds
    last_modify: Optional[float] = None  # Timestamp, unit in seconds
    time_done: Optional[float] = None  # Timestamp, unit in seconds
    issues: Optional[dict[str, TaskGraphIssue]] = None


class ProjectStatisticsData(BaseModel):
    active: int = 0
    snoozed: int = 0
    pending: int = 0
    done: int = 0
    unknown: int = 0


class TaskGraphProjectData(BaseModel):
    name: str
    DAG: Mapping
    metadata: dict[str, TaskGraphTaskMetadataItem]


class TaskGraphDataItem(BaseModel):
    name: str
    status: Optional[str] = None


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
        self.metadata: dict[str, TaskGraphTaskMetadataItem] = dict()
        self.statistics: ProjectStatisticsData = ProjectStatisticsData()
        self.__add_root()

    def __add_root(self):
        self.task_root = uuid.uuid4().__str__()
        self.metadata[self.task_root] = TaskGraphTaskMetadataItem()
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

    def __check_reminder(self, task_uuid: str) -> bool:
        meta = self.metadata[task_uuid]
        if meta.remind_after is None:
            raise ValueError(
                "No remind_after is set for task {}".format(task_uuid))
        elif time.time() > meta.remind_after:
            # it is time to remind
            return True
        else:
            # do not remind yet
            return False

    def update_statistics(self):
        statistics = ProjectStatisticsData()
        for k, v in self.metadata.items():
            if v.status is None:
                statistics.unknown += 1
            elif TaskStatus.done.value == v.status:
                statistics.done += 1
            elif TaskStatus.active.value == v.status:
                statistics.active += 1
            elif TaskStatus.pending.value == v.status:
                statistics.pending += 1
            elif TaskStatus.snoozed.value == v.status:
                statistics.snoozed += 1
            else:
                statistics.unknown += 1
        self.statistics = statistics

    def resolve_dependency(self, task_uuid: str):
        """
        Analyzes status of a given task in the project DAG to resolve dependency
        """
        # rule -1: if the task is already removed, it cannot has a status
        # this should normally not happen, so a warning is emitted
        if task_uuid not in self.metadata:
            lg.warning(
                "Task {} does not exist in current project, thus asking to resolve its dependency failed and nothing is changed.".format(task_uuid))
            lg.warning(
                "This usually happens when an action is scheduled for the task, but the task is removed manually before the action get executed.")
            return
        # rule 0: if a task is done, it is done forever unless it is revived
        if TaskStatus.done.value == self.metadata[task_uuid].status:
            return
        # rule 1: if task is currently snoozed, it remains snoozed until time to wake up.
        if self.__check_snoozed(task_uuid):
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

    def add_sub_task(self, parent: str, meta: TaskGraphTaskMetadataItem | None = None) -> str:
        """
        Adds a sub-task for a given parent task, marks the new task as active and
        the parent task as pending.
        """
        # create node for the task and record its metadata in project.metadata
        task_uuid = uuid.uuid4().__str__()
        if meta is not None:
            self.metadata[task_uuid] = meta
        else:
            self.metadata[task_uuid] = TaskGraphTaskMetadataItem()
        self.dag.add_node(task_uuid)
        # add dependency for the task, the parent task will depend on the new sub-task
        self.add_dependency(parent, dep=task_uuid)
        # mark status of tasks
        self.metadata[task_uuid].status = TaskStatus.active.value
        self.metadata[task_uuid].last_modify = time.time()
        return task_uuid

    def add_super_task(self, child: str, meta: TaskGraphTaskMetadataItem | None = None) -> str:
        """
        Adds a super-task for a given child task, marks the new task as pending.
        """
        # create node for the task and record its metadata in project.metadata,
        task_uuid = uuid.uuid4().__str__()
        if meta is not None:
            self.metadata[task_uuid] = meta
        else:
            self.metadata[task_uuid] = TaskGraphTaskMetadataItem()
        self.dag.add_node(task_uuid)
        # add dependency for the task, the new super-task will depend on the child task
        self.add_dependency(task_uuid, dep=child)
        self.metadata[task_uuid].last_modify = time.time()
        return task_uuid

    def modify_task_metadata(self, task_uuid: str, meta: TaskGraphTaskMetadataItem):
        """
        Modify several metadata for a single task all at once.
        Non-empty fields in meta are updated, while None-valued fields are ignored and not modified.
        """
        if task_uuid not in self.dag.nodes:
            raise ValueError(
                "Modifying non-existent task {}!".format(task_uuid))
        if meta.name is not None:
            self.metadata[task_uuid].name = meta.name
        if meta.detail is not None:
            self.metadata[task_uuid].detail = meta.detail
        if meta.status is not None:
            self.metadata[task_uuid].status = meta.status
        self.metadata[task_uuid].last_modify = time.time()

    def add_dependency(self, task_uuid: str, dep: str):
        """
        Adds an existing task as sub-task for a given parent task.
        Marks the parent task as pending.
        """
        dependency_uuid = uuid.uuid4().__str__()
        # [TODO] add metadata to dependency
        # self.dependency_metadata[dependency_uuid] = TaskGraphDependencyMetadataItem()
        self.dag.add_edge(dep, task_uuid, id=dependency_uuid)
        # mark status of task
        self.metadata[task_uuid].status = TaskStatus.pending.value

    def remove_dependency(self, task_uuid: str, dep_uuid: str):
        """
        Removes dep_uuid from task_uuid's dependency
        """
        dependency_uuid = self.dag.edges[dep_uuid, task_uuid]['id']
        # [TODO] remove dependency from dep meta
        # self.dependency_metadata.pop(dependency_uuid)
        self.dag.remove_edge(dep_uuid, task_uuid)
        self.resolve_dependency(task_uuid=task_uuid)

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
            self.resolve_dependency(task_uuid=node)

    def task_done(self, task_uuid: str):
        """
        Marks a task as done, resolving its children's dependency
        """
        self.metadata[task_uuid].status = TaskStatus.done.value
        self.metadata[task_uuid].time_done = time.time()
        for node in self.dag.successors(task_uuid):
            self.resolve_dependency(node)

    def task_snooze(self, task_uuid: str, snooze_until: float, reason: Optional[str] = None):
        """
        Marks a task as snoozed, removing it from active task list and do not resolve its
        children's dependency.
        Once snooze_until (timestamp) is passed, snoozed tasks will be re-set to active
        in the next analyze.
        """
        self.metadata[task_uuid].status = TaskStatus.snoozed.value
        self.metadata[task_uuid].wake_after = snooze_until
        self.metadata[task_uuid].snooze_reason = reason

    def task_add_reminder(self, task_uuid: str, remind_after: float):
        """
        Adds a reminder to a task.
        Once remind_after (timestamp) is passed, user defined action will be executed on task.
        """
        self.metadata[task_uuid].remind_after = remind_after

    def task_open_issue(self, task_uuid: str, title: str, description: Optional[str] = None) -> str:
        """
        Adds an issue to a task, optionally provides a description, default to no label.
        """
        task_meta = self.metadata[task_uuid]
        if task_meta.issues is None:
            # create issues metadata item if it does not exist yet
            task_meta.issues = dict()
        issue_uuid = uuid.uuid4().__str__()
        issue_last_modify = time.time()
        issue_data = TaskGraphIssue(
            title=title,
            status=IssueStatus.open.value,
            description=description,
            last_modify=issue_last_modify)
        task_meta.issues[issue_uuid] = issue_data
        return issue_uuid

    def task_close_issue(self, task_uuid: str, issue_uuid: str, reason: Optional[str] = None):
        """
        Closes an issue, optionally provides a reason.
        """
        task_meta = self.metadata[task_uuid]
        if task_meta.issues is None:
            raise ValueError(
                "No issues created for task {} yet!".format(task_uuid))
        if issue_uuid not in task_meta.issues:
            raise ValueError(
                "issue_uuid does not exist in list, already removed or not created yet.")
        task_meta.issues[issue_uuid].status = IssueStatus.closed.value
        task_meta.issues[issue_uuid].close_reason = reason
        task_meta.issues[issue_uuid].time_close = time.time()

    def task_modify_issue(self, task_uuid: str, issue_uuid: str,
                          title: Optional[str] = None, description: Optional[str] = None):
        """
        Modify issue data (title, description)
        """
        task_meta = self.metadata[task_uuid]
        if task_meta.issues is None:
            raise ValueError(
                "No issues created for task {} yet!".format(task_uuid))
        if issue_uuid not in task_meta.issues:
            raise ValueError(
                "issue_uuid does not exist in list, already removed or not created yet.")
        if title is not None:
            task_meta.issues[issue_uuid].title = title
        if description is not None:
            task_meta.issues[issue_uuid].description = description
        task_meta.issues[issue_uuid].last_modify = time.time()

    def task_reopen_issue(self, task_uuid: str, issue_uuid: str):
        """
        Re-opens a closed issue.
        """
        task_meta = self.metadata[task_uuid]
        if task_meta.issues is None:
            raise ValueError(
                "No issues created for task {} yet!".format(task_uuid))
        if issue_uuid not in task_meta.issues:
            raise ValueError(
                "issue_uuid does not exist in list, already removed or not created yet.")
        task_meta.issues[issue_uuid].status = IssueStatus.open.value

    def task_delete_issue(self, task_uuid: str, issue_uuid: str):
        """
        Deletes an issue (Closed issues are still saved in database, deleted issues are gone forever)
        """
        task_meta = self.metadata[task_uuid]
        if task_meta.issues is None:
            raise ValueError(
                "No issues created for task {} yet!".format(task_uuid))
        task_meta.issues.pop(issue_uuid)

    def task_raise_issue(self, task_uuid: str, issue_uuid: str):
        """
        Raises an issue to a sub-task of current task
        (Converts issue to task)
        """
        task_meta = self.metadata[task_uuid]
        if task_meta.issues is None:
            raise ValueError(
                "No issues created for task {} yet!".format(task_uuid))
        if issue_uuid not in task_meta.issues:
            raise ValueError(
                "Issue does not exist in task!")
        issue = task_meta.issues[issue_uuid]
        # Add new sub-task, map data between issue and task
        sub_task_meta = TaskGraphTaskMetadataItem()
        sub_task_meta.name = issue.title
        sub_task_meta.detail = issue.description
        self.add_sub_task(task_uuid, meta=sub_task_meta)
        # Remove converted issue
        task_meta.issues.pop(issue_uuid)

    def get_tasks_by_status(self, status: TaskStatus = TaskStatus.active) -> dict[str, TaskGraphTaskMetadataItem]:
        tasks = dict(
            filter(
                lambda item: item[1].status == status.value,
                self.metadata.items()
            ))
        return tasks

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

    def purge_metadata(self):
        """
        Removes unused metadata items from .metadata, by looking at each task uuid
        """
        new_metadata: dict[str, TaskGraphTaskMetadataItem] = dict()
        for item in self.dag.nodes:
            if item in self.metadata:
                new_metadata[item] = self.metadata[item]
        self.metadata = new_metadata

    def get_data_hash(self):
        """
        Calculates a hash from current project data, if the hashes match, then the projects
        should be identical.
        This method provides a way to compare TaskGraphProject's, which is handy for detecting
        data changes or handling data migration.
        """
        return hashlib.sha256(self.serialize().encode('utf-8')).hexdigest()


class TaskGraph:
    def __init__(self) -> None:
        self.projects: dict[str, TaskGraphProject] = dict()

    def new_project(self, name: str | None = None) -> str:
        proj_uuid = uuid.uuid4().__str__()
        proj = TaskGraphProject(name=name)
        self.projects[proj_uuid] = proj
        return proj_uuid

    def remove_project(self, project_id: str) -> TaskGraphProject:
        return self.projects.pop(project_id)

    def get_tasks_by_status(self, status: TaskStatus = TaskStatus.active):
        tasks = dict()
        for project_uuid in self.projects:
            proj = self.projects[project_uuid]
            tasks[project_uuid] = proj.get_tasks_by_status(status=status)
        return tasks

    def get_data(self) -> TaskGraphData:
        data = {}
        for project_id in self.projects:
            proj = self.projects[project_id]
            proj.update_statistics()
            status = ProjectStatus.done.value
            if proj.statistics.active > 0:
                # active task present, project is active
                status = ProjectStatus.active.value
            elif proj.statistics.snoozed > 0:
                # no active task, but at least 1 task is snoozed
                status = ProjectStatus.snoozed.value
            else:
                # no active or snoozed, project finished.
                pass
            data_obj = TaskGraphDataItem(
                name=proj.name,
                status=status
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


class TaskGraphEvents(Enum):
    wake_up = "wake_up"


class EventTaskWakeUp(BaseModel):
    project_uuid: str
    task_uuid: str


class TaskGraphSchedulerData(BaseModel):
    event_heap: list[Tuple[float, str, str]]
    event_map: dict[str, EventTaskWakeUp]


class TaskGraphScheduler:
    def __init__(self, taskgraph: TaskGraph) -> None:
        """
        Scheduler of all TaskGraph events, regardless of task or project.
        event_heap: min heap used to sort events, stored as (timestamp, event_uuid, event_type)
        event_map: key-value storage to store additional event data, as {event_uuid: EventData}
        """
        self.tg = taskgraph
        self.event_heap: list[Tuple[float, str, str]] = []
        self.event_map: dict[str, EventTaskWakeUp] = dict()
        self.scheduler_running = False
        self.eloop = asyncio.get_event_loop()

    def start_scheduler(self):
        self.scheduler_running = True
        self.eloop.create_task(self.periodic_check())

    def stop_scheduler(self):
        self.scheduler_running = False

    def get_data(self) -> TaskGraphSchedulerData:
        data_obj = TaskGraphSchedulerData(
            event_heap=self.event_heap,
            event_map=self.event_map
        )
        return data_obj

    def serialize(self) -> str:
        data_obj = self.get_data()
        return data_obj.model_dump_json(indent=2, exclude_none=True)

    def serialize_to_file(self, file_path: str):
        with open(file_path, 'wb') as f:
            f.write(self.serialize().encode("utf-8"))

    def load(self, data: TaskGraphSchedulerData):
        self.event_heap = data.event_heap
        self.event_map = data.event_map

    def load_from_file(self, path: str):
        with open(path, 'rb') as f:
            r = f.read().decode("utf-8")
            r = json.loads(r)
        data = TaskGraphSchedulerData(**r)
        return self.load(data)

    def schedule(self, timestamp: float, event_type: str,
                 event_data: EventTaskWakeUp):
        event_uuid = uuid.uuid4().__str__()
        heapq.heappush(self.event_heap, (timestamp, event_uuid, event_type))
        self.event_map[event_uuid] = event_data

    async def periodic_check(self):
        """
        Checks event heap constantly to trigger events.
        NOTE that this function eventually calls methods that modifies data of TaskGraph,
        be aware of data conflicts.
        This is the asynchronous version, thus no mutex is needed.
        """
        while self.scheduler_running:
            while (len(self.event_heap) > 0) and self.scheduler_running:
                # process all time-up events in a loop
                first_event = self.event_heap[0]
                t_event = first_event[0]
                if time.time() > t_event:
                    # trig event and remove it from event heap / event map
                    event_uuid = first_event[1]
                    event_type = first_event[2]
                    self.__process_event(
                        event_uuid=event_uuid, event_type=event_type)
                    heapq.heappop(self.event_heap)
                    self.event_map.pop(event_uuid)
                else:
                    # no more time-up event, go to outer loop and wait for nexts
                    break
                # all data operation is done, hand out control for a short period of time
                # to avoid blocking the main thread for too long in case of too many events.
                await asyncio.sleep(0.1)
            # all time-up events processed,
            # release control and come back to check events every second
            await asyncio.sleep(1)

    def __process_event(self, event_uuid: str, event_type: str):
        if TaskGraphEvents.wake_up.value == event_type:
            event_data: EventTaskWakeUp = self.event_map[event_uuid]
            project_uuid = event_data.project_uuid
            task_uuid = event_data.task_uuid
            # we need to check if the project and the task still exist before
            # processing wake_up event
            if project_uuid not in self.tg.projects:
                lg.warning("When processing wake_up event for task {} for project {}, the project does not exist in current database. The project is probably removed before this action.".format(
                    task_uuid, project_uuid))
                return
            target_project = self.tg.projects[project_uuid]
            if task_uuid not in target_project.metadata:
                lg.warning("When processing wake_up event for task {} in project {}, the task does not exist in the project. The task is probably removed before this action.".format(
                    task_uuid, project_uuid))
                return
            # check dependency to determine if it should be pending or active.
            # resolve_dependency will check wake_after metadata attached to the
            # task again to determine if it is really time to wake up, because
            # the user may set another time to snooze until, and the previous
            # event did not get removed. (Which means EventWakeUp only tries to
            # wake up the task, but does not guarantee that the task get woke up)
            target_project.resolve_dependency(task_uuid=task_uuid)
