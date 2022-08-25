#!bash

for i in $(seq ${1:-1}) ; do
    file=X1/x1.$i.html
    echo $file
    if [[ ! -f $file ]] ; then
        curl -A "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0" -H "Accept-Encoding: deflate, br" -H "Accept-Language: es-ES, es; q=0.$(($RANDOM%10))" "https://www.coches.net/segunda-mano/?MakeId=7&ModelId=944&pg=$i" -o $file
        sleep 10
    fi
done