from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo


class BaustelleForm(FlaskForm):
    auftragsnummer = StringField('Auftragsnummer', validators=[DataRequired()])
    auftragsname = StringField('Auftragsname', validators=[DataRequired()])
    auftragsadresse = StringField('Adresse', validators=[DataRequired()])
    auftragsbeschreibung = TextAreaField(
        'Beschreibung', validators=[DataRequired()])
    status = SelectField('Status', coerce=int, validators=[DataRequired()])
    submit_update = SubmitField('Update')
    submit_delete = SubmitField('Delete')


class VehicleForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    kennzeichen = StringField('Kennzeichen', validators=[DataRequired()])
    submit = SubmitField('Submit')


class VehicleSelectForm(FlaskForm):
    vehicle = SelectField('Vehicle', choices=[
                          (-1, 'Kein Fahrzeug')], validators=[DataRequired()])
    submit = SubmitField('Farhzeug wechseln')


class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
                                     DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Change Password')
