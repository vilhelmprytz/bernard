#!/usr/bin/env python3

import sys
from pathlib import Path

# add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app import db, app  # noqa: E402
from models import BannedIp  # noqa: E402

ip = BannedIp(ip=input("Enter IP to ban: "))

with app.app_context():
    db.session.add(ip)
    db.session.commit()
