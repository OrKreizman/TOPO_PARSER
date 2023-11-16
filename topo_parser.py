import argparse
import multiprocessing
import os
import pickle
import re
from datetime import datetime
from tqdm import tqdm
from itertools import islice


class Device:
    """
    A Class Represents a device
    """
    Host = 'Host'
    Switch = 'Switch'

    def __init__(self, host_chunk_data):
        """
        Build Device obj.
        :param host_chunk_data: Information lines about the device from the topology file
        """
        self.name = host_chunk_data[4].split()[2][1:-1]
        self.device_type = self.Host if self._is_host(host_chunk_data[4]) else self.Switch
        self.sysimgguid = host_chunk_data[2][len("sysimgguid") + 1:]
        self.connections = list()  # list to enable duplicates as required
        self.__get_connections(host_chunk_data=host_chunk_data)

    @staticmethod
    def _is_host(fifth_line):
        """
        Check if data chunk describe a Host
        :param fifth_line: the fifth line of the chunk data
        :return: True if Host False otherwise
        """
        return fifth_line.startswith("Ca")

    @staticmethod
    def _is_switch(fifth_line):
        """
        Check if data chunk describe a Switch
        :param fifth_line:
        :return: True if Switch False otherwise
        """
        return fifth_line.startswith("Switch")

    def __get_connections(self, host_chunk_data):
        """
        Get all device connections from the data chunk and insert as Connections object to the field self.connections
        :param host_chunk_data: Information lines about the device from the topology file
        :return: None
        """
        for i in range(5, len(host_chunk_data)):
            connection = Connection(host_chunk_data[i])
            self.connections.append(connection)



    def __str__(self):
        device_information = f'{self.device_type}:\n'
        device_information += f'sysimgguid={self.sysimgguid}\n'
        for connection in self.connections:
            device_information += str(connection)
        return device_information + '\n'


class Connection:
    """
    Class represent a device's connection
    """

    def __init__(self, connection_data):
        """
        Build a Connection object
        :param connection_data: a line with structured data about the connection for specific device
        """
        optional_port_id_pattern = '(\([\w]+\))?'
        port_number_pattern = '(\[\d+\])'
        port_pattern = port_number_pattern + optional_port_id_pattern
        destination_name_pattern = '"(.*?)"'
        pattern = r'{}\s+{}{}'.format(port_pattern, destination_name_pattern, port_pattern)
        match = re.match(pattern, connection_data)
        if match:
            self.port1, self.port_id1, self.destination_name, self.port2, self.port_id2 = match.groups()
        else:
            raise ValueError(f"Unexpected line structure for connection")

    def __str__(self):
        return f'Connected to: {self.destination_name}, Ports:={self.port1}=>{self.port2}\n'


class InfinibandTopologyParser:
    """
    Represents an Infiniband Topology Parser object
    """
    OUTPUT_FILE_NAME = '{}_output.txt'
    OUTPUT_FILE_START_MESSAGE = "### Printing all connections in the network\n" \
                                "### From file: {}\n### Data was parsed at: {}\n\n"

    def __init__(self, file_path):
        """
        Build InfinibandTopologyParser object.
        :param file_path: file path for the topology file to parse
        """
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.devices = dict()
        self.parsing_time = datetime.now()

    def __file_chunk_generator(self):
        """
        Generator for reading the topology file chunk by chunk.
        chunk - the group of lines describes specific device in the file.
        :return:
        """
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

    def parse(self):
        """
        Parse the given Topology file into the parser devices dict.
        each device in the dict is of type Device(class)
        :return: None
        """
        for device_data in self.__file_chunk_generator():
            device_obj = Device(device_data)
            self.devices[device_obj.name] = device_obj

    def print_devices_connections(self):
        """
        Print all topology connections (for each device) into the output file
        :return: None
        """
        visited_devices = set()
        with open(self.OUTPUT_FILE_NAME.format(self.file_name), 'w') as output_file:
            output_file.write(self.OUTPUT_FILE_START_MESSAGE.format(self.file_path, self.parsing_time))
            for device in self.devices.values():
                visited_devices.add(device.name)
                output_file.write(str(device))
            print(f'Output printed to the file: {self.OUTPUT_FILE_NAME.format(self.file_name)}')  # Report to user

    def print_devices_connections_BFS(self):
        """
        Print all topology connections (for each device) into the output file
        devices printed order is: BFS
        :return: None
        """
        visited_devices = set()
        to_visit = [iter(self.devices).__next__()]  # mark devices as visited to prevent infinity loop
        with open(self.OUTPUT_FILE_NAME.format(self.file_name), 'w') as output_file:
            output_file.write(self.OUTPUT_FILE_START_MESSAGE.format(self.file_path, self.parsing_time))
            while len(visited_devices) != len(self.devices):
                device = self.devices[to_visit.pop(0)]
                if device.name in visited_devices: continue
                visited_devices.add(device.name)
                output_file.write(str(device))
                to_visit.extend(connect.destination_name for connect in device.connections if
                                connect.destination_name not in visited_devices)
            print(f'Output printed to the file: {self.OUTPUT_FILE_NAME.format(self.file_name)}')  # Report to user


def main():
    topo_parser = None

    def run_parsing(file_path):
        nonlocal topo_parser
        topo_parser = InfinibandTopologyParser(file_path)
        topo_parser.parse()
        if not args.print_topology:
            with open('topo_objects.pkl', 'wb') as file:
                pickle.dump(topo_parser, file)

    def run_printing(topo_parser):
        if not topo_parser:
            with open('topo_objects.pkl', 'rb') as file:
                topo_parser = pickle.load(file)
        print_process = multiprocessing.Process(target=topo_parser.print_devices_connections)
        print_process.start()

    parser = argparse.ArgumentParser(description='Infiniband Topology Parser')
    parser.add_argument('-f', '--file', help='Specify the topology file')  # , required=True
    parser.add_argument('-p', '--print-topology', action='store_true', help='Print parsed topology')
    parser.add_argument('-q', '--quit', action='store_true', help='Quit the program')
    args = parser.parse_args()

    while True:
        if args.file: run_parsing(args.file)
        elif args.print_topology: run_printing(topo_parser)
        elif args.quit: break
        else: parser.print_help()
        user_input = input("Enter command (-h for help): ").split()
        args = parser.parse_args(user_input)


if __name__ == '__main__':
    # file_path = ".\TopologyFiles\large_topo_file"
    main()
