from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, eq=True)
class DNSEntry:
    content: str
    type: Literal["A", "AAAA"]


from dnsProviders import dnsProviderAuth  # noqa: E402


@dataclass
class SyncEntry:
    myDomain: str
    myDnsProvider: dnsProviderAuth
    externalDomain: str
