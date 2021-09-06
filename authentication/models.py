from flask_sqlalchemy import SQLAlchemy;

db = SQLAlchemy();


class UserRole(db.Model):
    __tablename__ = "userRoles"
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    roleId = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)



class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    ime = db.Column(db.String(256), nullable=False)
    prezime = db.Column(db.String(256), nullable=False)
    jmbg = db.Column(db.String(13), nullable=False)
    roles = db.relationship("Role", secondary=UserRole.__table__, back_populates="users")


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    users = db.relationship("User", secondary=UserRole.__table__, back_populates="roles")

    def __repr__(self):
        return self.name;
