from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Users, Skills
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, Details
from app import man_flag

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
    q = Skills.query.filter_by(manager_rating=None).join(Users).filter_by(manager_id=current_user.emp_id).all()
    print(type(q))
    if current_user.admin == 'Y':
        return render_template('dashboard_admin.html')
    user = Users.query.filter_by(manager_id=current_user.emp_id).first()
    if user is not None:
        for res in q:
            print("Update {} for {} skill ".format(res.employee_id, res.skill))
        return render_template('dashboard_manager.html', update=q)
    return render_template('dashboard.html', update=q)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/update_skill', methods=['GET', 'POST'])
def update_skill():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = dict(request.form)
        x = int((len(data) - 2) / 3)
        print(data, x)
        for i in range(1, x + 1):
            s = Skills(employee_id=current_user.emp_id, skill=data['skills' + str(i)],
                       skill_exp=data['experience' + str(i)], emp_rating=data['rating' + str(i)])
            db.session.add(s)
            db.session.commit()
        u = Users.query.filter_by(emp_id=current_user.emp_id).first()
        u.practice = data['practice']
        u.location = data['location']
        db.session.commit()
        return redirect('dashboard')
    return render_template('update_skill.html', title='Update Skill')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        data = dict(request.form)
        z = db.session.query(db.func.max(Skills.skill_id)).group_by(Skills.skill, Skills.employee_id).all()
        print(data)
        print(z)
        t = int(len(data)/3)
        flag = []
        ratings_all = []
        for p in range(1, t+1):
            res = []
            rating = {}
            for i in z:
                x = Skills.query.filter_by(skill_id=i[0]).first()
                print(x)
                if x.manager_rating is not None:
                    if x.skill == data['skills' + str(p)] and x.skill_exp >= int(data['experience' + str(p)]) and (x.emp_rating + x.manager_rating) / 2 >= int(data['rating' + str(p)]):
                        rating.update({x.employee_id: (x.emp_rating+x.manager_rating)/2})
                else:
                    if x.skill == data['skills' + str(p)] and x.skill_exp >= int(data['experience' + str(p)]) and x.emp_rating >= int(data['rating' + str(p)]):
                        rating.update({x.employee_id: x.emp_rating})
                        flag.append(x.employee_id)
            ratings_all.append(rating)
        print(flag)
        print(ratings_all)
        inter = list(ratings_all[0].keys())
        for i in range(0, len(ratings_all)-1):
            if i == 0:
                inter = list(set(list(ratings_all[i].keys())) & set(list(ratings_all[i+1].keys())))
            else:
                inter = list(set(inter) & set(list(ratings_all[i+1].keys())))
        print(inter)
        final_res = []
        for i in inter:
            x = Users.query.filter_by(emp_id=i).first()
            avg = 0
            for p in ratings_all:
                avg = avg + p[i]
            avg = avg/len(ratings_all)
            # y=0 -> manager_rating present
            y = 0
            for j in flag:
                if i == j:
                    y = 1
                    break
            final_res.append((x, y, avg))
        print(final_res)
        final_res.sort(key=lambda x: float(x[2]), reverse=True)
        return render_template('search.html', title='Search', result=final_res)
    return render_template('search.html', title='Search')


@app.route('/manager', methods=['GET', 'POST'])
def manager():
    global man_flag
    print(man_flag)
    q = Skills.query.filter_by(manager_rating=None).join(Users).filter_by(manager_id=current_user.emp_id).all()
    print(q)
    # flag = request.form['flag1']
    # print(flag)
    for res in q:
        print("Update {} for {} skill ".format(res.employee_id, res.skill))
    if request.method == 'POST' and request.form.get("choose_employee") is not None:
        # flag = request.form['flag']
        print("prev flag:", man_flag)
        if man_flag == 0:
            man_flag = 1
        else:
            man_flag = 0
        print("flag:", man_flag)
        id = request.form.get("choose_employee")
        rating = request.form.get("manager_rating")
        print(id, rating)
        s = Skills.query.filter_by(skill_id=id).all()
        if man_flag == 0:
            s[0].manager_rating = rating
            print(rating)
            db.session.commit()
        print(s)
        q = Skills.query.filter_by(manager_rating=None).join(Users).filter_by(manager_id=current_user.emp_id).all()
        name = db.session.query(Users.username).filter_by(emp_id=s[0].employee_id).first()
        return render_template('manager_rating.html', skills=q, name=name[0], skill=s, flag=man_flag)
    return render_template('manager_rating.html', skills=q, flag=man_flag)


