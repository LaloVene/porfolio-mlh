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

# assert ()                 # exit if string not found in text
# {
#   text=$1
#   string=$2

#   if [[ $text == *"$string"* ]];
#   then
#     echo "'$string': passed"
#   else
#     echo "'$string' not found in text:"
#     echo "$text"
#     # exit 99
#   fi
# }

# server="https://lalovene.duckdns.org/"
# username="$RANDOM"
# password="$RANDOM"
# wrongpassword="wrongpw"

# homepage () { curl -s $server; }
# about () { curl -s $server"/about"; }
# register () { curl -s -d "username=$1&password=$2" -X POST $server"/register"; }
# login () { curl -s -d "username=$1&password=$2" -X POST $server"/login"; }

# assert "$(homepage)" "Eduardo Venegas"
# assert "$(about)" "About Me"
# assert "$(register "" "$password")" "Username is required."
# assert "$(register "$username" "")" "Password is required."
# assert "$(register "$username" "$password")" "User ${username} created successfully"
# assert "$(register "$username" "$password")" "User ${username} is already registered."
# assert "$(login "" "$password")" "Incorrect username."
# assert "$(login "$username" "")" "Incorrect password."
# assert "$(login "$username" "$wrongpassword")" "Incorrect password."
# assert "$(login "$username" "$password")" "Login Successful"