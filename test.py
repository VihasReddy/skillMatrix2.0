from app import db
from app.models import Users, Skills, LookupTable


db.session.query(Users).delete()
db.session.commit()

u1 = Users(id='T0100', username='Vihas', email='vihasreddy@enquero.com', overall_exp=3, manager_id='T0099')
u2 = Users(id='T0101', username='Jagruth', email='jagruth@enquero.com', overall_exp=2, manager_id='T0100')
u3 = Users(id='T0102', username='Pruthvi', email='pruthvi@enquero.com', overall_exp=4, manager_id='T0100')
u4 = Users(id='T0099', username='Mahantesh.R', email='mahantesh@enquero.com', overall_exp=5, manager_id='T9999')
u1.set_password('1234')
u2.set_password('1234')
u3.set_password('1234')
u4.set_password('1234')
a1 = Users(id='admin', username='admin')
a1.set_admin()
a1.set_password('password')
db.session.add(a1)
db.session.add(u1)
db.session.add(u2)
db.session.add(u3)
db.session.add(u4)
db.session.commit()

users = Users.query.all()

for u in users:
    print(u)

skills = Skills.query.all()

for i in skills:
    print(i)

db.session.query(LookupTable).delete()
db.session.commit()

s1 = LookupTable(value='Python', field='skill')
s2 = LookupTable(value='Scala', field='skill')
s3 = LookupTable(value='JS', field='skill')
s4 = LookupTable(value='Communication', field='skill')
s5 = LookupTable(value='Java', field='skill')
l1 = LookupTable(value='Hyderabad', field='location')
l2 = LookupTable(value='Bangalore', field='location')
l3 = LookupTable(value='California', field='location')
db.session.add(s1)
db.session.add(s2)
db.session.add(s3)
db.session.add(s4)
db.session.add(s5)
db.session.add(l1)
db.session.add(l2)
db.session.add(l3)

db.session.commit()

l = LookupTable.query.all()

for i in l:
    print(i)

# current_user = Users.query.filter_by(id="T0100").first()
#
# r = db.engine.execute(
#     'select * from Users where id IN (select employee_id from Skills where skill_exp >= 3)').fetchall()
# x = db.engine.execute('select username from Users where overall_exp > ' + str(2)).fetchall()
# # y = db.engine.execute('select id from Users where manager_id LIKE 'T0100').fetchall()
#
# q = Skills.query.filter_by(manager_rating=None).join(Users).filter_by(manager_id=current_user.id).all()
#
# s = Skills.query.filter(Skills.skill_exp == 'Java')
#
# z = db.session.query(db.func.max(Skills.skill_id)).group_by(Skills.skill, Skills.employee_id).all()
#
# # res = db.session.query(Skills.employee_id).filter(Skills.skill == 'Java', Skills.skill_exp >= 2, (Skills.emp_rating + Skills.manager_rating)/2 >= 3)
#
# print(z)
#
# res =[]
#
#
# for i in z:
#     x = Skills.query.filter_by(skill_id=i[0]).first()
#     if x.manager_rating != None:
#         if x.skill == 'Java' and x.skill_exp >= 2 and (x.emp_rating + x.manager_rating) / 2 >= 3:
#             res.append(x)
#     else:
#         if x.skill == 'Java' and x.skill_exp >= 2 and x.emp_rating >= 3:
#             res.append(x)
#
# print(res)
#
# print(q[0].employee_id)
#
# for res in q:
#     print("Update {} for {} skill ".format(res.employee_id, res.skill))
