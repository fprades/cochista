
# python -m http.server 
echo http://$(ifconfig | grep "inet 172" | tr -s " " | cut -d" " -f3):8000