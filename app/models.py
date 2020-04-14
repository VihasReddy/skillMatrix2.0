from app import db, login
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from datetime import datetime


@login.user_loader
def load_user(id):
    return Users.query.get(id)


class Users(UserMixin, db.Model):
    id = db.Column(db.String(24), primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    overall_exp = db.Column(db.Integer, index=True, nullable=True)
    location = db.Column(db.String(24), index=True)
    manager_id = db.Column(db.String(24))
    practice = db.Column(db.String(24), index=True)
    employees = db.relationship('Skills', backref='author', lazy='dynamic')
    admin = db.Column(db.Enum('N', 'Y'), index=True, server_default='N')

    def __repr__(self):
        return '<emp_id : {}><name : {}> <manager_id : {}> <admin_status: {}>'.format(self.id, self.username,
                                                                                      self.manager_id, self.admin)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_admin(self):
        self.admin = 'Y'


class Skills(db.Model):
    skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(24), db.ForeignKey('users.id'))
    skill = db.Column(db.String(24), index=True)
    skill_exp = db.Column(db.Integer, index=True)
    emp_rating = db.Column(db.Integer, index=True)
    manager_rating = db.Column(db.Integer, index=True)
    skill_interest = db.Column(db.Integer, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def set_manager_rating(self, rating):
        self.manager_rating = rating

    def get_overall_rating(self):
        return 0.4*self.emp_rating + 0.6*self.manager_rating

    def __repr__(self):
        return '<skill_id : {}><Employee ID : {}><skill : {}><exp : {}><emp_rating : {}><manager_rating : {} ' \
               '<timestamp : {}>'.format(self.skill_id, self.employee_id, self.skill, self.skill_exp, self.emp_rating,
                                         self.manager_rating, self.timestamp)


class LookupTable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String(120), index=True)
    field = db.Column(db.String(24), index=True)

    def __repr__(self):
        return '<value : {}><field : {}>'.format(self.value, self.field)
