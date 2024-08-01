import json
import re

def logsrvasst(port, protocol):
    """
    Generate an rsyslog server-side configuration file content.
    
    Args:
    - port (int): The port on which the rsyslog server will listen.
    - protocol (str): The protocol used by the server, either 'tcp' or 'udp'.
    
    Returns:
    - str: The rsyslog configuration content.
    """
    if protocol not in ['tcp', 'udp']:
        raise ValueError("Protocol must be either 'tcp' or 'udp'.")
    
    # Configuration template
    config_template = f"""
# rsyslog server configuration

# Load the necessary modules
module(load="im{protocol}") 
input(type="im{protocol}" port="{port}")
# End of configuration
"""
    
    return config_template.strip()

def print_suggestions(port, protocol):
    """
    Print suggestions for managing SELinux and firewall rules if the port is not the default.
    
    Args:
    - port (int): The port that was used in the configuration.
    - protocol (str): The protocol used in the configuration.
    """
    if port != 514:
        print("\nSince you are using a non-default port, consider running the following commands to update SELinux and firewall rules:")
        print(f"# semanage port -a -t syslogd_port_t -p {protocol} {port}")
        print(f"# firewall-cmd --permanent --add-port={port}/{protocol}")
        print("# firewall-cmd --reload")

def load_properties(file_path):
    """Load properties from a JSON file."""
    with open(file_path, 'r') as file:
        properties = json.load(file)
    return properties

def get_property_name(code, properties):
    """Get the property name for a given code."""
    for prop in properties:
        if prop['code'] == code:
            return prop['name']
    return None

def extract_properties_and_constants(file_path, properties):
    """Extract properties and constants from the given file path."""
    # Split the file path by delimiters (/,-,_,.)
    path_parts = re.split(r'([/._-])', file_path)
    
    # Create a list to hold template components
    template_components = []
    
    # Determine if a part is a constant or property
    for part in path_parts:
        part = part.strip()
        if part:
            # Replace short-form codes with property names
            property_name = get_property_name(part, properties)
            if property_name:
                template_components.append(f'property(name="{property_name}")')
            else:
                # It's a constant if it doesn't match any property code
                template_components.append(f'constant(value="{part}")')
    
    return template_components

def generate_template(template_name, file_path, properties):
    """Generate the rsyslog template based on the given name and file path."""
    components = extract_properties_and_constants(file_path, properties)
    # Construct the template
    template = f'template(name="{template_name}" type="list") {{\n    ' + '\n    '.join(components) + '\n}'
    return template

def show_property_descriptions(properties):
    """Return the code and description of all properties as JSON data."""
    # Prepare the data
    data = [{'code': prop['code'], 'description': prop['description']} for prop in properties]
    # Convert to JSON
    return json.dumps(data, indent=4)


