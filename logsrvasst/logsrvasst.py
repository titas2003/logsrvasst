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


# rulesets


def create_rsyslog_ruleset(ruleset_name, template_name, port, protocol, facilities_severities):
    """
    Create an rsyslog configuration string based on the provided ruleset name, template name, port, protocol, and facilities/severities.
    
    Args:
        ruleset_name (str): The name of the ruleset.
        template_name (str): The name of the template to use in the ruleset.
        port (int): The port number to listen on.
        protocol (str): The protocol to use (e.g., 'imtcp' for TCP, 'imudp' for UDP).
        facilities_severities (str): A comma-separated list of facility.severity pairs.

    Returns:
        str: The generated rsyslog configuration.
    """
    config_lines = []

    # Add module loading based on protocol
    if protocol == 'tcp':
        config_lines.append('module(load="imtcp")\n')
    elif protocol == 'udp':
        config_lines.append('module(load="imudp")\n')
    else:
        raise ValueError("Unsupported protocol. Use 'imtcp' or 'imudp'.")

    # Process each facility.severity pair and aggregate them
    facilities_severities_list = [fs.strip() for fs in facilities_severities.split(',') if fs.strip()]
    facilities_severities_combined = ";".join(facilities_severities_list)
    
    # Add ruleset configuration
    config_lines.append(f'ruleset(name="{ruleset_name}"){{')
    config_lines.append(f'    {facilities_severities_combined} action(type="omfile" DynaFile="{template_name}")')
    config_lines.append('}\n')

    # Add input configuration
    config_lines.append(f'input(type="im{protocol}" port="{port}" ruleset="{ruleset_name}")\n')

    return "\n".join(config_lines)


# ruleset to accept TLS encrypted logs

def create_tls_rsyslog_ruleset(ruleset_name, template_name, port, tls_ca, tls_cert, tls_key, facilities_severities):
    """
    Create an rsyslog configuration string for TLS-encrypted logs in RainerScript format.
    
    Args:
        ruleset_name (str): The name of the ruleset.
        template_name (str): The name of the template to use in the ruleset.
        port (int): The port number to listen on.
        tls_cert (str): Path to the TLS certificate file.
        tls_key (str): Path to the TLS private key file.
        facilities_severities (str): A comma-separated list of facility.severity pairs.

    Returns:
        str: The generated rsyslog configuration in RainerScript format.
    """
    config_lines = []

    # Global TLS settings
    config_lines.append('global(')
    config_lines.append(f'    DefaultNetstreamDriver="gtls"')
    config_lines.append(f'    DefaultNetstreamDriverCAFile="{tls_ca}"')
    config_lines.append(f'    DefaultNetstreamDriverCertFile="{tls_cert}"')
    config_lines.append(f'    DefaultNetstreamDriverKeyFile="{tls_key}"')
    config_lines.append(')\n')

    # Load TCP listener module with TLS settings
    config_lines.append('# load TCP listener')
    config_lines.append('module(')
    config_lines.append(f'    load="imtcp"')
    config_lines.append(f'    StreamDriver.Name="gtls"')
    config_lines.append(f'    StreamDriver.Mode="1"')
    config_lines.append(f'    StreamDriver.Authmode="anon"')
    config_lines.append(')\n')

    # Input configuration
    config_lines.append(f'# start up listener at port {port}')
    config_lines.append('input(')
    config_lines.append(f'    type="imtcp"')
    config_lines.append(f'    port="{port}"')
    config_lines.append(')\n')

    # Ruleset configuration
    config_lines.append(f'ruleset(name="{ruleset_name}") {{')
    config_lines.append(f'    {facilities_severities} action(type="omfile" DynaFile="{template_name}")')
    config_lines.append('}\n')

    return "\n".join(config_lines)

# def main():
#     print(create_tls_rsyslog_ruleset("Test_Rule","Test_template",514,"/etc/CA.pem","/etc/tls.pem","/etc/tls.key","local3.info,local4.*"))
    
# if __name__ == "__main__":
#     main()