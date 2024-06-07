import search
import parse
import jinja
import utils
import json
import logging
import argparse

# Set up logging configuration
logging.basicConfig(
    filename='app.log',  # Log file name
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

logger = logging.getLogger(__name__)

def data_load(file_path):
    """Load data from the specified JSON file."""
    try:
        logger.info("Loading data from JSON file.")
        data = utils.read_json_file(file_path)
        logger.info("Data loaded successfully.")
        return data
    except Exception as e:
        logger.error(f"Failed to load data: {e}", stack_info=True, exc_info=True)
        raise

def tenant_search(apic_data):
    """Search for tenants in the APIC data and return VRF and VN lists."""
    try:
        logger.info("Starting tenant search.")
        keys_to_find = ["fvTenant"]
        data_results = search.search_json(apic_data, keys_to_find)
        logger.info("Tenant search results obtained.")
        
        vrf_list, virtual_network_list = search.tennant_search(data_results)
        
        logger.debug(f"VRF List: {json.dumps(vrf_list, indent=2)}")
        logger.debug(f"Virtual Network List: {json.dumps(virtual_network_list, indent=2)}")
        
        return vrf_list, virtual_network_list
    except Exception as e:
        logger.error(f"Tenant search failed: {e}", stack_info=True, exc_info=True)
        raise

def port_search(apic_data):
    """Search for tenants in the APIC data and return VRF and VN lists."""
    try:
        logger.info("Starting port search.")
        keys_to_find = ["fvTenant"]
        data_results = search.search_json(apic_data, keys_to_find)
        logger.info("Port search results obtained.")
        
        aci_bindings=search.get_vrf_bd_bindings(data_results)
        logger.debug(f"aci_bindings: {json.dumps(aci_bindings, indent=2)}")

        nodes_with_interface_profiles=search.get_nodes_with_interface_profiles(apic_data)
        logger.debug(f"nodes_with_interface_profiles: {json.dumps(aci_bindings, indent=2)}")

        interface_profile_tree=search.get_interface_profile_tree(apic_data)
        logger.debug(f"interface_profile_tree: {json.dumps(aci_bindings, indent=2)}")

        aci_bindings_with_ports=search.port_binding(aci_bindings, nodes_with_interface_profiles, interface_profile_tree, apic_data)    
        logger.debug(f"aci_bindings: {json.dumps(aci_bindings, indent=2)}")
        
        return aci_bindings_with_ports
    except Exception as e:
        logger.error(f"Port search failed: {e}", stack_info=True, exc_info=True)
        raise

def main():
    """Main function to load data and perform tenant search."""
    parser = argparse.ArgumentParser(description="ACI to Apstra Converter")
    parser.add_argument('--file', '-f', type=str, required=True, help='Path to the APIC configuration JSON file')
    parser.add_argument('--test', '-t', action='store_true', help='Run the script in test mode')
    

    args = parser.parse_args()
    
    logger.info("Script execution started with arguments: %s", args)

    if args.test:
        logger.info("Running in test mode.")
    else:
        logger.info("Running in normal mode.")
    
    try:
        apic_data = data_load(args.file)
        vrf_list, virtual_network_list = tenant_search(apic_data)
        # config = jinja.generate_apstra_datacenter_routing_zone_config(vrf_list)

        aci_bindings_with_ports=port_search(apic_data)

        logger.info("Script execution finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred during script execution: {e}", stack_info=True, exc_info=True)

if __name__ == "__main__":
    main()
