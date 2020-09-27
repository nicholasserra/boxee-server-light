from app import db


class AppRequest(db.Model):
    """
    CREATE TABLE app_request (
        id SERIAL PRIMARY KEY,
        ip VARCHAR,
        endpoint VARCHAR,
        timestamp timestamptz
    )
    """

    __tablename__ = 'app_request'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String())
    endpoint = db.Column(db.String())
    timestamp = db.Column(db.DateTime(timezone=True))

    def __init__(self, ip, endpoint, timestamp):
        self.ip = ip
        self.endpoint = endpoint
        self.timestamp = timestamp

    def __repr__(self):
        return 'AppRequest {}'.format(self.id)
