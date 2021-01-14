#!/usr/bin/env python3

import sys
from pathlib import Path
from dns_providers import bind9

# add parent folder
sys.path.append(str(Path(__file__).parent.parent.absolute()))

from app import db, app  # noqa: E402
from models import Zone, Record  # noqa: E402

bind9.sync(zones=Zone.query.all(), records=Record.query.all())
