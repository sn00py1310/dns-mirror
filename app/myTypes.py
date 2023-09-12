from dataclasses import dataclass
from typing import Set
from enum import StrEnum


class DNSEntryTypes(StrEnum):
    A = "A"
    AAAA = "AAAA"


@dataclass(frozen=True, eq=True)
class DNSEntry:
    content: str
    type: DNSEntryTypes


from dnsProviders import dnsProviderAuth  # noqa: E402


@dataclass
class SyncEntry:
    myDomain: str
    myDnsProvider: dnsProviderAuth
    externalDomain: str
    entryTypes: Set[DNSEntryTypes]
