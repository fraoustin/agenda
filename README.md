# agenda

TODO

## Usage by docker

    docker run -d -v <localpath>:/data --name mapit -p 5000:80 fraoustin/jlat

You can used the environment:

- JLAT_PORT default 5000
- JLAT_DEBUG default false
- JLAT_HOST default 0.0.0.0
- JLAT_DIR default /data