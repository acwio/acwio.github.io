from django import template
import dateutil.parser

# get a reference to the template library
register = template.Library()

@register.filter(name='string_to_datetime')
def string_to_datetime(date):
    '''
    Converts date from string to DateTime object.
    :param date: a string object containing Date information.
    :return:    a DateTime object of the given string.
    '''
    return dateutil.parser.parse(date)