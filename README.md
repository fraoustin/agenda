# agenda

web interface for caldav

## Usage by docker

    git clone https://github.com/fraoustin/agenda.git
    cd agenda
    docker build -t agenda .
    docker run -d  -e AGENDA_CALDAV=http://mycaldav --name agenda -p 5000:80 agenda

You can used the environment:

- AGENDA_PORT 5000
- AGENDA_DEBUG false
- AGENDA_HOST 0.0.0.0
- AGENDA_CALDAV http://localhost/
- AGENDA_START_WEEK_MONDAY true