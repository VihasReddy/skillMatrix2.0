from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class Details(FlaskForm):
    skills = SelectField('Skills', choices=[('Java', 'Java'), ('Python', 'Python'), ('Angular', 'Angular'),
                                            ('NodeJS', 'NodeJS'), ('DJango', 'DJango'), ('ReactJS', 'ReactJS'),
                                            ('Javascript', 'Javascript'), ('Scala', 'Scala')])
    experience = IntegerField('Experience(in years)', validators=[DataRequired()])
    emp_rating = SelectField('Rating', choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6), ('7', 7),
                                                ('8', 8), ('9', 9), ('10', 10)])
    location = SelectField('Location(current working)', choices=[('Bangalore, India', 'Bangalore, India'),
                                                                 ('Pune, India', 'Pune, India'),
                                                                 ('Hyderabad, India', 'Hyderabad, India'),
                                                                 ('Amsterdam, Netherlands', 'Amsterdam, Netherlands')])
    practices = SelectField('Practice', choices=[('PowerMe', 'PowerMe'), ('Step', 'Step'), ('Leap', 'Leap'),
                                                 ('Atlassian', 'Atlassian')])
    submit = SubmitField('Submit')

# class Search(FlaskForm):
