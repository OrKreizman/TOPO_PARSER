# Infiniband Topology Parser

This Python utility, named `topo_parser`, is designed to parse Infiniband network topology files, discover network connections, and print them. 
The program can be run from the command line using Python as follows:

```bash
python topo_parser.py <options>
```

## Usage

### Print Help
```bash
–h
```
Prints usage information and exits.

### Parse Topology File
```bash
–f topofile
```
Parses the specified Infiniband network topology file (`topofile.topo`). 
This option extracts and stores the network connections for further analysis.

### Print Parsed Topology
```bash
–p
```
Prints the parsed Infiniband network topology. 


## Infiniband Network Topology File Explanation



## Important Notes

- The utility is designed to report parsing progress to the user, allowing for the printing of the existing topology while still processing new topology data(using seperate process for printing).

## Example Usage

```bash
# Print usage information
python topo_parser.py –h

# Parse a topology file
python topo_parser.py –f topofile

# Print the parsed topology after the program is running
–p
```

