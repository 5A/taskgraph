# -*- coding: utf-8 -*-

"""server_config.py:
This module defines the data model of config file for the server of this application.
It also provides methods to load config from config file, or dump config to a file.
"""

__author__ = "Zhi Zi"
__email__ = "x@zzi.io"
__version__ = "20231115"

# std libs
import os
import json
from enum import Enum
# third party libs
from pydantic import BaseModel, UUID4
# this package

# meta params and defaults
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'server.config.json')


class UserAccessLevel(int, Enum):
    readonly = 1
    standard = 2
    advanced = 3


class UserConfig(BaseModel):
    id: UUID4
    username: str
    hashed_password: str
    access_level: UserAccessLevel


class JWTConfig(BaseModel):
    secret: str
    algorithm: str
    expire_seconds: int


class AuthConfig(BaseModel):
    users: list[UserConfig]
    jwt: JWTConfig


class CORSConfig(BaseModel):
    origins: list[str]
    allow_credentials: bool
    allow_methods: list[str]
    allow_headers: list[str]

class DatabaseConfig(BaseModel):
    root_path: str

class ApplicationConfig(BaseModel):
    auth: AuthConfig
    CORS: CORSConfig
    database: DatabaseConfig


def load_config_from_file(config_path: str = CONFIG_PATH):
    with open(config_path, 'r') as f:
        r = json.load(f)
    return ApplicationConfig(**r)


def dump_config_to_file(config: ApplicationConfig, config_path: str = CONFIG_PATH):
    with open(config_path, 'w+') as f:
        f.write(config.model_dump_json(indent=4))


server_config = load_config_from_file()
