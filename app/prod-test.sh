#!/bin/sh

server="https://lalovene.duckdns.org/"
while read endpoint;
do
response=$(curl --write-out '%{http_code}' --silent --output /dev/null $server$endpoint)
if [[ $response == "200" ]]; then
tput setaf 2; echo "Success /"$endpoint
else
tput setaf 1; echo "Error /"$endpoint
exit 1
fi
tput sgr0
done < endpoint.txt
exit 0