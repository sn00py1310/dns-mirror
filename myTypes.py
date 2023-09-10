from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, eq=True)
class DNSEntry:
    content: str
    type: Literal["A", "AAAA"]


@dataclass(frozen=True, eq=True)
class SyncEntry:
    myDomain: str
    externalDomain: str
