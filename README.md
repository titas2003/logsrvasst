# Rsyslog Server Side Configuration Generator

## Overview

This Python script generates rsyslog server-side configuration templates and assists with managing SELinux and firewall rules. It can also display property codes and descriptions in JSON format. The script includes functions to generate configurations, handle ports and protocols, and translate file path codes into property names.

## Functions

### `logsrvasst(port, protocol)`

Generates an rsyslog server-side configuration file content based on the specified port and protocol.

**Parameters:**
- `port` (int): The port on which the rsyslog server will listen. Commonly, this is 514, but you can specify a different port.
- `protocol` (str): The protocol used by the server, either `'tcp'` or `'udp'`.

**Returns:**
- `str`: The rsyslog configuration content.

**Example:**

```python
config = logsrvasst(514, 'udp')
print(config)
```

### output
```plaintext

# rsyslog server configuration

# Load the necessary modules
module(load="imudp") 
input(type="imudp" port="514")
# End of configuration
```

`print_suggestions(port, protocol)`
Prints suggestions for managing SELinux and firewall rules if a non-default port is used.

Parameters:

port (int): The port that was used in the configuration.
protocol (str): The protocol used in the configuration.

```python
print_suggestions(1234, 'tcp')
```

```plaintext
Since you are using a non-default port, consider running the following commands to update SELinux and firewall rules:
# semanage port -a -t syslogd_port_t -p tcp 1234
# firewall-cmd --permanent --add-port=1234/tcp
# firewall-cmd --reload
```

`load_properties(file_path)`
Loads property codes and descriptions from a JSON file.

Parameters:

. `file_path` (str): The path to the JSON file containing property codes and descriptions.

Returns:
. `list`: A list of dictionaries, each representing a property with its code, name, and description.

```python
properties = load_properties('properties.json')
print(properties)
```
```json
[
    {"code": "hst", "name": "hostname", "description": "The hostname of the machine where the log message was originated."},
    {"code": "src", "name": "source", "description": "The IP address or hostname of the source of the log message."},
    ...
]
```

`get_property_name(code, properties)`
Retrieves the property name for a given code from the list of properties.

Parameters:

`code` (str): The short-form code for the property.
`properties` (list): The list of properties.

Returns:

`str`: The property name corresponding to the given `code`, or `None` if not found.

```python
property_name = get_property_name('hst', properties)
print(property_name)
```
#### Output example:
```plaintext
hostname
```
`extract_properties_and_constants(file_path, properties)`
Extracts properties and constants from the given file path. Codes are replaced with the corresponding property names.

Parameters:

`file_path` (str): The file path to be parsed.
`properties` (list): The list of properties.

Returns:
`list`: A list of template components, including `property` and `constant` entries.

```python
components = extract_properties_and_constants('/var/log/src/hst-len/pme.log', properties)
print(components)
```
#### Output Example:
```python
[
    'constant(value="/")',
    'constant(value="var")',
    'constant(value="/")',
    'constant(value="log")',
    'constant(value="/")',
    'property(name="source")',
    'constant(value="/")',
    'property(name="hostname")',
    'constant(value="/")',
    'property(name="programname")',
    'constant(value=".log")'
]
```

`generate_template(template_name, file_path, properties)`
Generates an rsyslog template based on the provided name and file path. The file path is parsed to replace codes with property names.

####  Parameters:

`template_name` (str): The name of the template.

`file_path` (str): The file path to be parsed.

p`roperties` (list): The list of `properties`

Returns:
`str`: The generated rsyslog `template` as a `string`.

```python
template = generate_template('test', '/var/log/src/hst-len/pme.log', properties)
print(template)
```

#### Output Example:
```plaintext
template(name="test" type="list") {
    constant(value="/")
    constant(value="var")
    constant(value="/")
    constant(value="log")
    constant(value="/")
    property(name="source")
    constant(value="/")
    property(name="hostname")
    constant(value="/")
    property(name="programname")
    constant(value=".log")
}
```

`show_property_descriptions(properties)`
Returns a JSON-formatted string with property codes and their descriptions.

#### Parameters:

`properties` (list): The list of properties.

Returns:
`str`: A JSON formatted string containing the property codes and descriptions.

##### Usage Example:
```python
descriptions_json = show_property_descriptions(properties)
print(descriptions_json)
```
#### Output Example:
```json
[
    {
        "code": "hst",
        "description": "The hostname of the machine where the log message was originated."
    },
    {
        "code": "src",
        "description": "The IP address or hostname of the source of the log message."
    },
    ...
]
```

### Usage
1. Ensure that you have `Python 3.x` installed.
2. Create a `properties.json` file with the required property codes and descriptions in the same directory as the script.
3. Run the script using Python.

```python
import logsrvasst as asst
# Load properties from JSON file
port = input("Enter port number:")
protocol = input("Enter protocol")
print(asst.logsrvasst(port,protocol))
if(port != 514):
    asst.print_suggestions(port,protocol)
json_file_path = 'properties.json'
properties = asst.load_properties(json_file_path)
    
# Show property descriptions
property_descriptions_json = asst.show_property_descriptions(properties)
print("\nProperty descriptions in JSON format:")
# print(property_descriptions_json)
    
# User input
template_name = input("Enter the template name: ")
file_path = input("Enter the file path: ")

# Generate the rsyslog template
rsyslog_template = asst.generate_template(template_name, file_path, properties)
    
# Print the generated template
print("\nGenerated rsyslog template:")
print(rsyslog_template)
```

#### THANK YOU