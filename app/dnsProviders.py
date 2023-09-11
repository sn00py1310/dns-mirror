from typing import Set
import requests
from abc import abstractmethod, ABCMeta

from myTypes import DNSEntry

ALLOWED_RECORD_TYPES = ["A", "AAAA"]


class dnsProviderAuth(metaclass=ABCMeta):
    @abstractmethod
    def updateEntry(self, myDomain: str, wrongContent: str, wrongType: str, toMakeContent: str, toMakeType: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def removeEntry(self, myDomain: str, toDeleteContent: str, toDeleteType: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def createEntry(self, myDomain: str, createContent: str, createType: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def getRecordsForDomain(self, myDomain: str) -> Set[DNSEntry]:
        raise NotImplementedError


class Cloudflare(dnsProviderAuth):
    def __init__(self, *, zone_identifier: str, email: str, token: str):
        self.cf_zone_identifier: str = zone_identifier
        self.cf_base_api: str = "https://api.cloudflare.com/client/v4"
        self.cf_email: str = email
        self.cf_token: str = token

        self.cf_headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": self.cf_email,
            "Authorization": f"Bearer {self.cf_token}"
        }

    def cfCreateRecords(self, domain: str, ip: str, type: str) -> None:
        url = f"{self.cf_base_api}/zones/{self.cf_zone_identifier}/dns_records"

        payload: dict[str, str | bool | list[str] | int] = {
            "content": ip,
            "name": domain,
            "proxied": False,
            "type": type,
            "comment": "[Auto created by DNS-Sync]",
            "tags": list(),
            "ttl": 1
        }
        response = requests.request(
            "POST", url, json=payload, headers=self.cf_headers)
        if response.status_code != 200:
            raise Exception(f"Api error\n{response.text}")

    def cfGetRecordId(self, domain: str, ip: str, type: str) -> str:
        url = f"{self.cf_base_api}/zones/{self.cf_zone_identifier}/dns_records"
        params = {
            "type": type,
            "content": ip,
            "name": domain
        }
        response = requests.request(
            "GET", url, params=params, headers=self.cf_headers)
        if response.status_code != 200:
            raise Exception(f"Api error\n{response.text}")

        data = response.json()
        result = data["result"]

        if result:
            return result[0]["id"]

        return ""

    def cfUpdateRecord(self, record_id: str, domain: str, ip: str, type: str) -> None:
        url = f"{self.cf_base_api}/zones/{self.cf_zone_identifier}/dns_records/{record_id}"

        payload: dict[str, str | bool | list[str] | int] = {
            "content": ip,
            "name": domain,
            "proxied": False,
            "type": type,
            "comment": "",
            "tags": [],
            "ttl": 1
        }

        response = requests.request(
            "PUT", url, json=payload, headers=self.cf_headers)
        if response.status_code != 200:
            raise Exception(f"Api error\n{response.text}")

    def cfRemoveRecord(self, record_id: str) -> None:
        url = f"{self.cf_base_api}/zones/{self.cf_zone_identifier}/dns_records/{record_id}"

        response = requests.request("DELETE", url, headers=self.cf_headers)
        if response.status_code != 200:
            raise Exception(f"Api error\n{response.text}")

    def getRecordsForDomain(self, myDomain: str) -> Set[DNSEntry]:
        url = f"{self.cf_base_api}/zones/{self.cf_zone_identifier}/dns_records?name={myDomain}"
        response = requests.request("GET", url, headers=self.cf_headers)
        if response.status_code != 200:
            raise Exception(f"Api error\n{response.text}")

        data = response.json()
        result = data["result"]

        domainList: Set[DNSEntry] = set()

        for entry in result:
            if entry["type"] not in ALLOWED_RECORD_TYPES:
                continue

            a = DNSEntry(entry["content"], entry["type"])
            domainList.add(a)
        return domainList

    def removeEntry(self, myDomain: str, toDeleteContent: str, toDeleteType: str) -> None:
        record_id = self.cfGetRecordId(myDomain, toDeleteContent, toDeleteType)
        self.cfRemoveRecord(record_id)

    def createEntry(self, myDomain: str, createContent: str, createType: str) -> None:
        self.cfCreateRecords(myDomain, createContent, createType)

    def updateEntry(self, myDomain: str, wrongContent: str, wrongType: str, toMakeContent: str, toMakeType: str) -> None:
        record_id = self.cfGetRecordId(myDomain, wrongContent, wrongType)
        self.cfUpdateRecord(record_id, myDomain, toMakeContent, toMakeType)
