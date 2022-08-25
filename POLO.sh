#!bash

for i in $(seq ${1:-1}) ; do
    file=POLO/polo.$i.html
    echo $file
    if [[ ! -f $file ]] ; then
        curl -A "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0" -H "Accept-Encoding: deflate, br" -H "Accept-Language: es; q=0.$(($RANDOM%10))" "https://www.coches.net/segunda-mano/?MakeId=47&ModelId=109&pg=$i" -o $file
        sleep 10
    fi
done