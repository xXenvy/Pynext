"""
The MIT License (MIT)
Copyright (c) 2023-present xXenvy

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations
from typing import Any, Callable

from time import time
from random import choice
from string import ascii_letters, digits

from aiohttp import ClientResponse, client_exceptions
from asyncio import iscoroutinefunction
from datetime import datetime, timezone

DISCORD_EPOCH: int = 1420070400000

try:
    import orjson  # pyright: ignore[reportMissingImports]

    INSTALLED_ORJSON: bool = True
except ModuleNotFoundError:
    import json

    INSTALLED_ORJSON: bool = False


async def text_or_json(response: ClientResponse) -> dict | str:
    try:
        return await response.json()
    except client_exceptions.ContentTypeError:
        return await response.text()


class EqualityComparable:
    __slots__ = ()

    id: int

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.id != self.id
        return True


class Hashable(EqualityComparable):
    __slots__ = ()

    def __hash__(self) -> int:
        return self.id >> 22


def json_dumps(value: Any) -> str:
    if INSTALLED_ORJSON is True:
        assert orjson
        return orjson.dumps(value).decode("utf-8")

    assert json
    return json.dumps(value, separators=(",", ":"))


def json_loads(value: str) -> dict:
    if INSTALLED_ORJSON is True:
        assert orjson
        return orjson.loads(value)

    assert json
    return json.loads(value)


def snowflake_time(object_id: int) -> datetime:
    timestamp = ((object_id >> 22) + DISCORD_EPOCH) / 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def str_to_datetime(value: str) -> datetime:
    tuple_data: tuple[str, ...] = value.partition("T")
    datetime_str: str = f"{tuple_data[0]} {tuple_data[2][0:8]}"

    datetime_object: datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    return datetime_object


def applications_filter(data: dict[str, Any]) -> dict[int, Any]:
    apps: dict[int, dict[str, Any]] = {}

    for app_data in data["applications"]:
        app_data["app_commands"] = []
        apps[int(app_data["id"])] = app_data

    for command_data in data["application_commands"]:
        if application_data := apps.get(int(command_data["application_id"])):
            app_commands: list[dict[str, Any]] = application_data["app_commands"]
            app_commands.append(command_data)

    return apps


def nonce() -> int:
    return (int(time()) * 1000 - 1420070400000) * 4194304


def create_session(lenght: int = 32) -> str:
    return "".join(choice(ascii_letters + digits) for _ in range(lenght))


async def maybe_coro(coro: Callable, *args: Any, **kwargs: Any) -> Any:
    if iscoroutinefunction(coro):
        return await coro(*args, **kwargs)
    else:
        return coro(*args, **kwargs)
