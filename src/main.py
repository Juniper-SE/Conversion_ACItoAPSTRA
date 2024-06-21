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
    parser.add_argument('--port_file', '-p', type=str, required=True, help='Path to the ACI to Apstra fabric port mapping CSV file')
    parser.add_argument('--blueprint_name', '-b', type=str, required=True, help='Blueprint ID needed for Terraform Config file.')
    parser.add_argument('--new', '-n', action='store_true', help='Create a new blueprint on Apstra based on the current ACI topology / switches.')
    parser.add_argument('--output', '-o', type=str, required=True, help='Output directory for Terraform Config file.')
    parser.add_argument('--test', '-t', action='store_true', help='Run the script in test mode')

    args = parser.parse_args()
    logger.info("Script execution started with arguments: %s", args)

    if args.test:
        logger.info("Running in test mode.")
    else:
        logger.info("Running in normal mode.")

    if args.new:
        try:
            fnvread_file_path = input("input full file path of APIC \"fnvread\" command output in .csv format: ")
            apic_data = data_load(args.file)
            aci_bindings_with_ports = port_search(apic_data)
            vrf_list, virtual_network_list = tenant_search(apic_data)
            generic_system_single, generic_system_pc, generic_system_esi, vn_to_vlan, list_of_node_ids = search.get_generic_systems_nb(aci_bindings_with_ports, args.port_file)
            logical_devices, aci_spine_nodes, list_of_single_leaf, list_of_leaf_pairs, tep_pool = search.aci_fabric_discover(apic_data,fnvread_file_path)
            tf_path=utils.create_directory(args.output)
            tf_path_part1=utils.create_directory_part1(args.output)
            tf_path_part2 = utils.create_directory_part2(args.output)
            tf_path_part3 = utils.create_directory_part3(args.output)
            
            resources_config = jinja.generate_apstra_resources_config(tep_pool)
            utils.create_file(tf_path_part1, "resources.tf", content=resources_config)
            logical_devices_config = jinja.generate_apstra_logical_devices_config(logical_devices)
            utils.create_file(tf_path_part1, "logical_devices.tf", content=logical_devices_config)
            interface_maps_config = jinja.generate_apstra_interface_maps_config(logical_devices, aci_spine_nodes, list_of_single_leaf, list_of_leaf_pairs)
            utils.create_file(tf_path_part1, "interface_maps.tf", content=interface_maps_config)
            rack_types_config = jinja.generate_apstra_rack_types_config(list_of_single_leaf, list_of_leaf_pairs)
            utils.create_file(tf_path_part1, "rack_types.tf", content=rack_types_config)
            template_config = jinja.generate_apstra_template_config(aci_spine_nodes, list_of_single_leaf, list_of_leaf_pairs)
            utils.create_file(tf_path_part1, "template.tf", content=template_config)
            blueprint_config = jinja.generate_apstra_blueprint_config(args.blueprint_name)
            utils.create_file(tf_path_part1, "blueprint.tf", content=blueprint_config)
            resources_assign_config = jinja.generate_apstra_resources_assign_config()
            utils.create_file(tf_path_part1, "resources_assign.tf", content=resources_assign_config)
            interface_maps_assign_config = jinja.generate_apstra_interface_maps_assign_config(logical_devices, aci_spine_nodes, list_of_single_leaf, list_of_leaf_pairs)
            utils.create_file(tf_path_part1, "interface_maps_assign.tf", content=interface_maps_assign_config)

            vrf_config = jinja.generate_apstra_datacenter_routing_zone_nb_config(vrf_list, args.blueprint_name)
            utils.create_file(tf_path_part3, "vrf.tf", content=vrf_config)
            vn_config = jinja.generate_apstra_datacenter_virtual_network_nb_config(virtual_network_list, vn_to_vlan)
            utils.create_file(tf_path_part3, "vn.tf", content=vn_config)
            ct_config = jinja.generate_apstra_datacenter_ct_nb_config(vn_to_vlan)
            utils.create_file(tf_path_part3, "ct.tf", content=ct_config)

            generic_system_config = jinja.generate_apstra_datacenter_generic_system_nb_config(generic_system_single,generic_system_pc,generic_system_esi,list_of_single_leaf,list_of_leaf_pairs, args.blueprint_name)
            utils.create_file(tf_path_part2, "generic_systems.tf", content=generic_system_config)

            ct_assign_config = jinja.generate_apstra_datacenter_ct_assign_nb_config(vn_to_vlan,args.blueprint_name)
            utils.create_file(tf_path_part3, "ct_assign.tf", content=ct_assign_config)

            logger.info("Script execution finished successfully.")
        except Exception as e:
            logger.error(f"An error occurred during script execution: {e}", stack_info=True, exc_info=True)
    else:
        try:
            apic_data = data_load(args.file)
            aci_bindings_with_ports = port_search(apic_data)
            vrf_list, virtual_network_list = tenant_search(apic_data)
            generic_system_single, generic_system_pc, generic_system_esi, vn_to_vlan, list_of_node_ids = search.get_generic_systems(aci_bindings_with_ports, args.port_file)
            tf_path=utils.create_directory(args.output)
            vrf_config = jinja.generate_apstra_datacenter_routing_zone_config(vrf_list, args.blueprint_name)
            utils.create_file(tf_path, "vrf.tf", content=vrf_config)
            vn_config = jinja.generate_apstra_datacenter_virtual_network_config(virtual_network_list, vn_to_vlan)
            utils.create_file(tf_path, "vn.tf", content=vn_config)
            generic_system_config = jinja.generate_apstra_datacenter_generic_system_config(generic_system_single, generic_system_pc, generic_system_esi, list_of_node_ids)
            utils.create_file(tf_path, "generic_systems.tf", content=generic_system_config)
            ct_config = jinja.generate_apstra_datacenter_ct_config(vn_to_vlan)
            utils.create_file(tf_path, "ct.tf", content=ct_config)
            ct_assign_config = jinja.generate_apstra_datacenter_ct_assign_config(vn_to_vlan)
            utils.create_file(tf_path, "ct_assign.tf", content=ct_assign_config)

            logger.info("Script execution finished successfully.")
        except Exception as e:
            logger.error(f"An error occurred during script execution: {e}", stack_info=True, exc_info=True)

if __name__ == "__main__":
    main()
