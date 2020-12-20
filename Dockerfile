FROM debian as builder
LABEL maintainer="Frederic Aoustin <fraoustin@gmail.com>"

RUN apt-get update && apt-get install -y \
        minify \
    && rm -rf /var/lib/apt/lists/* 

RUN mkdir /agenda
RUN mkdir /agenda/files
COPY ./files/ /agenda/files/
WORKDIR /agenda/files/css
RUN minify -o icon.css icon.css
RUN minify -o agenda.css agenda.css
WORKDIR /agenda/files/javascripts
RUN minify -o agenda.js agenda.js

FROM python:3.8-alpine

RUN mkdir /data
VOLUME /data

RUN mkdir /agenda
COPY . /agenda/
RUN rm -rf /agenda/files
COPY --from=builder /agenda/files /agenda/files
RUN rm -rf /agenda/entrypoint.sh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN pip install -r /agenda/REQUIREMENTS.txt

ENV AGENDA_PORT 5000
ENV AGENDA_DEBUG false
ENV AGENDA_HOST 0.0.0.0
ENV AGENDA_DIR http://localhost/

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["agenda"]