# -*- coding: utf-8 -*-

"""taskgraph:
This package defines the data model and operations of taskgraph.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20240301"

from .taskgraph import (
    TaskGraph, TaskGraphProject,
    TaskGraphData, TaskGraphProjectData,
    TaskStatus, TaskGraphTaskMetadataItem,
    TaskGraphScheduler, TaskGraphEvents,
    EventTaskWakeUp,
)
