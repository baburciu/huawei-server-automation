curl -k -s  https://$ip/redfish/v1/  -u <user>:<pass> -X GET | jq .Oem.Hpe.Manager[0].HostName

# boburciu@WX-5CG020BDT2:~$ for ip in {192.168.X.22,192.168.X.24};do (echo -n "$ip        " ;curl -k -s   https://$ip/redfish/v1/  -u <user>:<pass> -X GET | jq .Oem.Hpe.Manager[0].HostName) ;done
# 192.168.X.130        "ILOCZ2XXXXLW0"
# 192.168.X.131        "ILOCZ2XXXXLW2"
# boburciu@WX-5CG020BDT2:~$

# For Huawei:
# [root@NetboX ~]#  curl -k -s  https://192.168.X.22/redfish/v1/  -u <user>:<pass> -X GET | jq .Oem.Huawei.HostName
# "2102311XBXXXXXXX0038"
# [root@NetboX ~]#
