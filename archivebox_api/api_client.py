#!/usr/bin/env python
from archivebox_api.api.api_client_auth import Api as AuthApi
from archivebox_api.api.api_client_cli import Api as CliApi
from archivebox_api.api.api_client_core import Api as CoreApi


class Api(AuthApi, CliApi, CoreApi):
    __slots__ = ()
