from myTypes import SyncEntry

cf_token = ""  # Cloudflare API token
cf_email = ""  # Cloudflare email
cf_zone_identifier = ""  # Cloudflare zone identifier
discord_webhook_url = ""  # Discord Webhook url for error reporting

dns_servers = ["1.1.1.1", "1.0.0.1", "2606:4700:4700::1111", "2606:4700:4700::1001",
               "8.8.8.8", "8.8.4.4", "2001:4860:4860::8888", "2001:4860:4860::8844"]

syncMap = [
    SyncEntry("example.com.your-domain.test", "example.com")
]
