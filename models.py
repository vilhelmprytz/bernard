from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Zone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zone = db.Column(
        db.String(253), unique=True, nullable=False
    )  # 253 maximum length of domain?
    dns_provider = db.Column(db.String(255), nullable=False)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subdomain = db.Column(
        db.String(253), unique=True, nullable=False
    )  # 253 maximum length of domain?
    ip = db.Column(db.String(15), unique=True, nullable=False)

    zone_id = db.Column(db.Integer, db.ForeignKey("zone.id"), nullable=False)
    zone = db.relationship("Zone", backref=db.backref("records", lazy=True))
