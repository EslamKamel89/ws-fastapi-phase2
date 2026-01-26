from typing import Any, Literal, TypedDict


class Message(TypedDict):
    type: Literal["broadcast"]
    sender: str
    payload: Any
