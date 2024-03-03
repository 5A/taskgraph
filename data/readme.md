# Data

This directory is where all database files are saved.
The database files are human-readable and can also be manually edited with any text editor.

If you are deploying the application with a static content server, do NOT expose this directory to public web! This directory should only be visible to the backend application and the administrator.

`projects.json` holds information used by TaskGraph to identify what projects are to be loaded.

`projects/xxxx-xxxx...xxx.json` holds data for each project.

It is recommanded that a centralized server, for example a managed server/NAS to be used to synchronize your changes to all client devices.
But for users who do not have a centralized server to store their data, the database files can be directly synchronized between multiple devices, with regular software like OneDrive, rsync or Syncthing.
The backend server is able to automatically monitor the data directory for any changes made by other software/human editing.
However, be aware that data inconsistency may occur if conficting changes are made simutanuously on different devices.
