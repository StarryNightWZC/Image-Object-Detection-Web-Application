from website import db


class Photo(db.Model):
    # 表的名字:
    __tablename__ = 'photos'
    username = db.Column(db.String(100))
    photourl=db.Column(db.String(100), primary_key=True)