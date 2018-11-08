from wtforms.widgets.core import html_params
from wtforms.widgets import HTMLString
from wtforms import StringField, BooleanField
from flask_wtf import FlaskForm
from wtforms.validators import Length


class InlineButtonWidget(object):
    """
    Render a basic ``<button>`` field.
    """
    input_type = 'submit'
    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        kwargs.setdefault('value', field.label.text)
        return HTMLString('<button %s>' % self.html_params(name=field.name, **kwargs))


class InlineSubmitField(BooleanField):
    """
    Represents an ``<button type="submit">``.  This allows checking if a given
    submit button has been pressed.
    """
    widget = InlineButtonWidget()


#class SignupForm(FlaskForm):
#    name = StringField('Name', [Length(min=1, max=200)])
#    submit = InlineSubmitField('sign up')