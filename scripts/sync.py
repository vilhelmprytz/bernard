#!/usr/bin/env python3

import sys
from pathlib import Path

# add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app import app  # noqa: E402
from models import Zone, Record  # noqa: E402
from dns_providers import bind9  # noqa: E402

with app.app_context():
    bind9.sync(zones=Zone.query.all(), records=Record.query.all())
