from flask import Blueprint, current_app, flash, request, render_template, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime, timedelta

from caldav.elements.ical import CalendarColor

class Event:

    def __init__(self, evt, cal):
        self.evt = evt
        self.cal = cal

    def __getattr__(self, id):
        if id == 'summary':
            return self.evt.vobject_instance.vevent.summary.value
        if id == 'start':
            dte = self.evt.vobject_instance.vevent.dtstart.value.strftime('%d/%m/%Y %H:%M')
            if dte.endswith(" 00:00"):
                return dte[:-6]
            return dte
        if id == 'end':
            dte = self.evt.vobject_instance.vevent.dtend.value.strftime('%d/%m/%Y %H:%M')
            if dte.endswith(" 00:00"):
                return dte[:-6]
            return dte
        if id == 'timestart':
            dte = self.evt.vobject_instance.vevent.dtstart.value.strftime('%H:%M')
            if dte.endswith("00:00"):
                return ""
            return dte
        if id == 'timeend':
            dte = self.evt.vobject_instance.vevent.dtend.value.strftime('%H:%M')
            if dte.endswith("00:00"):
                return ""
            return dte
        if id == 'color':
            return self.cal.get_properties([CalendarColor(),])['{http://apple.com/ns/ical/}calendar-color']
        return None



class Day:

    def __init__(self, day):
        self.day = day

    @property
    def events(self):
        events = []
        for calendar in current_user.calendars:
            events = events + [Event(evt, calendar) for evt in calendar.date_search(self.day, self.day+ timedelta(days=5), expand=True)]
        return events


@login_required
def day():
    day = request.args.get('day', datetime.today())
    return render_template('events.html', days=[Day(day),])


class Events(Blueprint):

    def __init__(self, name='events', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/', 'day', day, methods=['GET'])
        
       
    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init events on register is failed")