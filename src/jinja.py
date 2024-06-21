from jinja2 import Template

def generate_apstra_datacenter_routing_zone_config(vrf_list, blueprint_name):
    # Define the Jinja2 template as a string
    template_str = """
    data "apstra_datacenter_blueprint" "blueprint" {
        name = "{{blueprint_name}}"
    }
    {% for vrf in vrf_list %}
    resource "apstra_datacenter_routing_zone" "{{ vrf.apstra_vrf }}_rz" {
      name              = "{{ vrf.apstra_vrf }}"
      blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
    }
    {% endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        blueprint_name=blueprint_name,
        vrf_list=vrf_list
    )

    return output

def generate_apstra_datacenter_routing_zone_nb_config(vrf_list, blueprint_name):
    # Define the Jinja2 template as a string
    template_str = """
    data "apstra_datacenter_blueprint" "blueprint" {
        name = "{{blueprint_name}}"
    }
    {% for vrf in vrf_list %}
    resource "apstra_datacenter_routing_zone" "{{ vrf.apstra_vrf }}_rz" {
      name              = "{{ vrf.apstra_vrf }}"
      blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
    }
    {% endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        blueprint_name=blueprint_name,
        vrf_list=vrf_list
    )

    return output


def generate_apstra_datacenter_virtual_network_config(data, vn_to_vlan):
    # Define the Jinja2 template as a string
    template_str = """
    data "apstra_datacenter_systems" "all_leafs" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        filters = [
            {
                role = "leaf"
                system_type = "switch"
            },
        ]
    }
    data "apstra_datacenter_virtual_network_binding_constructor" "binder_default" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        switch_ids   = tolist(data.apstra_datacenter_systems.all_leafs.ids)
    }
    {%- for key,value in vn_to_vlan.items() %}
    data "apstra_datacenter_virtual_network_binding_constructor" "binder_{{key}}" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        vlan_id      = {{value}}
        switch_ids   = tolist(data.apstra_datacenter_systems.all_leafs.ids)
    }
    {%- endfor %}
    {%- for item in data %}
    resource "apstra_datacenter_virtual_network" "{{ item.vn_name }}" {
      name                         = "{{ item.vn_name }}"
      blueprint_id                 = data.apstra_datacenter_blueprint.blueprint.id
      type                         = "vxlan"
      routing_zone_id              = apstra_datacenter_routing_zone.{{item.vn_vrf_bind}}_rz.id
      ipv4_connectivity_enabled    = {{ item.vn_unicastRoute }}
      ipv4_virtual_gateway_enabled = {{ item.vn_unicastRoute }}
      {%- for sub_item in item.children %}
      ipv4_virtual_gateway         = "{{sub_item.apstra_ip}}"
      ipv4_subnet                  = "{{sub_item.apstra_network}}"
      {%- endfor %}
      {%- if 'mgmt_inb' in item.vn_name or 'infra_default' in item.vn_name or 'infra_ave-ctrl' in item.vn_name  %}
      bindings = data.apstra_datacenter_virtual_network_binding_constructor.binder_default.bindings
      {%- else %}
      reserve_vlan                 = true
      bindings = data.apstra_datacenter_virtual_network_binding_constructor.binder_{{item.vn_name}}.bindings
      {%- endif %}
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        data=data,
        vn_to_vlan=vn_to_vlan
    )

    return output

def generate_apstra_datacenter_virtual_network_nb_config(data, vn_to_vlan):
    # Define the Jinja2 template as a string
    template_str = """
    data "apstra_datacenter_systems" "all_leafs" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        filters = [
            {
                role = "leaf"
                system_type = "switch"
            },
        ]
    }
    data "apstra_datacenter_virtual_network_binding_constructor" "binder_default" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        switch_ids   = tolist(data.apstra_datacenter_systems.all_leafs.ids)
    }
    {%- for key,value in vn_to_vlan.items() %}
    data "apstra_datacenter_virtual_network_binding_constructor" "binder_{{key}}" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        vlan_id      = {{value}}
        switch_ids   = tolist(data.apstra_datacenter_systems.all_leafs.ids)
    }
    {%- endfor %}
    {%- for item in data %}
    resource "apstra_datacenter_virtual_network" "{{ item.vn_name }}" {
      name                         = "{{ item.vn_name }}"
      blueprint_id                 = data.apstra_datacenter_blueprint.blueprint.id
      type                         = "vxlan"
      routing_zone_id              = apstra_datacenter_routing_zone.{{item.vn_vrf_bind}}_rz.id
      ipv4_connectivity_enabled    = {{ item.vn_unicastRoute }}
      ipv4_virtual_gateway_enabled = {{ item.vn_unicastRoute }}
      {%- for sub_item in item.children %}
      ipv4_virtual_gateway         = "{{sub_item.apstra_ip}}"
      ipv4_subnet                  = "{{sub_item.apstra_network}}"
      {%- endfor %}
      {%- if 'mgmt_inb' in item.vn_name or 'infra_default' in item.vn_name or 'infra_ave-ctrl' in item.vn_name  %}
      bindings = data.apstra_datacenter_virtual_network_binding_constructor.binder_default.bindings
      {%- else %}
      reserve_vlan                 = true
      bindings = data.apstra_datacenter_virtual_network_binding_constructor.binder_{{item.vn_name}}.bindings
      {%- endif %}
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        data=data,
        vn_to_vlan=vn_to_vlan
    )

    return output


def generate_apstra_datacenter_generic_system_config(generic_system_single, generic_system_pc, generic_system_esi, list_of_node_ids):
    # Define the Jinja2 template as a string
    template_str = """
    locals {
        blueprint_id     = data.apstra_datacenter_blueprint.blueprint.id
        {%- for item in list_of_node_ids %}
        leaf_{{item}}_id = tolist(data.apstra_datacenter_systems.leaf_{{item}}.ids)
        {%- endfor %}
    }
    {%- for item in list_of_node_ids %}
    data "apstra_datacenter_systems" "leaf_{{item}}" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        filters = [
        {
            tag_ids = ["{{item}}"]
        }
        ]
    }
    {%- endfor %}
    {%- for key,value in generic_system_single.items() %}
    resource "apstra_datacenter_generic_system" "{{key}}" {
        blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
        name              = "{{key}}"
        hostname          = "generic.system"
        tags              = ["terraform", "{{key}}"]
        links = [
        {%- for port in value.node1_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            target_switch_id              = local.leaf_{{value.node1}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            },
        {%- endfor %}
        ]
    }
    {%- endfor %}
    {%- for key,value in generic_system_pc.items() %}
    resource "apstra_datacenter_generic_system" "{{key}}" {
        blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
        name              = "{{key}}"
        hostname          = "generic.system"
        tags              = ["terraform", "{{key}}"]
        links = [
        {%- for port in value.node1_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            lag_mode                      = "{{value.bundle_mode}}"  
            target_switch_id              = local.leaf_{{value.node1}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            group_label                   = "bond0"
            },
        {%- endfor %}
        ]
    }
    {%- endfor %}
    {%- for key,value in generic_system_esi.items() %}
    resource "apstra_datacenter_generic_system" "{{key}}" {
        blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
        name              = "{{key}}"
        hostname          = "generic.system"
        tags              = ["terraform", "{{key}}"]
        links = [
        {%- for port in value.node1_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            lag_mode                      = "{{value.bundle_mode}}"  
            target_switch_id              = local.leaf_{{value.node1}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            group_label                   = "bond0"
            },
        {%- endfor %}
        {%- for port in value.node2_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            lag_mode                      = "{{value.bundle_mode}}"  
            target_switch_id              = local.leaf_{{value.node2}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            group_label                   = "bond0"
            },
        {%- endfor %}
        ]
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(

        generic_system_single=generic_system_single,
        generic_system_pc=generic_system_pc,
        generic_system_esi=generic_system_esi,
        list_of_node_ids=list_of_node_ids
    )

    return output


def generate_apstra_datacenter_ct_config(vn_to_vlan):
    # Define the Jinja2 template as a string
    template_str = """
    {%- for key in vn_to_vlan.keys() %}
    data "apstra_datacenter_ct_virtual_network_single" "{{key}}_ct_tagged" {
      vn_id  = apstra_datacenter_virtual_network.{{key}}.id
      tagged = true
    }
    data "apstra_datacenter_ct_virtual_network_single" "{{key}}_ct_untagged" {
      vn_id  = apstra_datacenter_virtual_network.{{key}}.id
      tagged = false
    }
    resource "apstra_datacenter_connectivity_template" "{{key}}_ct_tagged" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      name         = "{{key}}_ct_tagged"
      description  = "Tagged Connectivity Template for VN: {{key}}"
      tags         = [
        "{{key}}_tagged",
      ]
      primitives   = [
        data.apstra_datacenter_ct_virtual_network_single.{{key}}_ct_tagged.primitive
      ]
    }
    resource "apstra_datacenter_connectivity_template" "{{key}}_ct_untagged" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      name         = "{{key}}_ct_untagged"
      description  = "Tagged Connectivity Template for VN: {{key}}"
      tags         = [
        "{{key}}_untagged",
      ]
      primitives   = [
        data.apstra_datacenter_ct_virtual_network_single.{{key}}_ct_untagged.primitive
      ]
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        vn_to_vlan=vn_to_vlan
    )

    return output

def generate_apstra_datacenter_ct_nb_config(vn_to_vlan):
    # Define the Jinja2 template as a string
    template_str = """
    {%- for key in vn_to_vlan.keys() %}
    data "apstra_datacenter_ct_virtual_network_single" "{{key}}_ct_tagged" {
      vn_id  = apstra_datacenter_virtual_network.{{key}}.id
      tagged = true
    }
    data "apstra_datacenter_ct_virtual_network_single" "{{key}}_ct_untagged" {
      vn_id  = apstra_datacenter_virtual_network.{{key}}.id
      tagged = false
    }
    resource "apstra_datacenter_connectivity_template" "{{key}}_ct_tagged" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      name         = "{{key}}_ct_tagged"
      description  = "Tagged Connectivity Template for VN: {{key}}"
      tags         = [
        "{{key}}_tagged",
      ]
      primitives   = [
        data.apstra_datacenter_ct_virtual_network_single.{{key}}_ct_tagged.primitive
      ]
    }
    resource "apstra_datacenter_connectivity_template" "{{key}}_ct_untagged" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      name         = "{{key}}_ct_untagged"
      description  = "Tagged Connectivity Template for VN: {{key}}"
      tags         = [
        "{{key}}_untagged",
      ]
      primitives   = [
        data.apstra_datacenter_ct_virtual_network_single.{{key}}_ct_untagged.primitive
      ]
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        vn_to_vlan=vn_to_vlan
    )

    return output

def generate_apstra_datacenter_ct_assign_config(vn_to_vlan):
    # Define the Jinja2 template as a string
    template_str = """
    {%- for key in vn_to_vlan.keys() %}
    data "apstra_datacenter_interfaces_by_link_tag" "{{key}}_tagged_links" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      tags         = ["{{key}}_tagged"]
    }
    data "apstra_datacenter_interfaces_by_link_tag" "{{key}}_untagged_links" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      tags         = ["{{key}}_untagged"]
    }
    resource "apstra_datacenter_connectivity_template_assignments" "{{key}}_tagged" {
      count = data.apstra_datacenter_interfaces_by_link_tag.{{key}}_tagged_links.ids != null ? 1 : 0
      blueprint_id              = data.apstra_datacenter_blueprint.blueprint.id
      application_point_ids    = tolist(data.apstra_datacenter_interfaces_by_link_tag.{{key}}_tagged_links.ids)
      connectivity_template_id = apstra_datacenter_connectivity_template.{{key}}_ct_tagged.id
    }
    resource "apstra_datacenter_connectivity_template_assignments" "{{key}}_untagged" {
      count = data.apstra_datacenter_interfaces_by_link_tag.{{key}}_untagged_links.ids != null ? 1 : 0
      blueprint_id              = data.apstra_datacenter_blueprint.blueprint.id
      application_point_ids    = tolist(data.apstra_datacenter_interfaces_by_link_tag.{{key}}_untagged_links.ids)
      connectivity_template_id = apstra_datacenter_connectivity_template.{{key}}_ct_untagged.id
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        vn_to_vlan=vn_to_vlan
    )
    return output

def generate_apstra_datacenter_ct_assign_nb_config(vn_to_vlan,blueprint_name):
    # Define the Jinja2 template as a string
    template_str = """
    {%- for key in vn_to_vlan.keys() %}
    data "apstra_datacenter_interfaces_by_link_tag" "{{key}}_tagged_links" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      tags         = ["{{key}}_tagged"]
    }
    data "apstra_datacenter_interfaces_by_link_tag" "{{key}}_untagged_links" {
      blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
      tags         = ["{{key}}_untagged"]
    }
    resource "apstra_datacenter_connectivity_template_assignments" "{{key}}_tagged" {
      count = data.apstra_datacenter_interfaces_by_link_tag.{{key}}_tagged_links.ids != null ? 1 : 0
      blueprint_id              = data.apstra_datacenter_blueprint.blueprint.id
      application_point_ids    = tolist(data.apstra_datacenter_interfaces_by_link_tag.{{key}}_tagged_links.ids)
      connectivity_template_id = apstra_datacenter_connectivity_template.{{key}}_ct_tagged.id
    }
    resource "apstra_datacenter_connectivity_template_assignments" "{{key}}_untagged" {
      count = data.apstra_datacenter_interfaces_by_link_tag.{{key}}_untagged_links.ids != null ? 1 : 0
      blueprint_id              = data.apstra_datacenter_blueprint.blueprint.id
      application_point_ids    = tolist(data.apstra_datacenter_interfaces_by_link_tag.{{key}}_untagged_links.ids)
      connectivity_template_id = apstra_datacenter_connectivity_template.{{key}}_ct_untagged.id
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        vn_to_vlan=vn_to_vlan,
        blueprint_name=blueprint_name
    )
    return output

def generate_apstra_logical_devices_config(logical_devices):
    # Define the Jinja2 template as a string
    template_str = """
    {%- for device in logical_devices %}
    resource "apstra_logical_device" "{{device.name}}" {
      name = "{{device.name}}"
      panels = [
        {%- if device.panel_1_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_1_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_1_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_1_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_1_count == 48  %}
        {
          rows = 2
          columns = 24
          port_groups = [
            {
              port_count = 48
              port_speed = "{{device.panel_1_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_1_count == 64  %}
        {
          rows = 4
          columns = 16
          port_groups = [
            {
              port_count = 64
              port_speed = "{{device.panel_1_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_1_count == 96  %}
        {
          rows = 4
          columns = 24
          port_groups = [
            {
              port_count = 96
              port_speed = "{{device.panel_1_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_2_count == 2  %}
        {
          rows = 1
          columns = 2
          port_groups = [
            {
              port_count = 2
              port_speed = "{{device.panel_2_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_2_count == 4  %}
        {
          rows = 2
          columns = 2
          port_groups = [
            {
              port_count = 4
              port_speed = "{{device.panel_2_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_2_count == 6  %}
        {
          rows = 2
          columns = 3
          port_groups = [
            {
              port_count = 6
              port_speed = "{{device.panel_2_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_2_count == 12  %}
        {
          rows = 2
          columns = 6
          port_groups = [
            {
              port_count = 12
              port_speed = "{{device.panel_2_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_2_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_2_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_2_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_2_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_3_count == 2  %}
        {
          rows = 1
          columns = 2
          port_groups = [
            {
              port_count = 2
              port_speed = "{{device.panel_3_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_3_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_3_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_3_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_3_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_4_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_4_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_4_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_4_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_5_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_5_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_5_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_5_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_6_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_6_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_6_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_6_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_7_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_7_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_7_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_7_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_8_count == 32  %}
        {
          rows = 2
          columns = 16
          port_groups = [
            {
              port_count = 32
              port_speed = "{{device.panel_8_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
        {%- if device.panel_8_count == 36  %}
        {
          rows = 2
          columns = 18
          port_groups = [
            {
              port_count = 36
              port_speed = "{{device.panel_8_speed}}"
              port_roles = ["superspine", "spine", "leaf", "peer", "access", "generic"]
            },
            ]
            },
        {%- endif %}
          ]
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        logical_devices=logical_devices
    )
    return output

def generate_apstra_interface_maps_config(logical_devices,aci_spine_nodes, list_of_single_leaf, list_of_leaf_pairs):
    # Define the Jinja2 template as a string
    template_str = """
    locals {
    {%- for device in logical_devices %}
      if_map_{{device.model}} = [
        { ld_panel       = 1
          ld_first_port  = 1
          phy_prefix     = "Ethernet1/"
          phy_first_port = 1
          count          = {{device.panel_1_count}}
        },
        { ld_panel       = 2
          ld_first_port  = 1
          {%- if "9504" in device.model or "9508" in device.model %}
          phy_prefix     = "Ethernet2/"
          phy_first_port = 1
          {%- else %}
          phy_prefix     = "Ethernet1/"
          phy_first_port = {{device.panel_1_count + 1}}
          {%- endif %}
          count          = {{device.panel_2_count}}
        },
        {%- if device.panel_3_count != 0 %}
        { ld_panel       = 3
          ld_first_port  = 1
          {%- if "9504" in device.model or "9508" in device.model %}
          phy_prefix     = "Ethernet3/"
          phy_first_port = 1
          {%- else %}
          phy_prefix     = "Ethernet1/"
          phy_first_port = {{device.panel_2_count + 1}}
          {%- endif %}
          count          = {{device.panel_3_count}}
        },
        {%- endif %}
        {%- if device.panel_4_count != 0 %}
        { ld_panel       = 4
          ld_first_port  = 1
          phy_prefix     = "Ethernet4/"
          phy_first_port = 1
          count          = {{device.panel_4_count}}
        },
        {%- endif %}
        {%- if device.panel_5_count != 0 %}
        { ld_panel       = 5
          ld_first_port  = 1
          phy_prefix     = "Ethernet5/"
          phy_first_port = 1
          count          = {{device.panel_5_count}}
        },
        {%- endif %}
        {%- if device.panel_6_count != 0 %}
        { ld_panel       = 6
          ld_first_port  = 1
          phy_prefix     = "Ethernet6/"
          phy_first_port = 1
          count          = {{device.panel_6_count}}
        },
        {%- endif %}
        {%- if device.panel_7_count != 0 %}
        { ld_panel       = 7
          ld_first_port  = 1
          phy_prefix     = "Ethernet7/"
          phy_first_port = 1
          count          = {{device.panel_7_count}}
        },
        {%- endif %}
        {%- if device.panel_8_count != 0 %}
        { ld_panel       = 8
          ld_first_port  = 1
          phy_prefix     = "Ethernet8/"
          phy_first_port = 1
          count          = {{device.panel_8_count}}
        },
        {%- endif %}
      ]
      interfaces_{{device.model}} = [
        for map in local.if_map_{{device.model}} : [
          for i in range(map.count) : {
            logical_device_port     = format("%d/%d", map.ld_panel, map.ld_first_port + i)
            physical_interface_name = format("%s%d", map.phy_prefix, map.phy_first_port + i)
            "transformation_id"       = 1
          }
        ]
      ]
    {%- endfor %}
    }
    {%- for device in logical_devices %}
    resource "apstra_interface_map" "IMAP_{{device.model}}" {
      name              = "IMAP_{{device.model}}"
      logical_device_id = apstra_logical_device.LD_{{device.model}}.id
      device_profile_id = "{{device.device_profile}}"
      interfaces        = flatten([local.interfaces_{{device.model}}])
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        logical_devices=logical_devices,
        aci_spine_nodes=aci_spine_nodes,
        list_of_single_leaf=list_of_single_leaf,
        list_of_leaf_pairs=list_of_leaf_pairs
    )
    return output

def generate_apstra_rack_types_config(list_of_single_leaf, list_of_leaf_pairs):
    # Define the Jinja2 template as a string
    template_str = """
    {%- for rack in list_of_leaf_pairs %}
    resource "apstra_rack_type" "dual_{{rack.node1}}_{{rack.node2}}" {
      name                       = "dual_{{rack.node1}}_{{rack.node2}}"
      description                = "dual_{{rack.model}}"
      fabric_connectivity_design = "l3clos"
      leaf_switches = {
        leaf_{{rack.node1}}_{{rack.node2}} = {
          logical_device_id   = apstra_logical_device.LD_{{rack.model}}.id
          spine_link_count    = 1
          spine_link_speed    = "{{rack.spine_link_speed}}"
          redundancy_protocol = "mlag"
          mlag_info = {
          mlag_keepalive_vlan = 4093
          peer_link_count = 1
          peer_link_port_channel_id = 1
          peer_link_speed = "{{rack.spine_link_speed}}"
      }
        }
      }
    }
    {%- endfor %}
    {%- for rack in list_of_single_leaf %}
    resource "apstra_rack_type" "single_{{rack.id}}" {
      name                       = "single_{{rack.id}}"
      description                = "single_{{rack.model}}"
      fabric_connectivity_design = "l3clos"
      leaf_switches = {
        leaf_{{rack.id}} = {
          logical_device_id   = apstra_logical_device.LD_{{rack.model}}.id
          spine_link_count    = 1
          spine_link_speed    = "{{rack.spine_link_speed}}"
        }
      }
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        list_of_single_leaf=list_of_single_leaf,
        list_of_leaf_pairs=list_of_leaf_pairs
    )
    return output

def generate_apstra_template_config(aci_spine_nodes,list_of_single_leaf, list_of_leaf_pairs):
    # Define the Jinja2 template as a string
    spine_count = len(aci_spine_nodes)
    template_str = """
    resource "apstra_template_rack_based" "created_from_aci_fabric" {
      name                     = "created_from_aci_fabric"
      asn_allocation_scheme    = "unique"
      overlay_control_protocol = "evpn"
      spine = {
        logical_device_id = apstra_logical_device.LD_{{aci_spine_nodes[0].model}}.id
        count             = {{spine_count}}
      }
      rack_infos = {
        {%- for rack in list_of_leaf_pairs %}
        (apstra_rack_type.dual_{{rack.node1}}_{{rack.node2}}.id) = {
        tags = ["{{rack.node1}}" , "{{rack.node2}}"]
        count = 1
        },
        {%- endfor %}
        {%- for rack in list_of_single_leaf %}
        (apstra_rack_type.single_{{rack.id}}.id) = {
        tags = ["{{rack.id}}"]
        count = 1
        }
        {%- endfor %}
        }
    }
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        list_of_single_leaf=list_of_single_leaf,
        list_of_leaf_pairs=list_of_leaf_pairs,
        aci_spine_nodes=aci_spine_nodes,
        spine_count=spine_count
    )
    return output

def generate_apstra_blueprint_config(blueprint_name):
    # Define the Jinja2 template as a string
    template_str = """
    resource "apstra_datacenter_blueprint" "blueprint" {
      name        = "{{blueprint_name}}"
      template_id = apstra_template_rack_based.created_from_aci_fabric.id
    }
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        blueprint_name=blueprint_name
    )
    return output

def generate_apstra_interface_maps_assign_config(logical_devices,aci_spine_nodes, list_of_single_leaf, list_of_leaf_pairs):
    # Define the Jinja2 template as a string
    template_str = """
    {%- for spine in aci_spine_nodes %}
    resource "apstra_datacenter_device_allocation" "imap_assign_{{spine.id}}" {
      blueprint_id     = apstra_datacenter_blueprint.blueprint.id
      node_name        = "{{spine.label}}"
      initial_interface_map_id = apstra_interface_map.IMAP_{{spine.model}}.id
    }
    {%- endfor %}
    {%- for leaf in list_of_single_leaf %}
    resource "apstra_datacenter_device_allocation" "imap_assign_{{leaf.id}}" {
      blueprint_id     = apstra_datacenter_blueprint.blueprint.id
      node_name        = "single_{{leaf.id}}_001_leaf1"
      initial_interface_map_id = apstra_interface_map.IMAP_{{leaf.model}}.id
    }
    {%- endfor %}
    {%- for item in list_of_leaf_pairs %}
    resource "apstra_datacenter_device_allocation" "imap_assign_{{item.node1}}" {
      blueprint_id     = apstra_datacenter_blueprint.blueprint.id
      node_name        = "dual_{{item.node1}}_{{item.node2}}_001_leaf1"
      initial_interface_map_id = apstra_interface_map.IMAP_{{item.model}}.id
    }
    resource "apstra_datacenter_device_allocation" "imap_assign_{{item.node2}}" {
      blueprint_id     = apstra_datacenter_blueprint.blueprint.id
      node_name        = "dual_{{item.node1}}_{{item.node2}}_001_leaf2"
      initial_interface_map_id = apstra_interface_map.IMAP_{{item.model}}.id
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        logical_devices=logical_devices,
        aci_spine_nodes=aci_spine_nodes,
        list_of_single_leaf=list_of_single_leaf,
        list_of_leaf_pairs=list_of_leaf_pairs
    )
    return output


def generate_apstra_datacenter_generic_system_nb_config(generic_system_single, generic_system_pc, generic_system_esi, list_of_single_leaf, list_of_leaf_pairs,blueprint_name):
    template_str = """
    data "apstra_datacenter_blueprint" "blueprint" {
        name = "{{blueprint_name}}"
    }
    locals {
        {%- for item in list_of_single_leaf %}
        leaf_{{item.id}}_id = tolist(data.apstra_datacenter_systems.leaf_{{item.id}}.ids)
        {%- endfor %}
        {%- for item in list_of_leaf_pairs %}
        leaf_{{item.node1}}_id = tolist(data.apstra_datacenter_systems.leaf_{{item.node1}}.ids)
        leaf_{{item.node2}}_id = tolist(data.apstra_datacenter_systems.leaf_{{item.node2}}.ids)
        {%- endfor %}
    }
    {%- for item in list_of_single_leaf %}
    data "apstra_datacenter_systems" "leaf_{{item.id}}" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        filters = [
        {
            label = "single_{{item.id}}_001_leaf1"
        }
        ]
    }
    {%- endfor %}
    {%- for item in list_of_leaf_pairs %}
    data "apstra_datacenter_systems" "leaf_{{item.node1}}" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        filters = [
        {
            label = "dual_{{item.node1}}_{{item.node2}}_001_leaf1"
        }
        ]
    }
    data "apstra_datacenter_systems" "leaf_{{item.node2}}" {
        blueprint_id = data.apstra_datacenter_blueprint.blueprint.id
        filters = [
        {
            label = "dual_{{item.node1}}_{{item.node2}}_001_leaf2"
        }
        ]
    }
    {%- endfor %}
    {%- for key,value in generic_system_single.items() %}
    resource "apstra_datacenter_generic_system" "{{key}}" {
        blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
        name              = "{{key}}"
        hostname          = "generic.system"
        tags              = ["terraform", "{{key}}"]
        links = [
        {%- for port in value.node1_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            target_switch_id              = local.leaf_{{value.node1}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            },
        {%- endfor %}
        ]
    }
    {%- endfor %}
    {%- for key,value in generic_system_pc.items() %}
    resource "apstra_datacenter_generic_system" "{{key}}" {
        blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
        name              = "{{key}}"
        hostname          = "generic.system"
        tags              = ["terraform", "{{key}}"]
        links = [
        {%- for port in value.node1_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            lag_mode                      = "{{value.bundle_mode}}"  
            target_switch_id              = local.leaf_{{value.node1}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            group_label                   = "bond0"
            },
        {%- endfor %}
        ]
    }
    {%- endfor %}
    {%- for key,value in generic_system_esi.items() %}
    resource "apstra_datacenter_generic_system" "{{key}}" {
        blueprint_id      = data.apstra_datacenter_blueprint.blueprint.id
        name              = "{{key}}"
        hostname          = "generic.system"
        tags              = ["terraform", "{{key}}"]
        links = [
        {%- for port in value.node1_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            lag_mode                      = "{{value.bundle_mode}}"  
            target_switch_id              = local.leaf_{{value.node1}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            group_label                   = "bond0"
            },
        {%- endfor %}
        {%- for port in value.node2_ports %}
            {
            tags                          = {{value.vn_tag_list}}
            lag_mode                      = "{{value.bundle_mode}}"  
            target_switch_id              = local.leaf_{{value.node2}}_id[0]
            target_switch_if_name         = "{{port}}"
            target_switch_if_transform_id = 1
            group_label                   = "bond0"
            },
        {%- endfor %}
        ]
    }
    {%- endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(

        generic_system_single=generic_system_single,
        generic_system_pc=generic_system_pc,
        generic_system_esi=generic_system_esi,
        list_of_single_leaf=list_of_single_leaf,
        list_of_leaf_pairs=list_of_leaf_pairs,
        blueprint_name=blueprint_name

    )

    return output

def generate_apstra_resources_config(tep_pool):
    # Define the Jinja2 template as a string
    template_str = """
    resource "apstra_ipv4_pool" "tep_pool" {
      name = "tep_pool"
      subnets = [
        { network = "{{tep_pool}}" },
      ]
    }
    resource "apstra_asn_pool" "spines_asn_pool" {
        name = "spines_asn_pool"
        ranges = [ 
            {
                first = 65001
                last = 65100
            } 
        ]
    }
    resource "apstra_asn_pool" "leafs_asn_pool" {
        name = "leafs_asn_pool"
        ranges = [ 
            {
                first = 65101
                last = 65500
            } 
        ]
    }
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        tep_pool=tep_pool
    )
    return output

def generate_apstra_resources_assign_config():
    # Define the Jinja2 template as a string
    template_str = """
    resource "apstra_datacenter_resource_pool_allocation" "spines_asn_pool" {
      blueprint_id = apstra_datacenter_blueprint.blueprint.id
      role         = "spine_asns"
      pool_ids     = [apstra_asn_pool.spines_asn_pool.id]
    }
    resource "apstra_datacenter_resource_pool_allocation" "leafs_asn_pool" {
      blueprint_id = apstra_datacenter_blueprint.blueprint.id
      role         = "leaf_asns"
      pool_ids     = [apstra_asn_pool.leafs_asn_pool.id]
    }
    
    resource "apstra_datacenter_resource_pool_allocation" "spine_loopback" {
      blueprint_id = apstra_datacenter_blueprint.blueprint.id
      role         = "spine_loopback_ips"
      pool_ids     = [apstra_ipv4_pool.tep_pool.id]
    }
    resource "apstra_datacenter_resource_pool_allocation" "leaf_loopback" {
      blueprint_id = apstra_datacenter_blueprint.blueprint.id
      role         = "leaf_loopback_ips"
      pool_ids     = [apstra_ipv4_pool.tep_pool.id]
    }
    resource "apstra_datacenter_resource_pool_allocation" "spine_leaf_link_ips" {
      blueprint_id = apstra_datacenter_blueprint.blueprint.id
      role         = "spine_leaf_link_ips"
      pool_ids     = [apstra_ipv4_pool.tep_pool.id]
    }
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
    )
    return output
