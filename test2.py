import yaml
from graphviz import Digraph

class Relationship:
    def __init__(self, type_, target, attribute):
        self.type = type_
        self.target = target
        self.attribute = attribute

def create_class(class_name, version_attributes):
    """
    Dynamically creates a class with the given name and attributes for each version,
    and handles relationships.
    """
    class_dict = {}
    for version_data in version_attributes:
        version = version_data['version']
        attributes = version_data['attributes']
        relationships = version_data['relationships']
        init_method = create_init_method(attributes)
        class_dict[version] = type(f"{class_name}_v{version}", (object,), {'__init__': init_method, 'relationships': relationships})

    return class_dict

def create_init_method(attributes):
    """
    Creates an __init__ method for a class with provided attributes.
    """
    def init_method(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    return init_method

def load_model_from_yaml(file_path):
    """
    Loads the YAML data and creates classes dynamically.
    """
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    model_classes = {}
    for class_name, version_attributes in data.items():
        model_classes[class_name] = create_class(class_name, version_attributes)

    return model_classes

def generate_graphviz_schema(model_classes):
    """
    Generates a Graphviz representation of the model schema.
    """
    dot = Digraph()

    for class_name, version_classes in model_classes.items():
        for version, class_ in version_classes.items():
            dot.node(f"{class_name}_v{version}", label=f"{class_name} (version {version})")
            relationships = class_.relationships
            for relationship in relationships:
                print(relationship)
                target_class_name = relationship['target']
                target_version = relationship['target_version']
                dot.edge(f"{class_name}_v{version}", f"{target_class_name}_v{target_version}", label=relationship['attribute'])


            #if hasattr(class_, 'relationships'):
            #    relationships = class_.relationships
            #    for relationship in relationships:
            #        dot.edge(f"{class_name}_v{version}", f"{relationship['target']}_v{relationship['version']}", label=relationship['attribute'])

    dot.render('output/test2', format='png', cleanup=True)

# Load data model from YAML file
model_classes = load_model_from_yaml('data/test2.yaml')

# Generate Graphviz schema
generate_graphviz_schema(model_classes)