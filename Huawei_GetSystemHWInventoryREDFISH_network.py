#! /usr/bin/env python3

# Gets network cards info from Huawei iBMC and dumps to local txt file, can be imported in another py script, inspired by
# https://github.com/dell/ibmc-Redfish-Scripting/blob/master/Redfish%20Python/GetSystemHWInventoryREDFISH.py
# Bogdan Adrian Burciu 23/09/2021 vers 1

# Import like:
    # import Huawei_GetSystemHWInventoryREDFISH_network
    # Huawei_GetSystemHWInventoryREDFISH_network.sys.argv=['192.168.201.14', 'Administrator', 'Orange123#']
    # Huawei_GetSystemHWInventoryREDFISH_network.main()

from datetime import datetime
from pprint import pprint
import argparse
import json
import os
import re
import requests
import sys
import time
import warnings
import logging

warnings.filterwarnings("ignore")


def main(argv=sys.argv[1:]):
    # expects ibmc_ip, ibmc_username, ibmc_password
    try:
        os.remove("hw_inventory.txt")
    except Exception as exc:
        logging.exception(exc)
        pass

    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    ibmc_ip = sys.argv[0]
    ibmc_username = sys.argv[1]
    ibmc_password = sys.argv[2]

    file = open("hw_inventory.txt", "a")
    d = datetime.now()
    current_date_time = "- Data collection timestamp: %s-%s-%s  %s:%s:%s\n" % (
        d.month, d.day, d.year, d.hour, d.minute, d.second)
    file.writelines(current_date_time)
    file.close()

    def check_supported_ibmc_version():
        # response = requests.get('https://%s/redfish/v1/Systems/' % ibmc_ip, verify=False,auth=(ibmc_username, ibmc_password))
        # print("\n\t\t >> vendor_output = Output of API call to /v1/Systems:", json.loads(response.text))
        # huawei_output = {'@odata.context': '/redfish/v1/$metadata#Systems',
        #                 '@odata.id': '/redfish/v1/Systems',
        #                 '@odata.type': '#ComputerSystemCollection.ComputerSystemCollection',
        #                 'Members': [{'@odata.id': '/redfish/v1/Systems/1'}],
        #                 'Members@odata.count': 1,
        #                 'Name': 'Computer System Collection'}
        # dell_output = {'@odata.context': '/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection',
        #                 '@odata.id': '/redfish/v1/Systems',
        #                 '@odata.type': '#ComputerSystemCollection.ComputerSystemCollection',
        #                 'Description': 'Collection of Computer Systems',
        #                 'Members': [{'@odata.id': '/redfish/v1/Systems/System.Embedded.1'}],
        #                 'Members@odata.count': 1,
        #                 'Name': 'Computer System Collection'}
        # hpe_output = {'@odata.context': '/redfish/v1/$metadata#Systems',
        #                 '@odata.id': '/redfish/v1/Systems/',
        #                 '@odata.type': '#ComputerSystemCollection.ComputerSystemCollection',
        #                 'Description': 'Computer Systems view',
        #                 'MemberType': 'ComputerSystem.1',
        #                 'Members': [{'@odata.id': '/redfish/v1/Systems/1/'}],
        #                 'Members@odata.count': 1,
        #                 'Name': 'Computer Systems',
        #                 'Total': 1,
        #                 'Type': 'Collection.1.0.0',
        #                 'links': {'Member': [{'href': '/redfish/v1/Systems/1/'}],
        #                           'self': {'href': '/redfish/v1/Systems/'}}}
        # print("System to be used in queries is", [x for x in json.loads(response.text)['Members'][0]['@odata.id'].split('/') if x][-1]
        response = requests.get('https://%s/redfish/v1/Systems/1' % ibmc_ip, verify=False,auth=(ibmc_username, ibmc_password))
        print("Supported version response code:",response.status_code)
        if response.status_code != 200:
            print("\n- WARNING, iBMC version installed does not support this feature using Redfish API")
            sys.exit()
        else:
            pass

    def get_network_information():
        file = open("hw_inventory.txt", "a")
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
        message = "\n---- Network Device Information ----"
        file.writelines(message)
        file.writelines("\n")
        print(message)
        network_uri_list = []
        for i in data['Members']:
            network = i['@odata.id']
            network_uri_list.append(network)
        if not network_uri_list:
            message = "\n- WARNING, no network information detected for system\n"
            file.writelines(message)
            file.writelines("\n")
            print(message)
        for i in network_uri_list:
            # network_uri_list = ['/redfish/v1/Chassis/1/NetworkAdapters/mainboardLOM'
            #                     '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard1'
            #                     '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard4'
            #                     '/redfish/v1/Chassis/1/NetworkAdapters/mainboardPCIeCard5']
            message = "\n- Network device details for %s -\n" % i.split("/")[-1]
            file.writelines(message)
            file.writelines("\n")
            print(message)
            #i = i.replace("Adapters", "Ports")
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
                if ii[0] == '@odata.id' or ii[0] == '@odata.context' or ii[0] == 'Metrics' \
                        or ii[0] == 'Links' or ii[0] == '@odata.type' \
                        or ii[0] == 'NetworkDeviceFunctions' or ii[0] == 'NetworkPorts':
                    pass
                elif ii[0] == "Controllers":
                    file.writelines(message)
                    print(message)
                    message = "FirmwarePackageVersion: %s" % ii[1][0]['FirmwarePackageVersion']
                    file.writelines(message)
                    file.writelines("\n")
                    print(message)
                else:
                    message = "%s: %s" % (ii[0], ii[1])
                    file.writelines(message)
                    file.writelines("\n")
                    print(message)
            # print('\n\t\t >> The port_uri_list is', port_uri_list)
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
                if response.status_code != 200:
                    print("\n- FAIL, get command failed, error is: %s" % data)
                    sys.exit()
                else:
                    message = "\n- Network port details for %s -\n" % z.split("/")[-1]
                    file.writelines(message)
                    file.writelines("\n")
                    print(message)
                    for ii in data.items():
                        if ii[0] == '@odata.id' or ii[0] == '@odata.context' or ii[0] == 'Metrics' or ii[
                            0] == 'Links' or \
                                ii[0] == '@odata.type':
                            pass
                        elif ii[0] == 'Oem':
                            try:
                                for iii in ii[1]['Huawei'].items():
                                    if iii[0] == '@odata.context' or iii[0] == '@odata.type':
                                        pass
                                    else:
                                        message = "%s: %s" % (iii[0], iii[1])
                                        file.writelines(message)
                                        file.writelines("\n")
                                        print(message)
                            except Exception as exc:
                                logging.exception(exc)
                                pass
                        else:
                            message = "%s: %s" % (ii[0], ii[1])
                            file.writelines(message)
                            file.writelines("\n")
                            print(message)
        file.close()

    check_supported_ibmc_version()
    get_network_information()


if __name__ == "__main__":
    main()
