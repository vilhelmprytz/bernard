#!/usr/bin/env python3

import sys
from pathlib import Path

# add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app import db, app  # noqa: E402
from models import BannedRecord  # noqa: E402

record = BannedRecord(subdomain=input("Enter record to ban: "))

with app.app_context():
    db.session.add(record)
    db.session.commit()
