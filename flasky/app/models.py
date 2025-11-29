from . import db


class Discipline(db.Model):
    __tablename__ = 'disciplines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    semester = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Discipline {self.name} (sem {self.semester})>'
