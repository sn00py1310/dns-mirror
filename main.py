import dns.resolver
from dns.resolver import NoAnswer
from typing import Literal, TypeVar, Set
import requests
import config

from myTypes import DNSEntry
T = TypeVar("T")

allowedTypes = ["A", "AAAA"]

cf_headers = {
    "Content-Type": "application/json",
    "X-Auth-Email": config.cf_email,
    "Authorization": f"Bearer {config.cf_token}"
}

cf_base_api = "https://api.cloudflare.com/client/v4"


def getItemFromSet(i: Set[T]) -> T:
    return next(iter(i))


def getRecords(domain: str, type: Literal["A", "AAAA"]) -> list[str]:
    try:
        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = config.dns_servers
        answers = my_resolver.resolve(domain, type, lifetime=15)
    except NoAnswer:
        return list()

    IPs: list[str] = list()
    if not answers.rrset:
        return IPs

    for rdata in answers.rrset:  # type: ignore
        # print(rdata.address)
        IPs.append(rdata.address)  # type: ignore
    return IPs


def cfGetRecords(checkDomain: str) -> Set[DNSEntry]:
    url = f"{cf_base_api}/zones/{config.cf_zone_identifier}/dns_records?name={checkDomain}"
    response = requests.request("GET", url, headers=cf_headers)
    if response.status_code != 200:
        raise Exception(f"Api error\n{response.text}")

    data = response.json()
    result = data["result"]

    domainList: Set[DNSEntry] = set()

    for entry in result:
        if entry["type"] not in allowedTypes:
            continue

        a = DNSEntry(entry["content"], entry["type"])
        domainList.add(a)
    return domainList


def cfCreateRecords(domain: str, ip: str, type: str) -> None:
    url = f"{cf_base_api}/zones/{config.cf_zone_identifier}/dns_records"

    payload: dict[str, str | bool | list[str] | int] = {
        "content": ip,
        "name": domain,
        "proxied": False,
        "type": type,
        "comment": "[Auto created by DNS-Sync]",
        "tags": list(),
        "ttl": 1
    }
    response = requests.request("POST", url, json=payload, headers=cf_headers)
    if response.status_code != 200:
        raise Exception(f"Api error\n{response.text}")


def cfGetRecordId(domain: str, ip: str, type: str) -> str:
    url = f"{cf_base_api}/zones/{config.cf_zone_identifier}/dns_records"
    params = {
        "type": type,
        "content": ip,
        "name": domain
    }
    response = requests.request("GET", url, params=params, headers=cf_headers)
    if response.status_code != 200:
        raise Exception(f"Api error\n{response.text}")

    data = response.json()
    result = data["result"]

    if result:
        return result[0]["id"]

    return ""


def cfUpdateRecord(record_id: str, domain: str, ip: str, type: str) -> None:
    url = f"{cf_base_api}/zones/{config.cf_zone_identifier}/dns_records/{record_id}"

    payload: dict[str, str | bool | list[str] | int] = {
        "content": ip,
        "name": domain,
        "proxied": False,
        "type": type,
        "comment": "",
        "tags": [],
        "ttl": 1
    }

    response = requests.request("PUT", url, json=payload, headers=cf_headers)
    if response.status_code != 200:
        raise Exception(f"Api error\n{response.text}")


def cfRemoveRecord(record_id: str) -> None:
    url = f"{cf_base_api}/zones/{config.cf_zone_identifier}/dns_records/{record_id}"

    response = requests.request("DELETE", url, headers=cf_headers)
    if response.status_code != 200:
        raise Exception(f"Api error\n{response.text}")


def updateStuff(myDomain: str, externalDomain: str) -> None:
    print(f"{myDomain} -> {externalDomain}")
    myEntries = cfGetRecords(myDomain)

    externalEntries: Set[DNSEntry] = set()
    Records = getRecords(externalDomain, "A")
    for record in Records:
        externalEntries.add(DNSEntry(record, "A"))

    Records = getRecords(externalDomain, "AAAA")
    for record in Records:
        externalEntries.add(DNSEntry(record, "AAAA"))

    print(f"Same: {myEntries == externalEntries}")
    if myEntries != externalEntries:
        myWrongEntries = myEntries.difference(externalEntries)
        toMakeEntries = externalEntries.difference(myEntries)

        # remove because of to many
        while len(myWrongEntries) > len(toMakeEntries):
            toDelete = getItemFromSet(myWrongEntries)
            print(f"Remove Entry {toDelete}")

            record_id = cfGetRecordId(
                myDomain, toDelete.content, toDelete.type)
            cfRemoveRecord(record_id)  # TODO Uncomment

            myWrongEntries.remove(toDelete)

        # create because of not enough
        while len(myWrongEntries) < len(toMakeEntries):
            create = getItemFromSet(toMakeEntries)
            print(f"Create Entry {create}")
            cfCreateRecords(myDomain, create.content,
                            create.type)  # TODO Uncomment

            toMakeEntries.remove(create)

        # Update to be the same
        while myWrongEntries != toMakeEntries:
            myWrong = getItemFromSet(myWrongEntries)
            toMake = getItemFromSet(toMakeEntries)

            print(f"Update: {myWrong} to {toMake}")

            record_id = cfGetRecordId(myDomain, myWrong.content, myWrong.type)
            cfUpdateRecord(record_id, myDomain,
                           toMake.content, toMake.type)  # TODO Uncomment

            myWrongEntries.remove(myWrong)
            toMakeEntries.remove(toMake)


def exceptionNotification(notification: str) -> None:
    requests.post(config.discord_webhook_url, json={"content": notification})


def main() -> None:
    for syncEntry in config.syncMap:
        updateStuff(syncEntry.myDomain, syncEntry.externalDomain)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(str(e))
        exceptionNotification(str(e))
