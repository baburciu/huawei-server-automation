curl -k -s  https://$ip/redfish/v1/Chassis/1/  -u <user>:<pass> -X GET | jq .SerialNumber
# per https://hewlettpackard.github.io/ilo-rest-api-docs/ilo5/?shell#serialnumber294

# boburciu@WX-5CG020BDT2:~$ for ip in {192.168.X.22,192.168.X.24};do (echo -n "$ip        " ;curl -k -s  https://$ip/redfish/v1/Chassis/1/  -u admin:### -X GET | jq .SerialNumber) ;done
# 192.168.X.22        "CZ2XXX03QQ"
# 192.168.X.24        "CZ2XXX03QX"
# boburciu@WX-5CG020BDT2:~$
