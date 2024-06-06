from jinja2 import Template

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
