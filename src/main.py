import search
import parse
import jinja
import utils
import json
import logging
import os

# Set up logging configuration
logging.basicConfig(
    filename='app.log',  # Log file name
    level=logging.DEBUG,  # Log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format
)

logger = logging.getLogger(__name__)

ACI_JSON_DATA = "/Users/ajarvis/Downloads/APIC.json"

def data_load():
    """Load data from the specified JSON file."""
    try:
        logger.info("Loading data from JSON file.")
        data_file_path = utils.get_data_test_file("APIC.json")
        data = utils.read_json_file(data_file_path)
        logger.info("Data loaded successfully.")
        return data
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
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
        logger.error(f"Tenant search failed: {e}")
        raise

def main():
    """Main function to load data and perform tenant search."""
    logger.info("Script execution started.")
    
    try:
        apic_data = data_load()
        vrf_list, virtual_network_list = tenant_search(apic_data)
        # config = jinja.generate_apstra_datacenter_routing_zone_config(vrf_list)
        logger.info("Script execution finished successfully.")
    except Exception as e:
        logger.error(f"An error occurred during script execution: {e}")

if __name__ == "__main__":
    main()
