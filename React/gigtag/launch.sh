#docker run -d --restart always -p 8110:8110 --name gigtag-fe gigtag-fe-temp
#docker run -d --restart always --pull always --env-file='.env' -p 8120:8120 --mount type=bind,source="$(pwd)"/data,target=/gigtag/data --name gigtag-be ants3107/gigtag:be
#docker run -d --restart always --env-file='.env' -p 8120:8120 --mount type=bind,source="$(pwd)"/data,target=/gigtag/data --name gigtag-be gigtag-be-temp


docker run -d --restart always --pull always -p 8110:8110 --name gigtag-fe ants3107/gigtag:fe
