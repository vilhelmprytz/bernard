def sync(records, zones):
    files = {}

    for zone in zones:
        files[zone.zone] = ""

    for record in records:
        files[record.zone.zone] = (
            files[record.zone.zone]
            + f"{record.subdomain}.{record.zone.zone}. IN A {record.ip}\n"
        )

    for filename, content in files.items():
        with open(f"zones/{filename}.zone", "w") as f:
            f.write(content)
