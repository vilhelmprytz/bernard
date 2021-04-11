from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import HTTPException
from json import dumps
import os
import string

from dns_providers import bind9
from models import db, Zone, Record, BannedIp, BannedRecord
from ipaddress import ip_address, IPv4Address
from validation import expect_json

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "bernard")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "bernard")

DATABASE_TYPE = os.environ.get("DATABASE_TYPE", "mysql")

app = Flask(__name__)
if DATABASE_TYPE == "mysql":
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
elif DATABASE_TYPE == "sqlite":
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/bernard.db"
else:
    raise Exception(f"invalid DATABASE_TYPE {DATABASE_TYPE}")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def valid_input(variable):
    alnum = set(string.ascii_letters + string.digits)
    if any(x not in alnum for x in variable):
        return False
    return True


def is_ipv4(ip: str) -> bool:
    try:
        return True if type(ip_address(ip)) is IPv4Address else False
    except ValueError:
        raise Exception(f"Invalid IP, {ip} (should not happen)")


# all error pages are now JSON instead of HTML
@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()

    response.data = dumps(
        {"success": False, "name": e.name, "description": e.description, "code": e.code}
    )

    response.content_type = "application/json"
    return response, e.code


@app.route("/api/subdomain", methods=["POST", "PUT", "GET", "DELETE"])
def api_subdomain():
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        remote_addr = request.environ["REMOTE_ADDR"]
    else:
        remote_addr = request.environ["HTTP_X_FORWARDED_FOR"]

    if not is_ipv4(remote_addr):
        abort(400, "Service currently only supports IPv4")

    # check if IP is banned
    if len(BannedIp.query.filter_by(ip=remote_addr).all()) != 0:
        abort(401, "Your IP has been banned from using this servcice")

    if request.method == "GET":
        search = Record.query.filter_by(ip=remote_addr)

        if len(search.all()) == 0:
            abort(404, "You do not have a subdomain")

        return jsonify(
            {
                "success": True,
                "name": "OK",
                "description": "You already have a subdomain",
                "code": 200,
                "response": {
                    "subdomain": f"{search.first().subdomain}.{search.first().zone.zone}"
                },
            }
        )

    if request.method == "DELETE":
        search = Record.query.filter_by(ip=remote_addr)

        if len(search.all()) == 0:
            abort(400, "You do not have a subdomain")

        db.session.delete(search.first())
        db.session.commit()

        bind9.sync(zones=Zone.query.all(), records=Record.query.all())

        return jsonify(
            {
                "success": True,
                "name": "OK",
                "description": "Subdomain removed",
                "code": 200,
            }
        )

    if request.method == "POST" or request.method == "PUT":
        # request data
        data = expect_json({"subdomain": str, "zone": str})
        subdomain = data["subdomain"].lower()
        zone_name = data["zone"].lower()

        # check if record is valid or banned
        if not valid_input(subdomain):
            abort(400, "Not valid subdomain")
        if len(subdomain) < 4 or len(subdomain) > 50:
            abort(400, "Too long or too short subdomain (between 4 and 50)")
        if len(BannedRecord.query.filter_by(subdomain=subdomain).all()) != 0:
            abort(401, "Unauthorized to obtain requested subdomain")

        # verify that zone is valid
        zone = Zone.query.filter_by(zone=zone_name)
        if len(zone.all()) != 1:
            abort(404, f"No zone with name {zone_name} found")
        zone = zone.first()

        # if PUT, we delete the previous record
        if request.method == "PUT":
            search = Record.query.filter_by(ip=remote_addr)

            if len(search.all()) == 0:
                abort(404, "You do not have a subdomain")

            db.session.delete(search.first())
            db.session.commit()

        # lookup in table
        search = Record.query.filter_by(subdomain=subdomain, zone=zone)

        if len(search.all()) != 0 and search.first().ip == remote_addr:
            return jsonify(
                {
                    "success": True,
                    "name": "OK",
                    "description": f"You already have this subdomain {subdomain}.{zone.zone}",
                    "code": 200,
                }
            )

        if len(search.all()) != 0 and search.first().ip != remote_addr:
            abort(400, "Someone else has this subdomain")

        record = Record(subdomain=subdomain, ip=remote_addr, zone=zone)

        db.session.add(record)
        try:
            db.session.commit()
        except Exception as e:
            if "Duplicate entry" in str(e):
                abort(
                    400,
                    "You already have a subdomain",
                )
            raise e

        bind9.sync(zones=Zone.query.all(), records=Record.query.all())

        return jsonify(
            {
                "success": True,
                "name": "OK",
                "description": "Subdomain created",
                "code": 200,
            }
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
