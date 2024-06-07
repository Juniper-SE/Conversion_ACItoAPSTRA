import utils
import re

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


def tennant_search(data):
    tennant_list=[]
    vrf_list=[]
    vritual_network_list=[]
    # Print the results
    for tennant in data:

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
                        ip, network = utils.get_ip_and_network(child_vn["fvSubnet"]["attributes"]["ip"])
                        vn_child_temp_data["apstra_ip"] = ip
                        vn_child_temp_data["apstra_network"] = network

                if vn_child_temp_data:
                    vn_temp_data["children"].append(dict(vn_child_temp_data))
                    
            vritual_network_list.append(vn_temp_data)

    return vrf_list,vritual_network_list

def port_binding(aci_bindings, nodes_with_interface_profiles, interface_profile_tree, data):
    aci_bindings_with_ports={}
    for bd in aci_bindings.keys():
        aci_bindings_with_ports[bd]=[]
        for entry in aci_bindings[bd]:
            mode=entry['mode']
            path=entry['path']
            encap=entry['encap']
            if 'protpaths-' in path:
                x = re.findall("paths-.*/", path)
                y = re.findall("\\[.*\\]", path)
                path_nodes_part=str(x[0])
                path_nodes_part=path_nodes_part.removeprefix('paths-')
                path_nodes_part=path_nodes_part.removesuffix('/')
                leaf_pair=path_nodes_part.split('-')
                node1=int(leaf_pair[0])
                node2=int(leaf_pair[1])
                pg_part=str(y[0])
                pg_part=pg_part.removeprefix('[')
                pg=pg_part.removesuffix(']')
                node1_leaf_profiles = nodes_with_interface_profiles[node1]
                node2_leaf_profiles = nodes_with_interface_profiles[node2]
                node1_ports=[]
                node2_ports=[]
                for profile in node1_leaf_profiles:
                    node1_ports.extend(interface_profile_tree[profile][pg])
                for profile in node2_leaf_profiles:
                    node2_ports.extend(interface_profile_tree[profile][pg])
                bundle_mode, port_speed = get_lag_mode_speed(data,pg)
                bundle_mode = 'lacp_' + bundle_mode
                entry['bundle_type']="esi"
                entry['bundle_mode'] = bundle_mode
                entry['node1'] = node1
                entry['node1_ports'] = node1_ports
                entry['node2'] = node2
                entry['node2_ports'] = node2_ports
                entry['port_speed'] = port_speed
                entry['port_description'] = pg
                aci_bindings_with_ports[bd].append(entry.copy())
            elif 'paths-' in path:
                if 'pathep-[eth1/' in path:
                    x = re.findall("paths-.*/p", path)
                    y = re.findall("\\[.*\\]", path)
                    path_nodes_part=str(x[0])
                    path_nodes_part=path_nodes_part.removeprefix('paths-')
                    path_nodes_part=path_nodes_part.removesuffix('/p')
                    node1=int(path_nodes_part)
                    node2="null"
                    port=str(y[0])
                    port=port.removeprefix('[eth1/')
                    port=port.removesuffix(']')
                    node1_ports=[]
                    node1_ports.append(port)
                    node2_ports="null"
                    entry['bundle_type']="No LAG"
                    entry['bundle_mode'] = "null"
                    entry['node1'] = node1
                    entry['node1_ports'] = node1_ports
                    entry['node2'] = node2
                    entry['node2_ports'] = node2_ports
                    port_speed = get_int_speed(data,node1,port)
                    entry['port_speed'] = port_speed
                    entry['port_description']= "Leaf_id_" + str(node1) + "_port_eth1_" + str(port)
                    aci_bindings_with_ports[bd].append(entry.copy())
                elif 'pathep-[' in path:
                    x = re.findall("paths-.*/", path)
                    y = re.findall("\\[.*\\]", path)
                    path_nodes_part = str(x[0])
                    path_nodes_part = path_nodes_part.removeprefix('paths-')
                    path_nodes_part = path_nodes_part.removesuffix('/')
                    node1 = int(path_nodes_part)
                    node2 = "null"
                    pg_part = str(y[0])
                    pg_part = pg_part.removeprefix('[')
                    pg = pg_part.removesuffix(']')
                    node1_leaf_profiles = nodes_with_interface_profiles[node1]
                    node1_ports = []
                    node2_ports = "null"
                    for profile in node1_leaf_profiles:
                        node1_ports.extend(interface_profile_tree[profile][pg])
                    bundle_mode, port_speed = get_lag_mode_speed(data,pg)
                    bundle_mode = 'lacp_' + bundle_mode
                    entry['bundle_type'] = "pc"
                    entry['bundle_mode'] = bundle_mode
                    entry['node1'] = node1
                    entry['node1_ports'] = node1_ports
                    entry['node2'] = node2
                    entry['node2_ports'] = node2_ports
                    entry['port_speed'] = port_speed
                    entry['port_description'] = pg
                    aci_bindings_with_ports[bd].append(entry.copy())

    return aci_bindings_with_ports

def get_vrf_bd_bindings(aci_tenants):
    # aci_tenants=[]
    aci_vrfs=[]
    aci_bds=[]
    aci_bindings={}
    path_tuple={}


    for T in aci_tenants:
        aci_tenant_name = str(T['attributes']['name'])
        for child in T['children']:
            if 'fvCtx' in child.keys():
                aci_vrf_name=str(child['fvCtx']['attributes']['name'])
                apstra_rz_name=aci_tenant_name+'_'+aci_vrf_name
                child['fvCtx']['attributes']['aci_tenant_name'] = aci_tenant_name
                child['fvCtx']['attributes']['apstra_rz_name']= apstra_rz_name
                aci_vrfs.append(child)
            if 'fvBD' in child.keys():
                aci_bd_name = str(child['fvBD']['attributes']['name'])
                aci_bd_subnets=[]
                apstra_vn_name= aci_tenant_name + '_' + aci_bd_name
                for subchild in child['fvBD']['children']:
                    if 'fvRsCtx' in subchild.keys():
                        aci_vrf_name = str(subchild['fvRsCtx']['attributes']['tnFvCtxName'])
                        apstra_rz_name = aci_tenant_name + '_' + aci_vrf_name
                    if 'fvSubnet' in subchild.keys():
                        subnet = str(subchild['fvSubnet']['attributes']['ip'])
                        aci_bd_subnets.append(subnet)
                child['fvBD']['attributes']['aci_tenant_name'] = aci_tenant_name
                child['fvBD']['attributes']['apstra_rz_name'] = apstra_rz_name
                child['fvBD']['attributes']['apstra_vn_name'] = apstra_vn_name
                child['fvBD']['attributes']['aci_bd_subnets'] = aci_bd_subnets
                aci_bds.append(child)
                aci_bindings[apstra_vn_name]=[]
    for T in aci_tenants:
        aci_tenant_name = str(T['attributes']['name'])
        for child in T['children']:
            if 'fvAp' in child.keys():
                try:
                    for subchild in child['fvAp']['children']:
                        if 'fvAEPg' in subchild.keys():
                            for sub2child in subchild['fvAEPg']['children']:
                                if 'fvRsBd' in sub2child.keys():
                                    aci_bd_name=sub2child['fvRsBd']['attributes']['tnFvBDName']
                                    apstra_vn_name=aci_tenant_name + '_' + aci_bd_name
                            for sub2child in subchild['fvAEPg']['children']:
                                if 'fvRsPathAtt' in sub2child.keys():
                                    encap=sub2child['fvRsPathAtt']['attributes']['encap']
                                    path=sub2child['fvRsPathAtt']['attributes']['tDn']
                                    mode=sub2child['fvRsPathAtt']['attributes']['mode']
                                    if mode == 'regular':
                                        mode='tagged'
                                    path_tuple['encap']=encap
                                    path_tuple['mode']=mode
                                    path_tuple['path'] = path
                                    aci_bindings[apstra_vn_name].append(path_tuple.copy())
                except:
                    continue
    return aci_bindings


def get_nodes_with_interface_profiles(data):
    interface_profiles = []
    node_profiles = []
    nodes_with_interface_profiles = {}
    # node_profiles = extract_objects_of_type(file_path, 'infraNodeP')
    # interface_profiles = extract_objects_of_type(file_path, 'infraAccPortP')
    node_profiles=search_json(data, 'infraNodeP')
    interface_profiles=search_json(data, 'infraAccPortP')
    for nodep in node_profiles:
        list_of_nodes = []
        list_of_intprofiles = []
        for child in nodep['children']:
            if 'infraRsAccPortP' in child.keys():
                tdn = str(child['infraRsAccPortP']['attributes']['tDn'])
                if len(tdn) != 0:
                    interface_profile_name = tdn.removeprefix('uni/infra/accportprof-')
                    list_of_intprofiles.append(interface_profile_name)
            elif 'infraLeafS' in child.keys():
                for nodeblk in child['infraLeafS']['children']:
                    first_node = int(nodeblk['infraNodeBlk']['attributes']['from_'])
                    last_node = int(nodeblk['infraNodeBlk']['attributes']['to_'])
                    if first_node != last_node:
                        list_of_nodes = list(range(first_node, last_node + 1, 1))
                    elif first_node == last_node:
                        list_of_nodes.append(first_node)
        if len(list_of_intprofiles) == 0 or len(list_of_nodes) == 0:
            continue
        else:
            for node in list_of_nodes:
                nodes_with_interface_profiles[node] = list_of_intprofiles
    return nodes_with_interface_profiles


def get_interface_profile_tree(data):
    interface_profiles=search_json(data, 'infraAccPortP')
    interface_profile_ports_tree = {}
    list_of_ports = []
    for profile in interface_profiles:
        interface_profile_name = profile['attributes']['name']
        # policy_group_name = 'NULL'
        interface_profile_ports_tree[interface_profile_name] = {}
        if 'children' in profile.keys():
            for child in profile['children']:
                list_of_ports = []
                policy_group_name = 'NULL'
                for entry in child['infraHPortS']['children']:
                    if 'infraRsAccBaseGrp' in entry.keys():
                        tdn = entry['infraRsAccBaseGrp']['attributes']['tDn']
                        if 'accportgrp' in tdn:
                            policy_group_name = tdn.removeprefix('uni/infra/funcprof/accportgrp-')
                        elif 'accbundle' in tdn:
                            policy_group_name = tdn.removeprefix('uni/infra/funcprof/accbundle-')
                    if 'infraPortBlk' in entry.keys():
                        first_port = int(entry['infraPortBlk']['attributes']['fromPort'])
                        last_port = int(entry['infraPortBlk']['attributes']['toPort'])
                        if first_port != last_port:
                            list_of_ports = list(range(first_port, last_port + 1, 1))
                        elif first_port == last_port:
                            list_of_ports.append(first_port)
                if policy_group_name == 'NULL' or len(list_of_ports) == 0:
                    continue
                else:
                    try:
                        interface_profile_ports_tree[interface_profile_name][policy_group_name] += list_of_ports
                    except:
                        interface_profile_ports_tree[interface_profile_name][policy_group_name] = list_of_ports
        else:
            continue
    return interface_profile_ports_tree

def get_lag_mode_speed(data,input_pg_name):
    list_of_bundles_pgs = []
    node_profiles = []
    nodes_with_interface_profiles = {}
    # list_of_bundles_pgs = extract_objects_of_type(file_path, 'infraAccBndlGrp')
    # list_of_speed_policies = extract_objects_of_type(file_path, 'fabricHIfPol')
    # list_of_bundle_policies = extract_objects_of_type(file_path, 'lacpLagPol')
    list_of_bundles_pgs=search_json(data, 'infraAccBndlGrp')
    list_of_speed_policies=search_json(data, 'fabricHIfPol')
    list_of_bundle_policies=search_json(data, 'lacpLagPol')
    for pg in list_of_bundles_pgs:
        pg_name=pg['attributes']['name']
        if pg_name == input_pg_name:
            for child in pg['children']:
                if 'infraRsLacpPol' in child.keys():
                    bundle_policy_name=child['infraRsLacpPol']['attributes']['tnLacpLagPolName']
                elif 'infraRsHIfPol' in child.keys():
                    speed_policy_name=child['infraRsHIfPol']['attributes']['tnFabricHIfPolName']
            for policy in list_of_bundle_policies:
                if bundle_policy_name == policy['attributes']['name']:
                    bundle_policy = policy['attributes']['mode']
            for policy in list_of_speed_policies:
                if speed_policy_name == policy['attributes']['name']:
                    speed_policy = policy['attributes']['speed']
    return bundle_policy , speed_policy


def get_int_speed (data, node, port):
    node = int(node)
    interface_profile_tree = get_interface_profile_tree(data)
    nodes_with_interface_profiles = get_nodes_with_interface_profiles(data)
    # list_of_individual_pgs = extract_objects_of_type(file_path, 'infraAccPortGrp')
    # list_of_speed_policies = extract_objects_of_type(file_path, 'fabricHIfPol')
    list_of_individual_pgs=search_json(data, 'infraAccPortGrp')
    list_of_speed_policies=search_json(data, 'fabricHIfPol')
    list_of_interface_profiles = nodes_with_interface_profiles[node]
    for profile in list_of_interface_profiles:
        for ip in interface_profile_tree.keys():
            for pg in interface_profile_tree[ip].keys():
                for p in interface_profile_tree[ip][pg]:
                    if str(p) == port:
                        policy_group = pg
    for pg in list_of_individual_pgs:
        if policy_group == pg['attributes']['name']:
            for child in pg['children']:
                if 'infraRsHIfPol' in child.keys():
                    speed_policy_name = child['infraRsHIfPol']['attributes']['tnFabricHIfPolName']
                    for policy in list_of_speed_policies:
                        if speed_policy_name == policy['attributes']['name']:
                            speed_policy = policy['attributes']['speed']
    return speed_policy









