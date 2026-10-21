from extensions import db


class Brand(db.Model):
    __tablename__ = 'brand'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)

    products = db.relationship('Product', backref='brand', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "description": self.description
        }
