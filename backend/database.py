# std libs
import os
import logging
import json
import asyncio
import time
# local packages
from taskgraph import TaskGraph, TaskGraphData, TaskGraphScheduler

# this package
from .server_config import DatabaseConfig


lg = logging.getLogger(__name__)


class TaskGraphDatabaseManager():
    def __init__(self, taskgraph: TaskGraph, scheduler: TaskGraphScheduler,
                 database_config: DatabaseConfig) -> None:
        self.tg = taskgraph
        self.sch = scheduler
        self.cfg = database_config
        # this hash information is used to compare if the project data on disk is
        # the same as the one in memory, to see if it has been changed.
        self.project_hashes: dict[str, str] = dict()
        self.manager_running = False
        self.eloop = asyncio.get_event_loop()

    def start_scheduler(self):
        self.manager_running = True
        self.eloop.create_task(self.periodic_check())

    def stop_scheduler(self):
        self.manager_running = False

    async def periodic_check(self):
        """
        Checks local file changes, load changes into memory, and save database periodically.
        NOTE that this function eventually calls methods that modifies data of TaskGraph
        and data on the disk, be aware of data conflicts and data corruption.
        This is the asynchronous version, thus no mutex is needed.
        """
        t_next_autosave = time.time() + 3600
        while self.manager_running:
            # [TODO]: check local files for auto loading
            # ...
            if time.time() > t_next_autosave:
                # Save database files every hour (set check_hash=True to save changes only)
                self.save_database(check_hash=True)
                t_next_autosave = t_next_autosave + 3600
            # release control and come back to check every second
            await asyncio.sleep(1)

    def load_projects(self, tg_data: TaskGraphData):
        projects_loaded: int = 0
        for project_id in tg_data.projects:
            project_name = tg_data.projects[project_id].name
            lg.info("Loading project: {} ({})".format(
                project_name, project_id))
            project_db_path = self.cfg.root_path + \
                "projects/{}.json".format(project_id)
            if os.path.exists(project_db_path):
                self.tg.load_project_from_file(project_db_path, project_id)
                # if loaded successful, save its hash for later use
                project = self.tg.projects[project_id]
                self.project_hashes[project_id] = project.get_data_hash()
                projects_loaded += 1
            else:
                lg.error(
                    "Cannot find database file for project {}!".format(project_id))
                lg.error("The DB item will be removed from project.json.")
        lg.info("Expected to load {} projects, {} projects actually loaded.".format(
            len(tg_data.projects), projects_loaded))

    def load_database(self):
        root_path = self.cfg.root_path
        projects_db_path = root_path + "projects.json"
        if os.path.exists(projects_db_path):
            lg.info("Database file found, loading projects.")
            with open(projects_db_path, 'rb') as f:
                r = f.read().decode("utf-8")
                r = json.loads(r)
            data = TaskGraphData(**r)
            self.load_projects(tg_data=data)
        else:
            lg.warning("No database file found!")
            lg.warning(
                "If this is a new installation of TaskGraph, this warning can be safely ignored.")
            lg.warning("Creating new database file at {}".format(
                projects_db_path))
            self.tg.serialize_to_file(projects_db_path)

    def save_project(self, project_id: str, check_hash: bool = False):
        project = self.tg.projects[project_id]
        if check_hash and (project_id in self.project_hashes):
            if project.get_data_hash() == self.project_hashes[project_id]:
                lg.debug("Project database file for {} not changed because the project has not been modified.".format(
                    project_id))
                return
        lg.info("Purging project metadata for {} before saving".format(project_id))
        project.purge_metadata()
        project_db_path = self.cfg.root_path + \
            "projects/{}.json".format(project_id)
        if os.path.exists(project_db_path):
            lg.info("Overwriting project database file at {}".format(
                project_db_path))
        else:
            lg.warning("Creating new project database file at {}".format(
                project_db_path))
        project.serialize_to_file(project_db_path)
        # if saved successfully, save its hash
        self.project_hashes[project_id] = project.get_data_hash()

    def save_projects(self, check_hash: bool = False):
        for project_id in self.tg.projects:
            self.save_project(project_id=project_id, check_hash=check_hash)

    def save_database(self, check_hash: bool = False):
        projects_db_path = self.cfg.root_path + "projects.json"
        if os.path.exists(projects_db_path):
            lg.info("Overwriting projects database file.")
        else:
            lg.warning("Creating new database file at {}".format(
                projects_db_path))
        self.save_projects(check_hash=check_hash)
        self.tg.serialize_to_file(projects_db_path)

    def delete_project(self, project_id: str):
        self.tg.remove_project(project_id=project_id)
        # SECURITY NOTICE:
        #   execute only if project_id is trustworthy.
        project_db_path = self.cfg.root_path + \
            "projects/{}.json".format(project_id)
        if os.path.exists(project_db_path):
            lg.warning("Deleting project database file at {}".format(
                project_db_path))
            os.remove(project_db_path)
        else:
            lg.warning("Did not find project database file {} when deleting project".format(
                project_db_path))

    def save_scheduler_database(self):
        scheduler_db_path = self.cfg.root_path + "scheduler.json"
        if os.path.exists(scheduler_db_path):
            lg.info("Overwriting scheduler database file.")
        else:
            lg.warning("Creating new scheduler database file at {}".format(
                scheduler_db_path))
        self.sch.serialize_to_file(scheduler_db_path)

    def load_scheduler_database(self):
        root_path = self.cfg.root_path
        scheduler_db_path = root_path + "scheduler.json"
        if os.path.exists(scheduler_db_path):
            self.sch.load_from_file(scheduler_db_path)
        else:
            lg.warning("No scheduler database file found!")
            lg.warning(
                "If this is a new installation of TaskGraph, this warning can be safely ignored.")
            lg.warning("Creating new scheduler database file at {}".format(
                scheduler_db_path))
            self.sch.serialize_to_file(scheduler_db_path)
