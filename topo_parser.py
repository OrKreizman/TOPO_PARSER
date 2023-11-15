
import argparse
import pickle
import multiprocessing

import re
from tqdm import tqdm
import threading
import time
from itertools import islice


class Device:
    """
    Represent a device
    """
    Host = 1
    Switch = 2

    @staticmethod
    def _is_host(fifth_line):
        """
        Check if data chunk describe a Host
        :param fifth_line: the fifth line of the chunk data
        :return:
        """
        return fifth_line.startswith("Ca")

    @staticmethod
    def _is_switch(fifth_line):
        """
        Check if data chunk describe a Switch
        :param fifth_line:
        :return:
        """
        return fifth_line.startswith("Switch")

    def __get_connections(self, host_chunk_data):
        for i in range(5, len(host_chunk_data)):
            connection = Connection(host_chunk_data[i])
            self.connections[connection.destination_name]=connection

    def __init__(self, host_chunk_data):
        self.name = host_chunk_data[4].split()[2][1:-1]
        self.device_type = self.Host if self._is_host(host_chunk_data[4]) else self.Switch
        self.sysimgguid = host_chunk_data[2][len("sysimgguid") + 1:]
        self.connections = dict()
        self.__get_connections(host_chunk_data=host_chunk_data)


class Connection:

    def __init__(self, connection_data):
        optional_port_id_pattern = '(\([\w]+\))?'
        port_number_pattern = '(\[\d+\])'
        port_pattern = port_number_pattern + optional_port_id_pattern
        destination_name_pattern = '"(.*?)"'
        pattern = r'{}\s+{}{}'.format(port_pattern,destination_name_pattern,port_pattern)
        match = re.match(pattern, connection_data)
        if match:
            self.port1,self.port_id1,self.destination_name, self.port2, self.port_id2 = match.groups()
        else:
            raise ValueError(f"Unexpected line structure for connection")


class InfinibandTopologyParser:

    def __init__(self,file_path):
        self.file_path = file_path
        self.devices = dict()
        # self.currently_parsing = threading.Event()

    def parse(self):
        # self.currently_parsing.clear()
        for device_data in self.read_device_data():
            device_obj = Device(device_data)
            self.devices[device_obj.name]=device_obj
        # self.currently_parsing.set()

    def read_device_data(self):
        current_device_data = []
        with open(self.file_path, 'r') as file:
            file = islice(file, 5, None)
            for line in tqdm(file):
                if line.strip() == '':
                    if current_device_data:
                        yield current_device_data
                        current_device_data = list()
                else:
                    current_device_data.append(line)
        if current_device_data:
            yield current_device_data


    def print_devices(self):
        # self.currently_parsing.wait()
        visited_devices = set()
        to_visit = [iter(self.devices).__next__()]
        output_file = open(f'output.txt', 'w')
        output_file.write(f'### printing all connections in the network\n### From file: {self.file_path}')
        while len(visited_devices)!=len(self.devices):
            device = self.devices[to_visit.pop(0)]
            visited_devices.add(device.name)
        # for device in self.devices.values():
            device_information = 'Host:\n' if device.device_type==Device.Host else 'Switch:\n'
            device_information += f'sysimgguid={device.sysimgguid}\n'
            for connection in device.connections.values():
                if connection.destination_name not in visited_devices: to_visit.append(connection.destination_name)
                if connection.port1:
                    device_information += f'Connected to: name={connection.destination_name}, Port_id:={connection.port1}\n'
            output_file.write(device_information)



if __name__ == '__main__':
    # file_path = ".\TopologyFiles\large_topo_file"
    parser = argparse.ArgumentParser(description='Infiniband Topology Parser')
    parser.add_argument('-f', '--file', help='Specify the topology file') # , required=True
    parser.add_argument('-p', '--print-topology', action='store_true', help='Print parsed topology')
    args = parser.parse_args()

    if args.file:
        topo_parser = InfinibandTopologyParser(args.file)
        parse_thread = threading.Thread(target=topo_parser.parse)
        parse_thread.start()
        parse_thread.join()
        if not args.print_topology:
            with open('topo_objects.pkl', 'wb') as file:
                pickle.dump(topo_parser, file)
    if args.print_topology:
        if not args.file:
            with open('topo_objects.pkl', 'rb') as file:
                topo_parser = pickle.load(file)
        print_thread = threading.Thread(target=topo_parser.print_devices)
        print_thread.start()






