#!bash

for i in $(seq ${1:-1}) ; do
    file=X1e/x1e.$i.html
    echo $file
    if [[ ! -f $file ]] ; then
        curl -A "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0" -H "Accept-Encoding: deflate, br" -H "Accept-Language: es; q=0.$(($RANDOM%10))" "https://www.coches.net/segunda-mano/?Fueltype2List=5&MakeId=7&ModelId=944&pg=$i" -o $file
        sleep 10
    fi
done