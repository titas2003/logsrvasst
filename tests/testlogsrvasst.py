import pytest
from logsrvasst.logsrvasst import load_properties, get_property_name, extract_properties_and_constants, generate_template, show_property_descriptions

# Sample data for tests
properties = [
    {"code": "hostname", "name": "hostname", "description": "The hostname of the machine where the log message was originated."},
    {"code": "source", "name": "source", "description": "The IP address or hostname of the source of the log message."},
    # Add more sample data if needed
]

def test_load_properties():
    # Test if properties are loaded correctly
    assert load_properties('logsrvasst/properties.json') == properties

def test_get_property_name():
    # Test if property name is fetched correctly
    assert get_property_name('hostname', properties) == 'hostname'

def test_extract_properties_and_constants():
    # Test if properties and constants are extracted correctly
    path = '/var/log/src/hst-len/pme.log'
    expected = [
        'constant(value="/")',
        'constant(value="var")',
        'constant(value="/")',
        'constant(value="log")',
        'constant(value="/")',
        'property(name="source")',
        'constant(value="/")',
        'constant(value="hostname")',
        'constant(value="-")',
        'constant(value="line")',
        'constant(value="/")',
        'property(name="programname")',
        'constant(value=".log")'
    ]
    assert extract_properties_and_constants(path, properties) == expected

def test_generate_template():
    # Test if the template is generated correctly
    template_name = 'test'
    path = '/var/log/src/hst-len/pme.log'
    expected_template = (
        'template(name="test" type="list") {\n'
        '    constant(value="/")\n'
        '    constant(value="var")\n'
        '    constant(value="/")\n'
        '    constant(value="log")\n'
        '    constant(value="/")\n'
        '    property(name="source")\n'
        '    constant(value="/")\n'
        '    constant(value="hostname")\n'
        '    constant(value="-")\n'
        '    constant(value="line")\n'
        '    constant(value="/")\n'
        '    property(name="programname")\n'
        '    constant(value=".log")\n'
        '}'
    )
    assert generate_template(template_name, path, properties) == expected_template

def test_show_property_descriptions():
    # Test if property descriptions are shown correctly
    expected = [
        {"code": "hostname", "description": "The hostname of the machine where the log message was originated."},
        {"code": "source", "description": "The IP address or hostname of the source of the log message."},
        # Add more expected results if needed
    ]
    assert show_property_descriptions(properties) == expected
