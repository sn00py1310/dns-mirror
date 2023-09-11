from myTypes import SyncEntry
from dnsProviders import Cloudflare
from webhooks import Discord

logLevel = 10

notification_webhooks = [
    Discord(webhook_id="", webhook_token="")
]

dns_servers = ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001",
               "8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844"]
dns_retry_amount = 2
dns_lifetime = 15

cf_provider = Cloudflare(zone_identifier="", email="", token="")

syncMap = [
    SyncEntry("example.mydomain.test", cf_provider, "example.com"),
    SyncEntry("example.mydomain.test", cf_provider, "example.com")
]
