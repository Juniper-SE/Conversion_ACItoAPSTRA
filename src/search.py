import utils

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