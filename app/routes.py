from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Users, Skills
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, Details


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
    for res in q:
        print("Update {} for {} skill ".format(res.employee_id, res.skill))
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
        search_res = []
        z = db.session.query(db.func.max(Skills.skill_id)).group_by(Skills.skill, Skills.employee_id).all()
        print(data)
        print(z)
        t = int(len(data)/3)
        flag = []
        for p in range(1, t+1):
            res = []
            for i in z:
                x = Skills.query.filter_by(skill_id=i[0]).first()
                print(x)
                if x.manager_rating is not None:
                    if x.skill == data['skills' + str(p)] and x.skill_exp >= int(data['experience' + str(p)]) and (x.emp_rating + x.manager_rating) / 2 >= int(data['rating' + str(p)]):
                        res.append(x.employee_id)
                else:
                    if x.skill == data['skills' + str(p)] and x.skill_exp >= int(data['experience' + str(p)]) and x.emp_rating >= int(data['rating' + str(p)]):
                        res.append(x.employee_id)
                        flag.append(x.employee_id)
            search_res.append(res)
        print(flag)
        print(search_res)
        inter = search_res[0]
        for i in range(0, len(search_res)-1):
            if i == 0:
                inter = list(set(search_res[i]) & set(search_res[i+1]))
            else:
                inter = list(set(inter) & set(search_res[i + 1]))
        print(inter)
        final_res = []
        for i in inter:
            x = Users.query.filter_by(emp_id=i).first()
            # y=0 -> manager_rating present
            y = 0
            for j in flag:
                if i == j:
                    y = 1
                    break;
            final_res.append((x, y))
        print(final_res)
        return render_template('search.html', title='Search', result=final_res)
    return render_template('search.html', title='Search')


@app.route('/manager', methods=['GET', 'POST'])
def manager():
    id = request.args.get("id")
    skill_id = request.args.get("skill_id")
    print("acb")
    print(id, skill_id)
    cur = Skills.query.filter_by(skill_id=skill_id).first()
    print(cur.emp_rating)
    name = db.session.query(Users.username).filter_by(emp_id=cur.employee_id).first()
    print(name[0])
    if request.method == 'POST':
        data = dict(request.form)
        print(data)
        s = Skills.query.filter_by(skill_id=skill_id).first()
        s.set_manager_rating(data['manager_rating'])
        db.session.commit()
        return redirect('dashboard')
    return render_template('manager.html', name=name[0], skill=cur.skill, rating=int(cur.emp_rating))


