from app import db


class Picture(db.Model):

    __table_name__ = 'pictures'

    id = db.Column(db.Integer, primary_key=True)

    # Instagram user id
    uid = db.Column(db.String(), nullable=False)

    # Instagram filename
    name = db.Column(db.String(), nullable=False)

    # App average rate
    average_rate = db.Column(db.SmallInteger, nullable=False, default=0)

    def serialize(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'name': self.name,
            'average_rate': self.average_rate
        }
