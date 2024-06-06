import json
import ipaddress
import os

def get_ip_and_network(cidr):
    try:
        # Parse the IP network from the CIDR notation
        network = ipaddress.IPv4Network(cidr, strict=False)
        # Get the IP address part
        ip_address = str(network.network_address + (1 << (32 - network.prefixlen)) - 1)
        # Get the network address with subnet mask
        network_address = str(network.network_address)
        subnet_mask = str(network.netmask)
        # Create the network address with subnet
        network_address_with_subnet = f"{network_address}/{network.prefixlen}"
        return ip_address, network_address_with_subnet
    
    except ValueError as e:
        return str(e)
    

def write_json_to_file(data, file_path):
    """
    Writes a Python list or dictionary to a file in JSON format.
    
    Parameters:
    data (list or dict): The data to be written to the file.
    file_path (str): The path to the file where the data should be written.
    
    Raises:
    TypeError: If the data is not a list or dictionary.
    Exception: For any other exceptions that may occur.
    """
    if not isinstance(data, (list, dict)):
        raise TypeError("Data must be a list or dictionary.")
    
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully written to {file_path}.")
    except TypeError as e:
        print(f"Error: {e}")
    except PermissionError:
        print(f"Error: Permission denied when accessing the file at {file_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def read_json_file(file_path):
    """
    Reads a JSON file from the specified file path and returns the data.
    
    Parameters:
    file_path (str): The path to the JSON file to be read.
    
    Returns:
    dict: The data from the JSON file if read successfully.
    
    Raises:
    FileNotFoundError: If the file is not found.
    PermissionError: If the file cannot be accessed due to permission issues.
    json.JSONDecodeError: If the file contains invalid JSON.
    Exception: For any other exceptions that may occur.
    """
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return json_data
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except PermissionError:
        print(f"Error: Permission denied when accessing the file at {file_path}.")
    except json.JSONDecodeError:
        print(f"Error: The file at {file_path} contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def get_data_test_file(filename):
    """Load a file from the data directory."""
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the data file
    data_file_path = os.path.join(script_dir, '..', 'data', filename)
    
    # Read the contents of the file
    return data_file_path