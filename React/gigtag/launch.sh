docker run -d --restart always -p 80:80 --name gigtag-fe gigtag:fe
docker run -d --restart always -p 8120:8120 --mount type=bind,source="$(pwd)"/data,target=/gigtag/data --name gigtag-be gigtag:be
