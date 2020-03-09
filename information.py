from app import db
from app.models import Users, Skills


def create():
    db.create_all()
    db.session.commit()


def load_user():
    u = Users(emp_id='T0099', username='Mahantesh.R', email='mahanteshr17@gmail.com', overall_exp=1, manager_id='2188')
    u.set_password('1234')
    db.session.add(u)
    db.session.commit()


def print_user():
    user = Users.query.all()
    for u in user:
        print(u.emp_id, u.username, u.manager_id)
    # u1 = Users.query.get('T0099')
    """ok = u1.employees.all()
    for i in ok:
        print(i.emp_id, i.experience, i.emp_rating, i.location, i.practices)"""


if __name__ == '__main__':
    # print("Enter 0 - print_user, 1 - Load user : ")
    # i = bool(input())
    # if i == 1:
    # load_user()
    print_user()
    # create()
