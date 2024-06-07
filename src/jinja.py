from jinja2 import Template

def generate_apstra_datacenter_routing_zone_config(vrf_list, blueprint_id):
    # Define the Jinja2 template as a string
    template_str = """
    {% for vrf in vrf_list %}
    resource "apstra_datacenter_routing_zone" "{{ vrf.apstra_vrf }}_rz" {
      name              = "{{ vrf.apstra_vrf }}"
      blueprint_id      = "{{ blueprint_id }}"
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


def generate_apstra_datacenter_virtual_network_config(data, blueprint_id):
    # Define the Jinja2 template as a string
    template_str = """
    {% for item in data %}
    resource "apstra_datacenter_virtual_network" "{{ item.vn_name }}" {
      name                         = "{{ item.vn_name }}"
      blueprint_id                 = "{{ blueprint_id }}"
      type                         = "vxlan"
      routing_zone_id              = "routing-zone-id"
      ipv4_connectivity_enabled    = {{ item.vn_unicastRoute }}
      ipv4_virtual_gateway_enabled = {{ item.vn_unicastRoute }}
      {% for sub_item in item.children %}
      ipv4_virtual_gateway         = "{{sub_item.apstra_ip}}"
      ipv4_subnet                  = "{{sub_item.apstra_network}}"
      {% endfor %}
      bindings = {
        "EBolN4LZ57ESEKtZwJk" = {
          "access_ids" = []
        },
        "nBuYdW7gDGtvhZ9KY2w" = {
          "access_ids" = []
        }
      }
    }
    {% endfor %}
    """

    # Load the template from the string
    template = Template(template_str)

    # Render the template with variables
    output = template.render(
        blueprint_id=blueprint_id,
        data=data
    )

    return output


        # # {% if item.apstra_ip is defined %}
         # # {% endif %}