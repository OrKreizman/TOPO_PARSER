import unittest
from topo_parser import *

class Test_Connection(unittest.TestCase):
    """
    Test the class Connection
    """
    connections_lines = ['[24]	"H-ec0d9a03007d7d0b"[1](ec0d9a03007d7d0b) 		# "r-dcs96 HCA-2" lid 28 4xEDR',
                         '[3]	"S-0002c903007b78b0"[1]		# "MF0;r-ufm-sw226:SX6036/U1" lid 19 4xFDR',
                         '[1](ec0d9a03007d7d0b) 	"S-b8599f0300fc6de4"[24]		# lid 28 lmc 0 "MF0;r-ufm-sw95:MQM8700/U1" lid 13 4xEDR']
    expected_data = [['[24]',None,"H-ec0d9a03007d7d0b",'[1]','(ec0d9a03007d7d0b)'],
                     ['[3]',None,"S-0002c903007b78b0",'[1]',None],
                     ['[1]','(ec0d9a03007d7d0b)',"S-b8599f0300fc6de4",'[24]',None]]

    def test_connection_creation(self):
        """
        Test that the connection constuctor saves the field as expected
        """
        for line,expected in zip(self.connections_lines,self.expected_data):
            line_connection = Connection(line)
            self.assertEqual(line_connection.port1, expected[0])
            self.assertEqual(line_connection.port_id1, expected[1])
            self.assertEqual(line_connection.destination_name, expected[2])
            self.assertEqual(line_connection.port2, expected[3])
            self.assertEqual(line_connection.port_id2, expected[4])

class Test_Device(unittest.TestCase):
    """
    Test the class Device
    """
    def test_is_host(self):
        """
        Test the function is_host returns true only in case of a host.
        """
        self.assertEqual(Device._is_host('Ca	1 "H-ec0d9a03007d7d0b"		# "r-dcs96 HCA-2"'),True)
        self.assertEqual(Device._is_host('Switch	41 "S-b8599f0300fc6de4"		# "MF0;r-ufm-sw95:MQM8700/U1" enhanced port 0 lid 13 lmc 0'),False)

    def test_is_switch(self):
        """
        Test the function is_switch returns true only in case of a switch.
        """
        self.assertEqual(Device._is_switch('Ca	1 "H-ec0d9a03007d7d0b"		# "r-dcs96 HCA-2"'),False)
        self.assertEqual(Device._is_switch('Switch	41 "S-b8599f0300fc6de4"		# "MF0;r-ufm-sw95:MQM8700/U1" enhanced port 0 lid 13 lmc 0'),True)

    def test_constructor(self):
        """
        Pay attention - to assert abject this function uses Device.__eq__()
        :return:
        """
        device_chunk_data = [
        'vendid=0x2c9',
        'devid=0xd2f0',
        'sysimgguid=0xb8599f0300fc6de4',
        'switchguid=0xb8599f0300fc6de4(b8599f0300fc6de4)',
        'Switch 41 "S-b8599f0300fc6de4" # "MF0;r-ufm-sw95:MQM8700/U1" enhanced port 0 lid 13 lmc 0',
        '[3] "S-0002c903007b78b0"[1] # "MF0;r-ufm-sw226:SX6036/U1" lid 19 4xFDR',
        '[23] "H-ec0d9a03007d7d0a"[1](ec0d9a03007d7d0a) # "r-dcs96 HCA-1" lid 9 4xEDR',
        '[24] "H-ec0d9a03007d7d0b"[1](ec0d9a03007d7d0b) # "r-dcs96 HCA-2" lid 28 4xEDR',
        '[41] "H-b8599f0300fc6dec"[1](b8599f0300fc6dec) # "Mellanox Technologies Aggregation Node" lid 14 4xHDR'
        ]

        device = Device(device_chunk_data)
        self.assertEqual(device.device_type, 'Switch')
        self.assertEqual(device.name,'S-b8599f0300fc6de4')
        self.assertEqual(device.sysimgguid,'0xb8599f0300fc6de4')
        for i in range (5,len(device_chunk_data)):
            self.assertEqual(device.connections[i-5],Connection(device_chunk_data[i]))

class Test_InfinibandTopologyParser(unittest.TestCase):
    """
    Test the class InfinibandTopologyParser.
    """

    file_path = ".\TopologyFiles\large_topo_file"

    def test_constructor(self):
        """
        Test the class constructor
        (storing fields as excpected)
        """
        from datetime import datetime, timedelta
        parsing_started_time = datetime.now()
        parser = InfinibandTopologyParser(self.file_path)
        self.assertEqual(parser.file_path,self.file_path)
        self.assertEqual(parser.file_name,os.path.basename(self.file_path))
        parsing_ending_time = datetime.now()
        # Assert that parsing_time is within [parsing_started_time,parsing_ending_time]
        self.assertLessEqual(parser.parsing_time, parsing_ending_time)
        self.assertLessEqual(parsing_started_time,parser.parsing_time)


if __name__ == '__main__':
    unittest.main()
