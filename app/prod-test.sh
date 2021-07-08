#!/bin/sh

server="https://lalovene.duckdns.org/"
while read endpoint;
do
response=$(curl --write-out '%{http_code}' --silent --output /dev/null $server$endpoint)
if [[ $response == "200" ]]; then
echo "Success /"$endpoint
else
echo "Error /"$endpoint
exit 1
fi

done < endpoint.txt
exit 0