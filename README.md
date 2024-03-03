# TaskGraph

TaskGraph is a simple application for personal project management.
It utilizes some ideas from asynchronous programming, cooperative multitasking and git versioning to help you finish projects more efficiently.

It is basically a todolist app with the following features:

* Tasks are organized into Projects.
    - A project is mapped to a directed acyclic graph (DAG).
    - Tasks are nodes in the project DAG.
    - A task can depend on another task, the dependency is represented by edges in the DAG.
    - Tasks can be inserted or removed at any time.
    - A task can be breaked down into more tasks.

* A Dispatcher tells you what to do now.
    - The dispatcher uses a eventloop to manage tasks.
    - When you finish the current task, you mark it as finished and ask the dispatcher for a list of available tasks and pick one to continue working.
    - You can leave the current task and mark it as interrupted at any time, if the current task requires to wait for some external event, for example waiting for package delivery or PCB manufacturing.
    - The dispatcher will automatically adds interrupted tasks back to available tasks for you to continue when received the required event.

* Metadata can be attached to tasks.
    - File paths
    - Timeouts
    - Deadlines
    - Geo Locations
    - Images and Videos
    - Links
    - Any other string
    - Special metadata reserved: Name, Status

* Actions can be attached to tasks.
    - Python scripts
    - Email reminder
    - WeChat reminder

* Database is saved as text files for easy synchronization across devices.
    - Human readable
    - Standard formats
    - Export to various formats

## Deployment

TaskGraph is based on python and javascript, no installation is required.
However, dependencies for python packages needs to be installed on the server side.
Check docs/dependencies.md for a guide on how to install deps.

To deploy the backend application, suppose that the python dependencies are installed in an anaconda environment called `taskgraph`, clone the project

    (base) $ git clone https://github.com/5A/taskgraph
    (base) $ cd taskgraph

then in the root directory of this project, run

    (base) $ conda activate taskgraph
    (taskgraph) $ uvicorn backend.main:app --log-config logging_helper/uvicorn_log.config.yaml --host 0.0.0.0

The frontend application is in the `frontend` directory, and can be served by any static content server application, such as nginx.
For temporary testing, you can run the built-in python3 HTTP server

    (base) $ cd frontend/dist
    (base) $ python -m http.server

then go to http://localhost:8000 to access the web GUI.

## Testing

To run the python unittests, do

    $ python -m unittest tests.test_taskgraph
