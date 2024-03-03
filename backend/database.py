# std libs
import os
import logging
import json
# local packages
from taskgraph import TaskGraph, TaskGraphData

# this package
from .server_config import DatabaseConfig


lg = logging.getLogger(__name__)


class TaskGraphDatabaseManager():
    def __init__(self, taskgraph: TaskGraph, database_config: DatabaseConfig) -> None:
        self.tg = taskgraph
        self.cfg = database_config

    def load_projects(self, tg_data: TaskGraphData):
        for item in tg_data.projects:
            lg.info("Loading project {}".format(item))
            project_db_path = self.cfg.root_path + \
                "projects/{}.json".format(item.id)
            if os.path.exists(project_db_path):
                self.tg.load_project_from_file(project_db_path, item.id)
            else:
                lg.error(
                    "Cannot find database file for project {}!".format(item))
                lg.error("The DB item will be removed from project.json.")

    def load_database(self):
        root_path = self.cfg.root_path
        projects_db_path = root_path + "projects.json"
        if os.path.exists(projects_db_path):
            lg.info("Database file found, loading projects.")
            with open(projects_db_path, 'r') as f:
                r = json.load(f)
            data = TaskGraphData(**r)
            self.load_projects(tg_data=data)
        else:
            lg.warning("No database file found!")
            lg.warning(
                "If this is a new installation of TaskGraph, this warning can be safely ignored.")
            lg.warning("Creating new database file at {}".format(
                projects_db_path))
            self.tg.serialize_to_file(projects_db_path)

    def save_project(self, project_id: str):
        project_db_path = self.cfg.root_path + \
            "projects/{}.json".format(project_id)
        project = self.tg.projects[project_id]
        if os.path.exists(project_db_path):
            lg.info("Overwriting project database file at {}".format(
                project_db_path))
        else:
            lg.warning("Creating new project database file at {}".format(
                project_db_path))
        project.serialize_to_file(project_db_path)

    def save_projects(self):
        for project_id in self.tg.projects:
            self.save_project(project_id=project_id)

    def save_database(self):
        projects_db_path = self.cfg.root_path + "projects.json"
        if os.path.exists(projects_db_path):
            lg.info("Overwriting projects database file.")
        else:
            lg.warning("Creating new database file at {}".format(
                projects_db_path))
        self.save_projects()
        self.tg.serialize_to_file(projects_db_path)
