import json
import ipaddress
from jinja2 import Template


blueprint_id = ""

def search_json(data, keys_to_find, path=""):
    results = []

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}/{key}" if path else key
            if key in keys_to_find:
                results.append({
                    "path": current_path,
                    "attributes": value.get("attributes", []),
                    "children": value.get("children", [])                    
                })
            results.extend(search_json(value, keys_to_find, current_path))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            current_path = f"{path}[{index}]"
            results.extend(search_json(item, keys_to_find, current_path))

    return results

def search_key(json_data, key):
    """
    Search for a key in the JSON data and return a list of all values associated with that key.
    
    :param json_data: The JSON data to search.
    :param key: The key to search for.
    :return: A list of values associated with the key.
    """
    results = []

    def search_recursive(data):
        # Check if the current data is a dictionary
        if isinstance(data, dict):
            for k, v in data.items():
                # If the key matches, add its value to the results
                if k == key:
                    results.append(v)
                # Recurse into the value
                search_recursive(v)
        # Check if the current data is a list
        elif isinstance(data, list):
            for item in data:
                # Recurse into each item in the list
                search_recursive(item)

    # Start the recursive search
    search_recursive(json_data)
    return results

def search_key_with_criteria(json_data, main_key, criteria_keys):
    """
    Search for a key in the JSON data and return a list of values associated with that key,
    only if other specified keys are also present at the same level.
    
    :param json_data: The JSON data to search.
    :param main_key: The main key to search for.
    :param criteria_keys: A list of additional keys that must also be present at the same level.
    :return: A list of values associated with the main key.
    """
    results = []

    def search_recursive(data):
        # Check if the current data is a dictionary
        if isinstance(data, dict):
            # Check if the main key and all criteria keys are present
            if main_key in data and all(k in data for k in criteria_keys):
                results.append(data[main_key])
            for v in data.values():
                # Recurse into the value
                search_recursive(v)
        # Check if the current data is a list
        elif isinstance(data, list):
            for item in data:
                # Recurse into each item in the list
                search_recursive(item)

    # Start the recursive search
    search_recursive(json_data)
    return results

def search_key_with_path_and_criteria(json_data, path_key, main_key, criteria_keys):
    """
    Search for a main key in the JSON data and return a list of values associated with that key,
    only if other specified keys are also present at the same level and a specific key is present in the path.
    
    :param json_data: The JSON data to search.
    :param path_key: The key that must be present in the path.
    :param main_key: The main key to search for.
    :param criteria_keys: A list of additional keys that must also be present at the same level.
    :return: A list of values associated with the main key.
    """
    results = []

    def search_recursive(data, path_found=False):
        # Check if the current data is a dictionary
        if isinstance(data, dict):
            # If the path key is found, mark path_found as True
            if path_key in data:
                path_found = True
            # Check if the main key and all criteria keys are present
            if path_found and main_key in data and all(k in data for k in criteria_keys):
                results.append(data[main_key])
            for v in data.values():
                # Recurse into the value with the updated path_found status
                search_recursive(v, path_found)
        # Check if the current data is a list
        elif isinstance(data, list):
            for item in data:
                # Recurse into each item in the list with the updated path_found status
                search_recursive(item, path_found)

    # Start the recursive search
    search_recursive(json_data)
    return results

def search_key_and_return_structure(json_data, key):
    """
    Search for a key in the JSON data and return the entire JSON structure under that key.
    If the key exists multiple times, add each structure to a list.
    
    :param json_data: The JSON data to search.
    :param key: The key to search for.
    :return: A list of JSON structures found under the specified key.
    """
    results = []

    def search_recursive(data):
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key:
                    results.append({k: v})
                search_recursive(v)
        elif isinstance(data, list):
            for item in data:
                search_recursive(item)

    search_recursive(json_data)
    return results

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

def generate_apstra_datacenter_routing_zone_config(vrf_list, blueprint_id):
    # Define the Jinja2 template as a string
    template_str = """
    {% for vrf in vrf_list %}
    resource "apstra_datacenter_routing_zone" "{{ vrf.apstra_vrf }}_rz" {
      name              = "{{ vrf.apstra_vrf }}"
      blueprint_id      = "{{ blueprint_id }}"
      virtual_network_ids = [apstra_virtual_network.{{ vrf.apstra_vrf }}.id]
    }
    {% endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        blueprint_id=blueprint_id,
        vrf_list=vrf_list
    )

    return output

def main():
    # Load the JSON data from a file
    file_path = '/Users/ajarvis/Downloads/APIC.json'
    json_data = read_json_file(file_path)
    if json_data:
        print("JSON data successfully read.")
    
    # Specify the keys to search for
    # keys_to_find = ["fvTenant", "fvBD", "fvAP", "fvAEPG", "fvCtx"]
    keys_to_find = ["fvTenant"]
    # Search the JSON data
    results = search_json(json_data, keys_to_find) 

    """
    This pulls all tennant names
    """

    keys_to_find = ["fvTenant"]
    # Search the JSON data
    tennant_results = search_json(json_data, keys_to_find) 

    tennant_list=[]
    vrf_list=[]
    vritual_network_list=[]
    # Print the results
    for tennant in tennant_results:
        # print(f"Path: {result['path']}")
        # print(f"Children: {json.dumps(result, indent=2)}")
        # print(json.dumps(result))
        tennant_list.append(tennant["attributes"]["name"])

        keys_to_find = ["fvCtx"]
        tennant_vrf = search_json(tennant, keys_to_find) 
        for vrf in tennant_vrf:
            vrf_tmp = {}
            vrf_tmp["aci_vrf"] = vrf["attributes"]["name"]
            vrf_tmp["apstra_vrf"] = tennant["attributes"]["name"] + "_" + vrf["attributes"]["name"]
            vrf_list.append(vrf_tmp)



        keys_to_find = ["fvBD"]
        tennant_vrf = search_json(tennant, keys_to_find) 
        for vrf in tennant_vrf:
            vn_temp_data = {}
            vn_temp_data["children"]=[]
            vn_temp_data["vn_name"] = vrf["attributes"]["name"]
            vn_temp_data["vn_mac"] = vrf["attributes"]["mac"]
            vn_temp_data["vn_unicastRoute"] = vrf["attributes"]["unicastRoute"]

            for child_vn in vrf["children"]:
                vn_child_temp_data = {}
                if "fvRsCtx" in child_vn:
                    vn_child_temp_data["vn_vrf_bind"] = child_vn["fvRsCtx"]["attributes"]["tnFvCtxName"]
                if vrf["attributes"]["unicastRoute"] == "yes":
                    if "fvSubnet" in child_vn:
                        vn_child_temp_data["aci_ip"] = child_vn["fvSubnet"]["attributes"]["ip"]
                        ip, network = get_ip_and_network(child_vn["fvSubnet"]["attributes"]["ip"])
                        vn_child_temp_data["apstra_ip"] = ip
                        vn_child_temp_data["apstra_network"] = network

                if vn_child_temp_data:
                    vn_temp_data["children"].append(dict(vn_child_temp_data))

                # print(vn_child_temp_data)
            
            vritual_network_list.append(vn_temp_data)

    print("\n\n\nVRF List\n")
    print(json.dumps(vrf_list))
    print("\n\n\nVN List\n")
    print(json.dumps(vritual_network_list))
    

    # print(json.dumps(results))


    # egg=search_key_and_return_structure(results, "fvTenant")
    # print(egg)

    print("\n\n\nTF Config\n")
    config = generate_apstra_datacenter_routing_zone_config(vrf_list, blueprint_id)
    print(config)


if __name__ == "__main__":
    main()

