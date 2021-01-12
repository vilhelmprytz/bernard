from flask import Flask, request, jsonify, abort
import os
from dns_providers import *
from models import db, Zone, Record

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "bernard")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "password")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "bernard")

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/api/subdomain", methods=["POST", "GET"])
def index():
    if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
        remote_addr = request.environ["REMOTE_ADDR"]
    else:
        remote_addr = request.environ["HTTP_X_FORWARDED_FOR"]

    if request.method == "POST":
        form = request.json
        subdomain = form["subdomain"]

        zone = Zone.query.filter_by(zone=form["zone"]).first()

        record = Record(subdomain=form["subdomain"], ip=remote_addr, zone=zone)
        db.session.add(record)
        try:
            db.session.commit()
        except Exception as e:
            if "Duplicate entry" in str(e):
                abort(400, "You already have a subdomain!")
            raise e

        try:
            globals()[zone.dns_provider].add(
                zone=zone.zone, subdomain=subdomain, ip=remote_addr
            )  # dirty way to execute str as func
        except Exception as e:
            db.session.delete(record)
            db.session.commit()
            raise e

        return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0")
