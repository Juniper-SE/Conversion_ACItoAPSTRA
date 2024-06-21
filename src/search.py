import utils
import re
import csv
import json

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
            vn_temp_data["vn_name"] = tennant["attributes"]["name"] + "_" + vrf["attributes"]["name"]
            vn_temp_data["vn_mac"] = vrf["attributes"]["mac"]
            vn_temp_data["vn_unicastRoute"] = vrf["attributes"]["unicastRoute"]
            if vn_temp_data["vn_unicastRoute"] == "yes":
                vn_temp_data["vn_unicastRoute"] = "true"
            elif vn_temp_data["vn_unicastRoute"] == "no":
                vn_temp_data["vn_unicastRoute"] = "false"
            for child_vn in vrf["children"]:
                vn_child_temp_data = {}
                if "fvRsCtx" in child_vn:
                    if child_vn["fvRsCtx"]["attributes"]["tnFvCtxName"] != "":
                        vn_temp_data["vn_vrf_bind"] = tennant["attributes"]["name"] + "_" + child_vn["fvRsCtx"]["attributes"]["tnFvCtxName"]
                    else:
                        vn_temp_data["vn_vrf_bind"] = "ignore_this_vn"
                if vrf["attributes"]["unicastRoute"] == "yes":
                    if "fvSubnet" in child_vn:
                        vn_child_temp_data["aci_ip"] = child_vn["fvSubnet"]["attributes"]["ip"]
                        ip, network = utils.get_ip_and_network(child_vn["fvSubnet"]["attributes"]["ip"])
                        vn_child_temp_data["apstra_ip"] = ip
                        vn_child_temp_data["apstra_network"] = network
                        vn_temp_data["children"].append(dict(vn_child_temp_data))
            if vn_temp_data["vn_vrf_bind"] != "ignore_this_vn":
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
                entry['vn_tag_list'] = []
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
                    entry['vn_tag_list'] = []
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
                    entry['vn_tag_list'] = []
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
                                    encap=str(encap)
                                    encap=encap.removeprefix("vlan-")
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


def get_int_speed(data, node, port):
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


def apstra_port_num (port_mapping_filename,aci_node_id,aci_port_num):
    with open(port_mapping_filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if (row['aci_node_id'] == str(aci_node_id)) & (row['aci_port_num'] == str(aci_port_num)):
                apstra_port_num = row['apstra_port_num']
                break
    return apstra_port_num


def get_generic_systems(data, filename):
    generic_system_single = {}
    generic_system_pc = {}
    generic_system_esi = {}
    vn_to_vlan = {}
    list_of_node_ids = []
    for vn in data.keys():
        try:
            vn_to_vlan[vn] = data[vn][0]["encap"]
        except:
            continue
    for vn in data.keys():
        for path in data[vn]:
            if path["bundle_type"] == "pc":
                generic_system_pc[path["port_description"]] = path
            if path["bundle_type"] == "esi":
                generic_system_esi[path["port_description"]] = path
            if path["bundle_type"] == "No LAG":
                generic_system_single[path["port_description"]] = path
            try:
                if path["node1"] != "null":
                    list_of_node_ids.append(path["node1"])
                if path["node2"] != "null":
                    list_of_node_ids.append(path["node2"])
            except:
                continue
    list_of_node_ids = set(list_of_node_ids)
    for vn in data.keys():
        for path in data[vn]:
            if path["bundle_type"] == "pc":
                if path["mode"] == "tagged":
                    vn_and_mode = str(vn) + "_" + "tagged"
                if path["mode"] == "untagged":
                    vn_and_mode = str(vn) + "_" + "untagged"
                generic_system_pc[path["port_description"]]["vn_tag_list"].extend([vn_and_mode])
            if path["bundle_type"] == "esi":
                if path["mode"] == "tagged":
                    vn_and_mode = str(vn) + "_" + "tagged"
                if path["mode"] == "untagged":
                    vn_and_mode = str(vn) + "_" + "untagged"
                generic_system_esi[path["port_description"]]["vn_tag_list"].extend([vn_and_mode])
            if path["bundle_type"] == "No LAG":
                if path["mode"] == "tagged":
                    vn_and_mode = str(vn) + "_" + "tagged"
                if path["mode"] == "untagged":
                    vn_and_mode = str(vn) + "_" + "untagged"
                generic_system_single[path["port_description"]]["vn_tag_list"].extend([vn_and_mode])
    for path in generic_system_esi.keys():
        list_aci_node1_ports = generic_system_esi[path]['node1_ports']
        list_aci_node2_ports = generic_system_esi[path]['node2_ports']
        vn_tag_list = generic_system_esi[path]['vn_tag_list']
        vn_tag_list = json.dumps(vn_tag_list)
        generic_system_esi[path]['vn_tag_list'] = vn_tag_list
        if list_aci_node1_ports != "null":
            list_apstra_node1_ports = []
            for port in list_aci_node1_ports:
                apstra_port = apstra_port_num(filename, generic_system_esi[path]['node1'], port)
                list_apstra_node1_ports.append(apstra_port)
            generic_system_esi[path]['node1_ports'] = list_apstra_node1_ports
        if list_aci_node2_ports != "null":
            list_apstra_node2_ports = []
            for port in list_aci_node2_ports:
                apstra_port = apstra_port_num(filename, generic_system_esi[path]['node2'], port)
                list_apstra_node2_ports.append(apstra_port)
            generic_system_esi[path]['node2_ports'] = list_apstra_node2_ports
    for path in generic_system_pc.keys():
        list_aci_node1_ports = generic_system_pc[path]['node1_ports']
        vn_tag_list = generic_system_pc[path]['vn_tag_list']
        vn_tag_list = json.dumps(vn_tag_list)
        generic_system_pc[path]['vn_tag_list'] = vn_tag_list
        if list_aci_node1_ports != "null":
            list_apstra_node1_ports = []
            for port in list_aci_node1_ports:
                apstra_port = apstra_port_num(filename, generic_system_pc[path]['node1'], port)
                list_apstra_node1_ports.append(apstra_port)
            generic_system_pc[path]['node1_ports'] = list_apstra_node1_ports
    for path in generic_system_single.keys():
        list_aci_node1_ports = generic_system_single[path]['node1_ports']
        vn_tag_list = generic_system_single[path]['vn_tag_list']
        vn_tag_list = json.dumps(vn_tag_list)
        generic_system_single[path]['vn_tag_list'] = vn_tag_list
        if list_aci_node1_ports != "null":
            list_apstra_node1_ports = []
            for port in list_aci_node1_ports:
                apstra_port = apstra_port_num(filename, generic_system_single[path]['node1'], port)
                list_apstra_node1_ports.append(apstra_port)
            generic_system_single[path]['node1_ports'] = list_apstra_node1_ports

    return generic_system_single, generic_system_pc, generic_system_esi, vn_to_vlan, list_of_node_ids


def get_generic_systems_nb(data, filename):
    generic_system_single = {}
    generic_system_pc = {}
    generic_system_esi = {}
    vn_to_vlan = {}
    list_of_node_ids = []
    for vn in data.keys():
        try:
            vn_to_vlan[vn] = data[vn][0]["encap"]
        except:
            continue
    for vn in data.keys():
        for path in data[vn]:
            if path["bundle_type"] == "pc":
                generic_system_pc[path["port_description"]] = path
            if path["bundle_type"] == "esi":
                generic_system_esi[path["port_description"]] = path
            if path["bundle_type"] == "No LAG":
                generic_system_single[path["port_description"]] = path
            try:
                if path["node1"] != "null":
                    list_of_node_ids.append(path["node1"])
                if path["node2"] != "null":
                    list_of_node_ids.append(path["node2"])
            except:
                continue
    list_of_node_ids = set(list_of_node_ids)
    for vn in data.keys():
        for path in data[vn]:
            if path["bundle_type"] == "pc":
                if path["mode"] == "tagged":
                    vn_and_mode = str(vn) + "_" + "tagged"
                if path["mode"] == "untagged":
                    vn_and_mode = str(vn) + "_" + "untagged"
                generic_system_pc[path["port_description"]]["vn_tag_list"].extend([vn_and_mode])
            if path["bundle_type"] == "esi":
                if path["mode"] == "tagged":
                    vn_and_mode = str(vn) + "_" + "tagged"
                if path["mode"] == "untagged":
                    vn_and_mode = str(vn) + "_" + "untagged"
                generic_system_esi[path["port_description"]]["vn_tag_list"].extend([vn_and_mode])
            if path["bundle_type"] == "No LAG":
                if path["mode"] == "tagged":
                    vn_and_mode = str(vn) + "_" + "tagged"
                if path["mode"] == "untagged":
                    vn_and_mode = str(vn) + "_" + "untagged"
                generic_system_single[path["port_description"]]["vn_tag_list"].extend([vn_and_mode])
    for path in generic_system_esi.keys():
        list_aci_node1_ports = generic_system_esi[path]['node1_ports']
        list_aci_node2_ports = generic_system_esi[path]['node2_ports']
        vn_tag_list = generic_system_esi[path]['vn_tag_list']
        vn_tag_list = json.dumps(vn_tag_list)
        generic_system_esi[path]['vn_tag_list'] = vn_tag_list
        if list_aci_node1_ports != "null":
            list_apstra_node1_ports = []
            for port in list_aci_node1_ports:
                apstra_port = "Ethernet1/" + str(port)
                list_apstra_node1_ports.append(apstra_port)
            generic_system_esi[path]['node1_ports'] = list_apstra_node1_ports
        if list_aci_node2_ports != "null":
            list_apstra_node2_ports = []
            for port in list_aci_node2_ports:
                apstra_port = "Ethernet1/" + str(port)
                list_apstra_node2_ports.append(apstra_port)
            generic_system_esi[path]['node2_ports'] = list_apstra_node2_ports
    for path in generic_system_pc.keys():
        list_aci_node1_ports = generic_system_pc[path]['node1_ports']
        vn_tag_list = generic_system_pc[path]['vn_tag_list']
        vn_tag_list = json.dumps(vn_tag_list)
        generic_system_pc[path]['vn_tag_list'] = vn_tag_list
        if list_aci_node1_ports != "null":
            list_apstra_node1_ports = []
            for port in list_aci_node1_ports:
                apstra_port = "Ethernet1/" + str(port)
                list_apstra_node1_ports.append(apstra_port)
            generic_system_pc[path]['node1_ports'] = list_apstra_node1_ports
    for path in generic_system_single.keys():
        list_aci_node1_ports = generic_system_single[path]['node1_ports']
        vn_tag_list = generic_system_single[path]['vn_tag_list']
        vn_tag_list = json.dumps(vn_tag_list)
        generic_system_single[path]['vn_tag_list'] = vn_tag_list
        if list_aci_node1_ports != "null":
            list_apstra_node1_ports = []
            for port in list_aci_node1_ports:
                apstra_port = "Ethernet1/" + str(port)
                list_apstra_node1_ports.append(apstra_port)
            generic_system_single[path]['node1_ports'] = list_apstra_node1_ports

    return generic_system_single, generic_system_pc, generic_system_esi, vn_to_vlan, list_of_node_ids

def aci_fabric_discover(data, fnvread_file_path):
    aci_leaf_nodes = []
    aci_leaf_ids = []
    aci_spine_nodes = []
    aci_spine_ids = []
    aci_leaf = {}
    aci_spine = {}
    spine_models = []
    leaf_models = []
    logical_device = {}
    logical_devices = []
    i = 0
    with open(fnvread_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['nodeRole'] == "3":
                i = i + 1
                label = "spine" + str(i)
                aci_spine['id'] = row['id']
                aci_spine['model'] = row['model']
                aci_spine['fabricId'] = row['fabricId']
                aci_spine['podId'] = row['podId']
                aci_spine['label'] = label
                aci_spine_nodes.append(aci_spine.copy())
                aci_spine_ids.append(row['id'])
            if row['nodeRole'] == "2":
                aci_leaf['id'] = row['id']
                aci_leaf['model'] = row['model']
                aci_leaf['fabricId'] = row['fabricId']
                aci_leaf['podId'] = row['podId']
                aci_leaf_nodes.append(aci_leaf.copy())
                aci_leaf_ids.append(row['id'])
    for spine in aci_spine_nodes:
        spine_models.append(spine['model'])
    for leaf in aci_leaf_nodes:
        leaf_models.append(leaf['model'])
    spine_models = list(set(spine_models))
    leaf_models = list(set(leaf_models))
    for model in leaf_models:
        with open("./cisco_device_profiles/cisco_device_models.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['cisco_model'] == model:
                    logical_device['name'] = "LD_" + model
                    logical_device['model'] = model
                    logical_device['device_profile'] = row['device_profile']
                    logical_device['panel_1_count'] = int(row['panel_1_count'])
                    logical_device['panel_1_speed'] = row['panel_1_speed']
                    logical_device['panel_2_count'] = int(row['panel_2_count'])
                    logical_device['panel_2_speed'] = row['panel_2_speed']
                    logical_device['panel_3_count'] = int(row['panel_3_count'])
                    logical_device['panel_3_speed'] = row['panel_3_speed']
                    logical_device['panel_4_count'] = int(row['panel_4_count'])
                    logical_device['panel_4_speed'] = row['panel_4_speed']
                    logical_device['panel_5_count'] = int(row['panel_5_count'])
                    logical_device['panel_5_speed'] = row['panel_5_speed']
                    logical_device['panel_6_count'] = int(row['panel_6_count'])
                    logical_device['panel_6_speed'] = row['panel_6_speed']
                    logical_device['panel_7_count'] = int(row['panel_7_count'])
                    logical_device['panel_7_speed'] = row['panel_7_speed']
                    logical_device['panel_8_count'] = int(row['panel_8_count'])
                    logical_device['panel_8_speed'] = row['panel_8_speed']
                    logical_devices.append(logical_device.copy())
    for model in spine_models:
        with open("./cisco_device_profiles/cisco_device_models.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['cisco_model'] == model:
                    logical_device['name'] = "LD_" + model
                    logical_device['model'] = model
                    logical_device['device_profile'] = row['device_profile']
                    logical_device['panel_1_count'] = int(row['panel_1_count'])
                    logical_device['panel_1_speed'] = row['panel_1_speed']
                    logical_device['panel_2_count'] = int(row['panel_2_count'])
                    logical_device['panel_2_speed'] = row['panel_2_speed']
                    logical_device['panel_3_count'] = int(row['panel_3_count'])
                    logical_device['panel_3_speed'] = row['panel_3_speed']
                    logical_device['panel_4_count'] = int(row['panel_4_count'])
                    logical_device['panel_4_speed'] = row['panel_4_speed']
                    logical_device['panel_5_count'] = int(row['panel_5_count'])
                    logical_device['panel_5_speed'] = row['panel_5_speed']
                    logical_device['panel_6_count'] = int(row['panel_6_count'])
                    logical_device['panel_6_speed'] = row['panel_6_speed']
                    logical_device['panel_7_count'] = int(row['panel_7_count'])
                    logical_device['panel_7_speed'] = row['panel_7_speed']
                    logical_device['panel_8_count'] = int(row['panel_8_count'])
                    logical_device['panel_8_speed'] = row['panel_8_speed']
                    logical_devices.append(logical_device.copy())
    vpc_domains = search_json(data, 'fabricExplicitGEp')
    fabric_policy = search_json(data, 'fabricSetupPol')
    for child in fabric_policy:
        for subchild in child['children']:
            if 'fabricSetupP' in subchild:
                tep_pool = subchild['fabricSetupP']['attributes']['tepPool']
    #tep_pool = fabric_policy['attributes']['tepPool']
    list_of_leaf_pairs = []
    list_of_single_leaf = []
    single_leaf_dict = {}
    list_of_leaf_pairs_ids = []
    leaf_pair_dict = {}
    for path in vpc_domains:
        node_pair = []
        for child in path['children']:
            if "fabricNodePEp" in child.keys():
                node_pair.append(int(child['fabricNodePEp']['attributes']['id']))
                list_of_leaf_pairs_ids.append(child['fabricNodePEp']['attributes']['id'])
        node_pair.sort()
        leaf_pair_dict['node1'] = str(node_pair[0])
        leaf_pair_dict['node2'] = str(node_pair[1])
        for leaf in aci_leaf_nodes:
            if leaf['id'] == leaf_pair_dict['node1']:
                leaf_pair_dict['model'] = leaf['model']
                leaf_pair_dict['fabricId'] = leaf['fabricId']
                leaf_pair_dict['podId'] = leaf['podId']
        for device in logical_devices:
            if device['model'] == leaf_pair_dict['model']:
                #if device['model'] == "N9K-C9348GC-FXP":
                if device['panel_3_speed'] != "0":
                    leaf_pair_dict['spine_link_speed'] = device['panel_3_speed']
                elif device['panel_2_speed'] != "0":
                    leaf_pair_dict['spine_link_speed'] = device['panel_2_speed']
                else:
                    leaf_pair_dict['spine_link_speed'] = device['panel_1_speed']
        list_of_leaf_pairs.append(leaf_pair_dict.copy())
    for id in aci_leaf_ids:
        if id not in list_of_leaf_pairs_ids:
            single_leaf_dict['id'] = id
            for leaf in aci_leaf_nodes:
                if id == leaf['id']:
                    single_leaf_dict['model'] = leaf['model']
                    single_leaf_dict['fabricId'] = leaf['fabricId']
                    single_leaf_dict['podId'] = leaf['podId']
                    for device in logical_devices:
                        if device['model'] == single_leaf_dict['model']:
                            #if device['model'] == "N9K-C9348GC-FXP":
                            if device['panel_3_speed'] != "0":
                                single_leaf_dict['spine_link_speed'] = device['panel_3_speed']
                            elif device['panel_2_speed'] != "0":
                                single_leaf_dict['spine_link_speed'] = device['panel_2_speed']
                            else:
                                single_leaf_dict['spine_link_speed'] = device['panel_1_speed']
            list_of_single_leaf.append(single_leaf_dict.copy())
    return logical_devices, aci_spine_nodes, list_of_single_leaf, list_of_leaf_pairs, tep_pool

















