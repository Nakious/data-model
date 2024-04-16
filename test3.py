import yaml
from graphviz import Digraph
import sqlite3

class Relationship:
    def __init__(self, type_, target, attribute):
        self.type = type_
        self.target = target
        self.attribute = attribute

def create_class(class_name, version_attributes, relationships):
    """
    Dynamically creates a class with the given name and attributes for each version,
    and handles relationships.
    """
    print(class_name)
    print(version_attributes)
    print(relationships)
    class_dict = {}
    for version_data in version_attributes:
        version = version_data['version']
        attributes = version_data['attributes']
        init_method = create_init_method(attributes)
        class_dict[version] = type(f"{class_name}_v{version}", (object,), {'__init__': init_method})

    for relationship_data in relationships:
        target = relationship_data['target']
        attribute = relationship_data['attribute']
        for version, class_ in class_dict.items():
            if class_name in target:  # Check if the target class matches the current class being processed
                class_.__dict__[attribute] = Relationship(relationship_data['type'], target, attribute)

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
        relationships = []
        for version_data in version_attributes:
            if 'relationships' in version_data:
                relationships.extend(version_data['relationships'])
        model_classes[class_name] = create_class(class_name, version_attributes, relationships)

    return model_classes



model_classes = load_model_from_yaml("data/test3_model.yaml")


def generate_graphviz_schema(model_classes):
    """
    Generates a Graphviz representation of the model schema.
    """
    dot = Digraph()

    for class_name, version_classes in model_classes.items():
        for version, class_ in version_classes.items():
            dot.node(f"{class_name}_v{version}", label=f"{class_name} (version {version})")
            if hasattr(class_, '__dict__'):
                relationships = class_.__dict__
                for relationship in relationships.values():
                    if isinstance(relationship, Relationship):
                        dot.edge(f"{class_name}_v{version}", f"{relationship.target}_v{version}", label=relationship.attribute)

    dot.render('output/test3', format='png', cleanup=True)



generate_graphviz_schema(model_classes)




# Test the dynamically created classes
Pupil = model_classes['Pupil']
Tutor = model_classes['Tutor']
Class = model_classes['Class']

    
# person1 = Person(name='John', age=30, gender='Male')
# address1 = Address(street='123 Main St', city='New York', country='USA')

# print(person1.name, person1.age, person1.gender)
# print(address1.street, address1.city, address1.country)




def load_data_from_yaml(file_path):
    """
    Loads data from YAML file.
    """
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    person_phone_numbers = {}  # Store phone numbers already linked to persons
    for class_name, versions in data.items():
        for instance_data in versions:
            version = instance_data.pop('version')
            if class_name == 'Person':
                if 'phone_numbers' in instance_data:
                    for phone_data in instance_data['phone_numbers']:
                        phone_number = phone_data['number']
                        if phone_number in person_phone_numbers:
                            raise ValueError(f"Phone number '{phone_number}' is already linked to another person.")
                        person_phone_numbers[phone_number] = instance_data['name']

            # Insert logic to process other classes as needed

    return data



# Connect to SQLite database
# Plan is to save data here so that it is possible to do a diff each time a successive data.yaml is read in
# Ultimately this needs to allow versioning tags etc. to baseline the environment(s)

conn = sqlite3.connect("output/test3_data.db")
cursor = conn.cursor()

# Create SQLite tables based on model classes
#for class_name, version_classes in model_classes.items():
#    for version, class_ in version_classes.items():
#        create_table(cursor, f"{class_name}_v{version}", class_.__dict__.keys())

#    # Load data from YAML file and update or insert into the database
#    with open("data.yaml", 'r') as file:
#        yaml_data = yaml.safe_load(file)

#    for class_name, versions in yaml_data.items():
#        for instance_data in versions:
#            version = instance_data.pop('version')
#            update_or_insert_data(cursor, f"{class_name}_v{version}", **instance_data)

#    # Load data from the database
#    for class_name, version_classes in model_classes.items():
#        for version, class_ in version_classes.items():
#            instances = load_data_from_db(cursor, f"{class_name}_v{version}")
#            print(f"{class_name} (version {version}) instances:")
#            for instance in instances:
#                print(instance.__dict__)

# Commit changes and close connection
conn.commit()
conn.close()