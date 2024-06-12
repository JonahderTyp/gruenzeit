from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired


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
