#! /usr/bin/env python3

# Gets network cards info from Huawei iBMC and returns a dictionary with key being the port and value being the MAC
# https://github.com/dell/ibmc-Redfish-Scripting/blob/master/Redfish%20Python/GetSystemHWInventoryREDFISH.py
# Bogdan Adrian Burciu 23/09/2021 vers 1

from pprint import pprint
import json
import requests
import sys
import warnings
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    ibmc_username = 'Administrator'
    ibmc_password = 'Orange123#'
    # def get_nics_mac_for_server_ibmc(server_ibmc_ip):
    #     # reach out to ibmc and get the MAC address as dict values for server_port keys
    #     GetSystemHWInventoryREDFISH_network.sys.argv = [server_ibmc_ip, server_ibmc_username, server_ibmc_password]
    #     GetSystemHWInventoryREDFISH_network.main()
    #     # above saves the network cards inventory from Dell PowerEdge server to local file hw_inventory.txt
    #     pattern = "^AssociatedNetworkAddresses"
    #     file = open("hw_inventory.txt", "r")
    #     lines = file.read()
    #     lines = lines.splitlines()
    #     for j, line in enumerate(lines):
    #         if re.search(pattern, line):
    #             next_line = lines[j + 6]
    #             # print(line)
    #             # print(next_line)
    #             # AssociatedNetworkAddresses: ['78:AC:44:0A:86:42']
    #             # Id: NIC.Integrated.1-1
    #             # :
    #             # AssociatedNetworkAddresses: ['40:A6:B7:3E:83:E1']
    #             # Id: NIC.Slot.1-2

    #             # choose to collect MAC only for slot NIC cards, as only those go to switches:
    #             if "NIC.Slot" in next_line:
    #                 server_port_mac = line.split('[\'')[1].split('\']')[0]
    #                 server_port_nic = 'NIC{}-P{}'.format(next_line.split('.')[-1].split('-')[0],
    #                                                      next_line.split('.')[-1].split('-')[1])
    #                 dict_server_port_mac[server_port_nic] = server_port_mac
    #             else:
    #                 continue
    #     print('\tFor server {} the MAC addresses are: \n{}\n'.format(server_ibmc_ip, dict_server_port_mac))
    #     return dict_server_port_mac

    def get_huawei_server_nic_mac(ibmc_ip, ibmc_username, ibmc_password):
        response = requests.get('https://%s/redfish/v1/Chassis/1/NetworkAdapters' % ibmc_ip,
                                verify=False, auth=(ibmc_username, ibmc_password))
        data = response.json()
        # print("\n\t\t >> Output of API call to /v1/Systems/1/NetworkAdapters:", data)   
        # data = {'@odata.context': '/redfish/v1/$metadata#Chassis/Members/1/NetworkAdapters/$entity',
        #         '@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters',
        #         '@odata.type': '#NetworkAdapterCollection.NetworkAdapterCollection',
        #         'Members': [{'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM'},
        #                     {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard1'},
        #                     {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard2'},
        #                     {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard3'}],
        #         'Members@odata.count': 4,
        #         'Name': 'NetworkAdapter Collection'}             
        if response.status_code != 200:
            print("\n- FAIL, get command failed, error is: %s" % data)
            sys.exit()        
        network_uri_list = []
        for i in data['Members']:
            network = i['@odata.id']
            network_uri_list.append(network)
        if not network_uri_list:
            message = "\n- WARNING, no network information detected for system\n"
        dict_server_port_mac = {}    
        for i in network_uri_list:
            # network_uri_list = ['/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM'
            #                     '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard1'
            #                     '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard4'
            #                     '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5']
            message = "\n- Network device details for %s -\n" % i.split("/")[-1]
            response = requests.get('https://%s%s' % (ibmc_ip, i), verify=False, auth=(ibmc_username, ibmc_password))
            data = response.json()
            # print("\n\t\t >> Output of API call to /redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM:", data)
            # data = {'@odata.context': '/redfish/v1/$metadata#Chassis/Members/1/NetworkAdapters/Members/$entity',
            #         '@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM',
            #         '@odata.type': '#NetworkAdapter.v1_0_0.NetworkAdapter',
            #         'Controllers': [{'ControllerCapabilities': {'NetworkPortCount': 4},
            #                         'FirmwarePackageVersion': None,
            #                         'Link': {'NetworkPorts': [{'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM/NetworkPorts/1'},
            #                                                 {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM/NetworkPorts/2'},
            #                                                 {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM/NetworkPorts/3'},
            #                                                 {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM/NetworkPorts/4'}],
            #                                 'NetworkPorts@odata.count': 4}}],
            #         'Id': 'mainboardLOM',
            #         'Manufacturer': 'Intel',
            #         'Model': 'X722',
            #         'Name': 'mainboardLOM',
            #         'NetworkPorts': {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM/NetworkPorts'},
            #         'Oem': {'Huawei': {'CardManufacturer': 'Huawei',
            #                         'CardModel': '2*10GE+2*GE',
            #                         'Configuration': {'Effective': True,
            #                                             'PortsConfig': [{'PFsInfo': [{'PFId': 0,
            #                                                                         'PermanentAddress': 'F063F9173678'}],
            #                                                             'PortId': 1},
            #                                                             {'PFsInfo': [{'PFId': 1,
            #                                                                         'PermanentAddress': 'F063F9173679'}],
            #                                                             'PortId': 2},
            #                                                             {'PFsInfo': [{'PFId': 0,
            #                                                                         'PermanentAddress': 'F063F917367A'}],
            #                                                             'PortId': 3},
            #                                                             {'PFsInfo': [{'PFId': 1,
            #                                                                         'PermanentAddress': 'F063F917367B'}],
            #                                                             'PortId': 4}]},
            #                         'DeviceLocator': 'LOM',
            #                         'DriverName': None,
            #                         'DriverVersion': None,
            #                         'Name': 'LOM',
            #                         'NetworkTechnology': ['Ethernet'],
            #                         'Position': 'mainboard',
            #                         'RootBDF': '0000:19:03.0'}},
            #         'Status': {'Health': 'OK', 'State': 'Enabled'}}
            if response.status_code != 200:
                print("\n- FAIL, get command failed, error is: %s" % data)
                sys.exit()
            for ii in data.items():
                if ii[0] == 'NetworkPorts':
                    url_port = ii[1]['@odata.id']
                    response = requests.get('https://%s%s' % (ibmc_ip, url_port), verify=False,
                                            auth=(ibmc_username, ibmc_password))
                    data = response.json()
                    # print('\n\t\t >> Output of API call to /redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM/NetworkPorts', data)
                    # data = {'@odata.context': '/redfish/v1/$metadata#Chassis/Members/1/NetworkAdapters/Members/mainboardPCIeCard5/NetworkPorts/$entity',
                    #     '@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5/NetworkPorts',
                    #     '@odata.type': '#NetworkPortCollection.NetworkPortCollection',
                    #     'Members': [{'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5/NetworkPorts/1'},
                    #                 {'@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5/NetworkPorts/2'}],
                    #     'Members@odata.count': 2,
                    #     'Name': 'Network Port Collection'}
                    if response.status_code != 200:
                        print("\n- FAIL, get command failed, error is: %s" % data)
                        sys.exit()
                    else:
                        port_uri_list = []
                        for j in data['Members']:
                            port_uri_list.append(j['@odata.id'])
                else:
                    pass
            for z in port_uri_list:
                # port_uri_list = ['/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5/NetworkPorts/1', 
                #                  '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5/NetworkPorts/2']
                response = requests.get('https://%s%s' % (ibmc_ip, z), verify=False,
                                        auth=(ibmc_username, ibmc_password))
                data = response.json()
                # print('\n\t\t >> Output of API call to /redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5/NetworkPorts/2', data)
                # data = {'@odata.context': '/redfish/v1/$metadata#Chassis/Members/1/NetworkAdapters/Members/mainboardPCIeCard5/NetworkPorts/Members/$entity',
                #         '@odata.id': '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5/NetworkPorts/1',
                #         '@odata.type': '#NetworkPort.v1_0_0.NetworkPort',
                #         'AssociatedNetworkAddresses': ['AC:75:1D:AD:B7:FE'],
                #         'Id': '1',
                #         'LinkStatus': None,
                #         'Name': '1',
                #         'Oem': {'Huawei': {'BDF': '0000:88:00.0',
                #                             'DriverName': None,
                #                             'DriverVersion': None,
                #                             'FirmwarePackageVersion': None,
                #                             'PortType': 'OpticalPort'}},
                #         'PhysicalPortNumber': '1'}

                # creating a name for the port from the NetworkAdapter path (which will be a key assigend with value of its AssociatedNetworkAddresses)
                custom_name_elements = z.split("NetworkAdapters")[-1].split("/")
                # removing empty elements from the list
                custom_name_elements = [x for x in custom_name_elements if x]
                custom_name = '-'.join(custom_name_elements)
                # >>> custom_name
                # 'mainboardPCIeCard5-NetworkPorts-1'
                # >>>                
                if response.status_code != 200:
                    print("\n- FAIL, get command failed, error is: %s" % data)
                    sys.exit()
                else:
                    # creating a dict with key from NetworkAdapter path and value of its AssociatedNetworkAddresses
                    dict_server_port_mac[custom_name] = data['AssociatedNetworkAddresses']
        pprint(dict_server_port_mac)
        # {'mainboardLOM-NetworkPorts-1': ['F0:63:F9:17:36:78'],
        # 'mainboardLOM-NetworkPorts-2': ['F0:63:F9:17:36:79'],
        # 'mainboardLOM-NetworkPorts-3': ['F0:63:F9:17:36:7A'],
        # 'mainboardLOM-NetworkPorts-4': ['F0:63:F9:17:36:7B'],
        # 'mainboardPCIeCard1-NetworkPorts-1': ['AC:75:1D:AD:B5:9D'],
        # 'mainboardPCIeCard1-NetworkPorts-2': ['AC:75:1D:AD:B5:9E'],
        # 'mainboardPCIeCard4-NetworkPorts-1': ['AC:75:1D:AD:B9:0E'],
        # 'mainboardPCIeCard4-NetworkPorts-2': ['AC:75:1D:AD:B9:0F'],
        # 'mainboardPCIeCard5-NetworkPorts-1': ['AC:75:1D:AD:B7:FE'],
        # 'mainboardPCIeCard5-NetworkPorts-2': ['AC:75:1D:AD:B7:FF']}                            
        return dict_server_port_mac

    get_huawei_server_nic_mac(ibmc_ip = '192.168.201.14',ibmc_username = 'Administrator',ibmc_password = 'Orange123#')

if __name__ == "__main__":
    main()    
