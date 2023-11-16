# Infiniband Topology Parser

This Python utility, named `topo_parser`, is designed to parse Infiniband network topology files, discover network connections, and print the parsed topology. 
The program can be run from the command line with the following options:

## Usage

### Print Help
```bash
topo_parser –h
```
Prints usage information and exits.

### Parse Topology File
```bash
topo_parser –f topofile.topo
```
Parses the specified Infiniband network topology file (`topofile.topo`). 
This option extracts and stores the network connections for further analysis.

### Print Parsed Topology
```bash
topo_parser –p
```
Prints the parsed Infiniband network topology. 


## Infiniband Network Topology File Explanation



## Important Notes

- The utility is designed to report parsing progress to the user, allowing for the printing of the existing topology while still processing new topology data(using seperate process for printing).

## Example Usage

```bash
# Print usage information
topo_parser –h

# Parse a topology file
topo_parser –f topofile

# Print the parsed topology
topo_parser –p
```

