from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Users, Skills
from werkzeug.urls import url_parse
import json

from app import app, db
from app.forms import LoginForm
from sqlalchemy import extract

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    q = Skills.query.filter_by(manager_rating=None).join(Users).filter_by(manager_id=current_user.id).all()
    if current_user.admin == 'Y':
        return render_template('dashboard_admin.html')
    user = Users.query.filter_by(manager_id=current_user.id).first()
    if user is not None:
        return render_template('dashboard_manager.html', update=q)
    return render_template('dashboard.html', update=q)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/update_skill', methods=['GET', 'POST'])
def update_skill():
    x = db.session.query(db.func.max(Skills.skill_id)).group_by(Skills.skill, Skills.employee_id).filter(
        Skills.employee_id == current_user.id).all()
    print(x)
    skills = []
    for i in x:
        skills.append(Skills.query.filter_by(skill_id=i[0]).first())
    print(skills)
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = dict(request.form)
        p = []
        for key in data:
            if "skills" in key:
                p.append(key[6:])
        print(p)
        print(data, x)
        for i in p:
            s = Skills(employee_id=current_user.id, skill=data['skills' + i],
                       skill_exp=data['experience' + i], emp_rating=data['rating' + i])
            db.session.add(s)
            db.session.commit()
        return redirect('dashboard')
    return render_template('update_skill.html', title='Update Skill', skills=skills, len=len(skills))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = dict(request.form)
        z = db.session.query(db.func.max(Skills.skill_id)).group_by(Skills.skill, Skills.employee_id).all()
        print(data)
        print(z)
        t = []
        for key in data:
            if "skills" in key:
                t.append(key[6:])
        print(t)
        flag = []
        ratings_all = []
        final_res = []
        u = Users.query.filter(Users.admin == 'N').all()
        for i in u:
            final_res.append((i, 0))
        print(final_res)
        for p in t:
            if data['skills'+p] == "any":
                return render_template('search.html', title='Search', result=final_res)
        for p in t:
            rating = {}
            for i in z:
                x = Skills.query.filter_by(skill_id=i[0]).first()
                print(x)
                if x.manager_rating is not None:
                    if x.skill == data['skills' + p] and x.skill_exp >= int(data['experience' + p]) and (
                            x.emp_rating + x.manager_rating) / 2 >= int(data['rating' + p]):
                        rating.update({x.employee_id: (x.emp_rating + x.manager_rating) / 2})
                else:
                    if x.skill == data['skills' + p] and x.skill_exp >= int(
                            data['experience' + p]) and x.emp_rating >= int(data['rating' + p]):
                        rating.update({x.employee_id: x.emp_rating})
                        flag.append(x.employee_id)
            ratings_all.append(rating)
        print(flag)
        print(ratings_all)
        inter = list(ratings_all[0].keys())
        for i in range(0, len(ratings_all) - 1):
            if i == 0:
                inter = list(set(list(ratings_all[i].keys())) & set(list(ratings_all[i + 1].keys())))
            else:
                inter = list(set(inter) & set(list(ratings_all[i + 1].keys())))
        print(inter)
        final_res = []
        for i in inter:
            x = Users.query.filter_by(id=i).first()
            avg = 0
            for p in ratings_all:
                avg = avg + p[i]
            avg = avg / len(ratings_all)
            y = 0
            for j in flag:
                if i == j:
                    y = 1
                    break
            final_res.append((x, y, avg))
        print(final_res)
        final_res.sort(key=lambda x: float(x[2]), reverse=True)
        print(final_res)
        return render_template('search.html', title='Search', result=final_res)
    return render_template('search.html', title='Search')


@app.route('/manager_rating', methods=['GET', 'POST'])
def manager_rating():
    q = Users.query.filter_by(manager_id=current_user.id).all()
    print(q)
    if request.method == 'POST':
        data = dict(request.form)
        print(data)
        if data["flag"] == "select":
            u = Users.query.filter_by(id=data['choose_employee']).first()
            q.insert(0, q.pop(q.index(Users.query.filter_by(id=data['choose_employee']).first())))
            name = u.username
            print(u, q)
            x = db.session.query(db.func.max(Skills.skill_id)).group_by(Skills.skill, Skills.employee_id).filter(Skills.employee_id == data['choose_employee']).all()
            print(x)
            s = []
            for i in x:
                s.append(Skills.query.filter_by(skill_id=i[0]).first())
            print(s)
            return render_template('manager_rating.html', emp=q, skills=s, name=name, flag=1)
        else:
            u = Users.query.filter_by(id=data['choose_employee']).first()
            name = u.username
            x = db.session.query(db.func.max(Skills.skill_id)).group_by(Skills.skill, Skills.employee_id).filter(Skills.employee_id == data['choose_employee']).all()
            print(x)
            s = []
            for i in x:
                s.append(Skills.query.filter_by(skill_id=i[0]).first())
            for j in s:
                rating = data['manager_rating' + str(j.skill_id)]
                j.manager_rating = rating
                print(rating)
                db.session.commit()
            return render_template('manager_rating.html', emp=q, skills=s, name=name, flag=0)
    return render_template('manager_rating.html', emp=q, flag=0)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        p = request.form.get("practice")
        l = request.form.get("location")
        print(p, l)
        u = Users.query.filter_by(id=current_user.id).first()
        u.practice = p
        u.location = l
        db.session.commit()
        return redirect('dashboard')
    return render_template('edit_profile.html')


@app.route('/overall_statistics')
def overall_stats():
    x = db.session.query(Skills.skill, db.func.count(Skills.employee_id.distinct())).group_by(Skills.skill).all()
    print(x)
    data = [['Tech', 'No. of ppl']]
    for i in x:
        data.append([i[0], i[1]])
    print(data)
    y = db.session.query(Skills.skill, db.func.count(Skills.employee_id.distinct())).group_by(Skills.skill).all()
    print(y)
    data1 = [
        ['Year', 'Python', 'Java', 'HTML'],
        ['2014', 4.5, 3.9, 4.2],
        ['2015', 4.5, 3.7, 4.3],
        ['2016', 3.9, 4.0, 4.4],
        ['2017', 3.9, 3.8, 4.5]
    ]
    print(json.dumps(data))
    return render_template('overall_stats.html', data=json.dumps(data), data1=json.dumps(data1))


@app.route('/emp_stats/<string:id>', methods=['GET', 'POST'])
def emp_stats(id):
    print(id)
    d = db.session.query(Skills.skill.distinct()).filter_by(employee_id=id).order_by(Skills.skill_id).all()
    t = db.session.query(extract('year', Skills.timestamp), extract('month', Skills.timestamp),
                         extract('day', Skills.timestamp),Skills.skill,Skills.emp_rating).filter_by(employee_id=id).order_by(Skills.skill_id).all()
    res =[['time']]
    for i in d:
        res[0].append(i[0])
    print(res)
    x = [0]*len(res[0])
    for i in t:
        x[0] = (i[0], i[1], i[2])
        x[res[0].index(i[3])] = i[4]
        res.append(x[:])
    print(res)
    return render_template('emp_stat.html', data=json.dumps(res))
