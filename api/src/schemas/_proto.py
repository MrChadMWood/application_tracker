from typing import Protocol, Type
from pydantic import BaseModel


# Used for annotating type: schema module
class SchemaProtocol(Protocol):
    Create: Type[BaseModel]
    Read: Type[BaseModel]
