import requests
import os
import json

CLOUDFLARE_ENDPOINT = "https://api.cloudflare.com/client/v4"
CLOUDFLARE_API_TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]

headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}


def add(zone, subdomain, ip):
    r = requests.get(f"{CLOUDFLARE_ENDPOINT}/zones?name={zone}", headers=headers)
    if r.status_code != requests.codes.ok:
        raise Exception(f"cloudflare {str(r.content)}")

    data = r.json()
    if len(data["result"]) != 1:
        raise Exception("no such domain or too many domains")
    zone_id = data["result"][0]["id"]

    r = requests.post(
        f"{CLOUDFLARE_ENDPOINT}/zones/{zone_id}/dns_records",
        data=json.dumps(
            {"type": "A", "name": f"{subdomain}.{zone}", "content": ip, "ttl": 1}
        ),
        headers=headers,
    )

    if r.status_code != requests.codes.ok:
        raise Exception(f"cloudflare {str(r.content)}")
