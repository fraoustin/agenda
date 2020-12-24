from flask import Blueprint, current_app, flash, request, render_template, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime, timedelta
import uuid

from caldav.elements.ical import CalendarColor
from caldav.elements import dav, cdav

vcal = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:%(uid)s
DTSTAMP:20110510T182145Z
DTSTART:%(start)s
DTEND:%(end)s
SUMMARY:%(summary)s
DESCRIPTION:%(description)s
END:VEVENT
END:VCALENDAR
"""

class Event:

    def __init__(self, evt, cal):
        self.evt = evt
        self.cal = cal

    def save(self, no_overwrite=False, no_create=False):
        self.evt.vobject_instance.vevent.save(no_overwrite=no_overwrite, no_create=no_create, obj_type='event')

    def __setattr__(self, id, value):
        if id == 'summary':
            self.evt.vobject_instance.vevent.summary.value = value
        elif id == 'description':
            self.evt.vobject_instance.vevent.description.value = value
        elif id == 'start':
            self.evt.vobject_instance.vevent.dtstart.value = datetime.strptime(value, '%d/%m/%Y %H:%M') 
        elif id == 'end':
            self.evt.vobject_instance.vevent.dtend.value = datetime.strptime(value, '%d/%m/%Y %H:%M')
        else:
            super().__setattr__(id, value)

    def __getattr__(self, id):
        if id == 'uid':
            return self.evt.vobject_instance.vevent.uid.value
        if id == 'uidsimple':
            simple = self.evt.vobject_instance.vevent.uid.value
            return simple.replace('-','')
        if id == 'summary':
            return self.evt.vobject_instance.vevent.summary.value
        if id == 'description':
            return self.evt.vobject_instance.vevent.description.value
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
        if id == 'daystart':
            return self.evt.vobject_instance.vevent.dtstart.value.strftime('%d/%m/%Y')
        if id == 'hourstart':
            return self.evt.vobject_instance.vevent.dtstart.value.strftime('%H')
        if id == 'minstart':
            return self.evt.vobject_instance.vevent.dtstart.value.strftime('%M')
        if id == 'dayend':
            return self.evt.vobject_instance.vevent.dtend.value.strftime('%d/%m/%Y')
        if id == 'hourend':
            return self.evt.vobject_instance.vevent.dtend.value.strftime('%H')
        if id == 'minend':
            return self.evt.vobject_instance.vevent.dtend.value.strftime('%M')
        return None

    def delete(self):
        return self.evt.delete()
    def __lt__(self, other):
        return self.timestart < other.timestart

    def __le__(self, other):
        return self.timestart <= other.timestart

    def __eq__(self, other):
        return self.timestart == other.timestart

    def __ne__(self, other):
        return self.timestart != other.timestart

    def __gt__(self, other):
        return self.timestart > other.timestart

    def __ge__(self, other):
        return self.timestart >= other.timestart



class Day:

    def __init__(self, day):
        self.day = day
    
    def __str__(self):
        return self.day.strftime('%d/%m/%Y')

    @property
    def a(self):
        return self.day.strftime('%A')[0]

    @property
    def d(self):
        return self.day.strftime('%d')
        
    @property    
    def m(self):
        return self.day.strftime('%m')
        
    @property    
    def link(self):
        return "/?day=%s" % self.day.strftime('%Y%m%d')
        
    @property    
    def next(self):
        if current_app.config["AGENDA_START_WEEK_MONDAY"] == True:
            day_start = self.day - timedelta(days= int(self.day.weekday()))
        else:
            day_start = self.day - timedelta(days= int(self.day.weekday())+1)
        return Day(day_start + timedelta(days=7))
        
    @property    
    def prev(self):
        if current_app.config["AGENDA_START_WEEK_MONDAY"] == True:
            day_start = self.day - timedelta(days= int(self.day.weekday()))
        else:
            day_start = self.day - timedelta(days= int(self.day.weekday())+1)
        return Day(day_start - timedelta(days=1))
        
    @property    
    def days_of_week(self):
        if current_app.config["AGENDA_START_WEEK_MONDAY"] == True:
            day_start = self.day - timedelta(days= int(self.day.weekday()))
        else:
            day_start = self.day - timedelta(days= int(self.day.weekday())+1)
        days = []
        for cnt in range(0,7):
            days.append(Day(day_start + timedelta(days = cnt)))
        return days

    @property
    def events(self):
        events = []
        for calendar in current_user.calendars:
            events = events + [Event(evt, calendar) for evt in calendar.date_search(self.day, self.day+ timedelta(days=1), expand=True)]
        events.sort()
        return events    

@login_required
def day():
    day = datetime.strptime(request.args.get('day', datetime.today().strftime('%Y%m%d')), '%Y%m%d')
    return render_template('events.html', day=Day(day))

@login_required
def add():
    summary = request.form['summary']
    daystart = request.form['daystart']
    hourstart = request.form['hourstart']
    minstart = request.form['minstart']
    dayend = request.form['dayend']
    hourend = request.form['hourend']
    minend = request.form['minend']
    description = request.form['description']
    start = datetime.strptime("%s %s:%s" % (daystart, hourstart, minstart), '%d/%m/%Y %H:%M').strftime('%Y%m%dT%H%M00Z')
    end = datetime.strptime("%s %s:%s" % (dayend, hourend, minend), '%d/%m/%Y %H:%M').strftime('%Y%m%dT%H%M00Z')
    if "%s:%s" % (hourstart, minstart) == "00:00" and start == end:
        end = datetime.strptime("%s %s:%s" % (dayend, hourend, minend), '%d/%m/%Y %H:%M') + + timedelta(days=1)
        end = end.strftime('%Y%m%dT%H%M00Z')
    uid = str(uuid.uuid4())
    calendar = current_user.calendars[0]
    if len(current_app.config['AGENDA_DEFAULT']) > 0:
        for cal in current_user.calendars:
            if cal.get_properties([dav.DisplayName(),])['{DAV:}displayname'] == current_app.config['AGENDA_DEFAULT']:
                calendar = cal
    calendar.add_event(vcal % {'uid': uid, 'start': start, 'end': end, 'summary': summary, 'description': description})
    day = datetime.strptime(daystart, '%d/%m/%Y').strftime('%Y%m%d')
    return redirect(url_for('events.day', day=day))

@login_required
def update():
    summary = request.form['summary']
    uid = request.form['uid']
    daystart = request.form['daystart']
    hourstart = request.form['hourstart']
    minstart = request.form['minstart']
    dayend = request.form['dayend']
    hourend = request.form['hourend']
    minend = request.form['minend']
    description = request.form['description']
    for calendar in current_user.calendars:
        try:
            evt = Event(calendar.event_by_uid(uid), calendar)
            evt.start = "%s %s:%s" % (daystart, hourstart, minstart)
            if not len(dayend): dayend= daystart
            if not len(hourend): hourend = hourstart
            if not len(minend): minend = minstart
            evt.description = description
            evt.summary = summary
            data = evt.evt._get_data()
            try:
                evt.end = "%s %s:%s" % (dayend, hourend, minend)
                data = evt.evt._get_data()
            except:
                if "%s %s:%s" % (dayend, hourend, minend) != "%s %s:%s" % (daystart, hourstart, minstart):
                    end = datetime.strptime("%s %s:%s" % (dayend, hourend, minend), '%d/%m/%Y %H:%M').strftime('%Y%m%dT%H%M00Z')
                    data = data.replace('END:VEVENT', 'DTEND:%s\nEND:VEVENT' % end)
            evt.delete()
            calendar.add_event(data)
        except Exception as err:
            print(err)

    day = datetime.strptime(daystart, '%d/%m/%Y').strftime('%Y%m%d')
    return redirect(url_for('events.day', day=day))

@login_required
def trash():
    uid = request.form['uid']
    daystart = request.form['daystart']
    for calendar in current_user.calendars:
        try:
            evt = calendar.event_by_uid(uid)
            evt.delete()
        except Exception as err:
            print(err)
    day = datetime.strptime(daystart, '%d/%m/%Y').strftime('%Y%m%d')
    return redirect(url_for('events.day', day=day))


class Events(Blueprint):

    def __init__(self, name='events', import_name=__name__, *args, **kwargs):
        Blueprint.__init__(self, name, import_name, template_folder='templates', *args, **kwargs)
        self.add_url_rule('/', 'day', day, methods=['GET'])
        self.add_url_rule('/add', 'add', add, methods=['POST'])
        self.add_url_rule('/update', 'update', update, methods=['POST'])
        self.add_url_rule('/trash', 'trash', trash, methods=['POST'])
        
       
    def register(self, app, options, first_registration=False):
        try:
            Blueprint.register(self, app, options, first_registration)
        except:
            app.logger.error("init events on register is failed")