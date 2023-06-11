from app import db, bcrypt

class User(db.Document):
    email = db.EmailField(unique=True, required=True)
    password = db.BinaryField(required=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)