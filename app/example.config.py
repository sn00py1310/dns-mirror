from myTypes import SyncEntry, DNSEntryTypes
from dnsProviders import Cloudflare
from webhooks import Discord, UptimeMonitor

logLevel = 10

error_webhooks = [
    Discord(webhook_id="", webhook_token="")
]

success_webhooks = [
    UptimeMonitor("https://uptime.mydomain.test/api/push/XXXXXXXXX?status=up&msg={{msg}}", "{{msg}}")
]

dns_servers = ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001",
               "8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844"]
dns_retry_amount = 2
dns_lifetime = 15

cf_provider = Cloudflare(zone_identifier="", email="", token="")
entryTypes = set([DNSEntryTypes.A, DNSEntryTypes.AAAA])

syncMap = [
    SyncEntry("example.mydomain.test", cf_provider, "example.com", entryTypes),
    SyncEntry("example.mydomain.test", cf_provider, "example.com", entryTypes)
]
