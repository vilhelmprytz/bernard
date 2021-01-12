import sys
from pathlib import Path

# add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app import db, app  # noqa: E402
from models import Zone  # noqa: E402

name = input("Enter zone name: ")
dns_provider = input("Enter DNS provider: ")

zone = Zone(zone=name, dns_provider=dns_provider)

with app.app_context():
    db.session.add(zone)
    db.session.commit()
