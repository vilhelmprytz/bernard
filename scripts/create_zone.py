#!/usr/bin/env python3

import sys
from pathlib import Path

# add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app import db, app  # noqa: E402
from models import Zone  # noqa: E402

zone = Zone(zone=input("Enter zone name: "))

with app.app_context():
    db.session.add(zone)
    db.session.commit()
