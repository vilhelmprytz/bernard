from flask import Flask, request, jsonify
import os
import string
from dns_providers import bind9
from models import db, Zone, Record, BannedIp, BannedRecord

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


def json_abort(code, msg):
    return jsonify({"success": False, "description": msg, "code": code}), code


def valid_input(variable):
    alnum = set(string.ascii_letters + string.digits)
    if any(x not in alnum for x in variable):
        return False
    return True


@app.route("/api/subdomain", methods=["POST", "PUT", "GET", "DELETE"])
def api_subdomain():
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        remote_addr = request.environ["REMOTE_ADDR"]
    else:
        remote_addr = request.environ["HTTP_X_FORWARDED_FOR"]

    # check if IP is banned
    if len(BannedIp.query.filter_by(ip=remote_addr).all()) != 0:
        return json_abort(401, "Your IP has been banned from using this servcice")

    if request.method == "GET":
        search = Record.query.filter_by(ip=remote_addr)

        if len(search.all()) == 0:
            return json_abort(404, "You do not have a subdomain")

        return jsonify(
            {
                "success": True,
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
            return json_abort(404, "You do not have a subdomain")

        db.session.delete(search.first())
        db.session.commit()

        bind9.sync(zones=Zone.query.all(), records=Record.query.all())

        return jsonify(
            {
                "success": True,
                "description": "Subdomain removed",
                "code": 200,
            }
        )

    if request.method == "POST" or request.method == "PUT":
        # request data
        form = request.json
        subdomain = form["subdomain"]
        zone_name = form["zone"]

        # check if record is valid or banned
        if not valid_input(subdomain):
            return json_abort(400, "Not valid subdomain")
        if len(subdomain) < 4 or len(subdomain) > 50:
            return json_abort(400, "Too long or too short subdomain (between 4 and 50)")
        if len(BannedRecord.query.filter_by(subdomain=subdomain).all()) != 0:
            return json_abort(401, "Unauthorized to obtain requested subdomain")

        # verify that zone is valid
        zone = Zone.query.filter_by(zone=zone_name)
        if len(zone.all()) != 1:
            return json_abort(400, "Invalid zone")
        zone = zone.first()

        # if PUT, we delete the previous record
        if request.method == "PUT":
            search = Record.query.filter_by(ip=remote_addr)

            if len(search.all()) == 0:
                return json_abort(404, "You do not have a subdomain")

            db.session.delete(search.first())
            db.session.commit()

        # lookup in table
        search = Record.query.filter_by(subdomain=form["subdomain"], zone=zone)

        if len(search.all()) != 0 and search.first().ip == remote_addr:
            return jsonify(
                {
                    "success": True,
                    "description": f"You already have this subdomain {subdomain}.{zone.zone}",
                    "code": 200,
                }
            )

        if len(search.all()) != 0 and search.first().ip != remote_addr:
            return json_abort(400, "Someone else has this subdomain")

        record = Record(subdomain=form["subdomain"], ip=remote_addr, zone=zone)

        db.session.add(record)
        try:
            db.session.commit()
        except Exception as e:
            if "Duplicate entry" in str(e):
                return json_abort(
                    400,
                    "You already have a subdomain, contact the subdomain provider to remove it!",
                )
            raise e

        bind9.sync(zones=Zone.query.all(), records=Record.query.all())

        return jsonify(
            {"success": True, "description": "Subdomain created", "code": 200}
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0")
