import dns.resolver
from dns.resolver import LifetimeTimeout
from typing import TypeVar, Set
import config
import logging

from myTypes import DNSEntry, dnsProviderAuth, DNSEntryTypes
T = TypeVar("T")

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s \t- %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)


def getItemFromSet(i: Set[T]) -> T:
    return next(iter(i))


def getRecords(domain: str, type: DNSEntryTypes) -> list[str]:
    dns_retry_counter = 0
    while dns_retry_counter <= config.dns_retry_amount:
        try:
            my_resolver = dns.resolver.Resolver()
            my_resolver.nameservers = config.dns_servers
            answers = my_resolver.resolve(
                domain, type, lifetime=config.dns_lifetime, raise_on_no_answer=False)

            IPs: list[str] = list()
            if not answers or not answers.rrset:
                return IPs

            for rdata in answers.rrset:  # type: ignore
                IPs.append(rdata.address)  # type: ignore
            return IPs

        except LifetimeTimeout as e:
            if dns_retry_counter >= config.dns_retry_amount:
                raise e

            dns_retry_counter += 1
            log.warning(f"DNS timeout retry no {dns_retry_counter}")

    return list()


def updateStuff(myDomain: str, dnsProvider: dnsProviderAuth, externalDomain: str, types: Set[DNSEntryTypes]) -> None:
    log.info(f"{myDomain} -> {externalDomain}")
    myEntries = dnsProvider.getRecordsForDomain(myDomain, types)

    externalEntries: Set[DNSEntry] = set()

    for type in types:
        Records = getRecords(externalDomain, type)
        for record in Records:
            externalEntries.add(DNSEntry(record, type))

    log.debug(f"Same: {myEntries == externalEntries}")
    if myEntries != externalEntries:
        myWrongEntries = myEntries.difference(externalEntries)
        toMakeEntries = externalEntries.difference(myEntries)

        # remove because of to many
        while len(myWrongEntries) > len(toMakeEntries):
            toDelete = getItemFromSet(myWrongEntries)
            log.info(f"Remove Entry {toDelete}")

            dnsProvider.removeEntry(myDomain, toDelete.content, toDelete.type)

            myWrongEntries.remove(toDelete)

        # create because of not enough
        while len(myWrongEntries) < len(toMakeEntries):
            create = getItemFromSet(toMakeEntries)
            log.debug(f"Create Entry {create}")
            dnsProvider.createEntry(myDomain, create.content, create.type)

            toMakeEntries.remove(create)

        # Update to be the same
        while myWrongEntries != toMakeEntries:
            myWrong = getItemFromSet(myWrongEntries)
            toMake = getItemFromSet(toMakeEntries)

            log.debug(f"Update: {myWrong} to {toMake}")

            dnsProvider.updateEntry(
                myDomain, myWrong.content, myWrong.type, toMake.content, toMake.type)

            myWrongEntries.remove(myWrong)
            toMakeEntries.remove(toMake)


def exceptionNotification(notification: str) -> None:
    for webhook in config.error_webhooks:
        webhook.sendNotification(notification)


def main() -> None:
    for syncEntry in config.syncMap:
        updateStuff(syncEntry.myDomain, syncEntry.myDnsProvider,
                    syncEntry.externalDomain, syncEntry.entryTypes)


if __name__ == "__main__":
    try:
        log.debug("Startup")
        main()
        for webhook in config.success_webhooks:
            webhook.sendNotification("Everything updated")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.exception(e)
        exceptionNotification(str(e))
