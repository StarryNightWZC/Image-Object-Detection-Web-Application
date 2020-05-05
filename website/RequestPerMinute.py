from website import db

class RequestPerMinute(db.Model):
    __tablename__ = 'requestperminute'
    requestid = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)  # A type for datetime.datetime() objects.

    def __repr__(self):
        return '<RequestPerMinute {}>'.format(self.instance_id)