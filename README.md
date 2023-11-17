
# Topology Parser

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
Parses the specified Infiniband network topology file (`topofile`). 
This option extracts and stores the network connections for further analysis.
To ensure successful parsing, place the topofile in the current directory or specify the full path to the file.

### Print Parsed Topology
```bash
–p
```
Prints the parsed Infiniband network topology. 

### Quitting the Program
```bash
–q
```
Quit the program. 

...

## Important Notes

- The utility is designed to report parsing progress to the user, allowing for the printing of the existing topology while still parsing new topology data (using a separate process for printing).

## Example Usage

```bash
# Print usage information
python topo_parser.py –h

# Parse a topology file
python topo_parser.py –f topofile

# Print the parsed topology after the program is running
–p

# Quit the program
–q
```

## Installing Required Packages

To install the required packages for running `topo_parser`, use the following command:

```bash
pip install -r requirements.txt
```

This command will install the necessary dependencies specified in the `requirements.txt` file, ensuring the utility runs successfully.

---
