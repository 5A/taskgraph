# -*- coding: utf-8 -*-

"""test_taskgraph.py:
Integration test for taskgraph core library
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240301"

# std libs
import unittest
import logging
import time
import os
# project packages
from logging_helper import TestingLogFormatter
# package to be tested
from taskgraph import TaskGraphProject, TaskGraph

# configure root logger to output all logs to stdout
lg = logging.getLogger()
lg.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(TestingLogFormatter())
lg.addHandler(ch)

# configure logger for this module.
lg = logging.getLogger(__name__)

# setup temporary file path for testing
TEMPORARY_FILE_PATH = os.path.dirname(__file__)


class TestTaskGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        lg.info("Test started")
        # cls.tg = TaskGraph()

    @classmethod
    def tearDownClass(cls):
        lg.info("Test ended.")

    def test_task_graph(self):
        lg.info("Testing TaskGraph Core Library")
        self.tg = TaskGraph()
        lg.info("Constructing a test project")
        proj1 = self.tg.new_project("Test Project")
        proj = self.tg.projects[proj1]
        task1 = proj.add_task(proj.task_root)
        task2 = proj.add_task(proj.task_root)
        task3 = proj.add_task(proj.task_root)
        task4 = proj.add_task(task1)
        task5 = proj.add_task(task4)
        task6 = proj.add_task(task2)
        proj.add_dependency(task6, dep=task3)
        lg.info("Saving project to temporary file")
        to_save = proj.serialize()
        lg.info(to_save)
        proj_save_path = os.path.join(TEMPORARY_FILE_PATH, "test_taskgraph_project.json")
        with open(proj_save_path, 'w') as f:
            f.write(to_save)
        lg.info("Loading back")
        proj = TaskGraphProject()
        proj.load_from_file(proj_save_path)
        lg.info("Loaded: ")
        lg.info(proj.serialize())
        lg.info("Testing project export")
        self.tg.new_project(name="Test Project 2")
        to_save = self.tg.serialize()
        lg.info((to_save))
        tg_save_path = os.path.join(TEMPORARY_FILE_PATH, "test_taskgraph.json")
        with open(tg_save_path, 'w') as f:
            f.write(to_save)
        lg.info("Testing load project from file")
        self.tg.load_project_from_file(proj_save_path)
        lg.info(self.tg.serialize())
        

