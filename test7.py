import yaml
from typing import List, Any

# Step 1: Function to create fields with default values based on type
def create_field(attribute_name, attribute_type):
    field_types = {
        'int': 0,
        'str': '',
        'List[int]': []
    }
    # Handle custom types like List[int]
    if 'List' in attribute_type:
        return list
    return field_types.get(attribute_type, None)

# Step 2: Dynamically create a class with fields and relationships
def create_class_from_yaml(class_name, fields, relationships=None):
    class_attributes = {}
    
    # Create attributes for fields
    for field in fields:
        attr_name = field['name']
        attr_type = field['type']
        class_attributes[attr_name] = create_field(attr_name, attr_type)
    
    # Create attributes for relationships
    if relationships:
        for relationship in relationships:
            relationship_type = relationship['type']
            attribute_name = relationship['attribute']
            class_attributes[attribute_name] = create_field(attribute_name, relationship_type)
    
    # Define the `__init__` method dynamically
    def init(self, **kwargs):
        for attr, default_value in class_attributes.items():
            setattr(self, attr, kwargs.get(attr, default_value))
    
    # Return the class dynamically using type()
    return type(class_name, (object,), {'__init__': init})

# Step 3: Function to instantiate objects from test data
def instantiate_objects(class_map, model_name, instances_data):
    instances = []
    cls = class_map.get(model_name)
    
    for data in instances_data:
        # Create an instance with the provided data
        instance = cls(**data)
        instances.append(instance)
    
    return instances

# Step 4: Main function to create classes, instantiate them, and handle relationships
def main(yaml_model, test_data):
    dynamic_classes = {}
    
    # Step 4.1: Create dynamic classes from the YAML model
    for model in yaml_model:
        class_name = model['name']
        fields = model.get('fields', [])
        relationships = model.get('relationships', [])
        
        # Dynamically create the class
        dynamic_class = create_class_from_yaml(class_name, fields, relationships)
        dynamic_classes[class_name] = dynamic_class
        
    # Step 4.2: Instantiate objects from test data
    instantiated_objects = {}
    
    for model_name, instances_data in test_data.items():
        instances = instantiate_objects(dynamic_classes, model_name, instances_data)
        instantiated_objects[model_name] = instances
    
    # Step 4.3: Resolve relationships (e.g., for Tutor and Student to Class)
    class_instances = {inst.class_id: inst for inst in instantiated_objects.get('Class', [])}
    
    for tutor in instantiated_objects.get('Tutor', []):
        tutor.Class = [class_instances[class_id] for class_id in tutor.Class]
    
    for student in instantiated_objects.get('Student', []):
        student.Class = [class_instances[class_id] for class_id in student.Class]
    
    return instantiated_objects

# Example YAML model
yaml_model = """
- name: Class
  fields:
    - name: version
      type: int
    - name: name
      type: str
    - name: class_id
      type: int

- name: Tutor
  fields:
    - name: version
      type: int
    - name: name
      type: str
    - name: employee_id
      type: int
  relationships:
    - schema: one_to_many
      target: Class
      attribute: Class
      type: List[int]
      reference_field: class_id

- name: Student
  fields:
    - name: version
      type: int  
    - name: name
      type: str
    - name: student_id
      type: int
  relationships:
    - schema: many_to_many
      target: Class
      attribute: Class
      type: List[int]
      reference_field: class_id
"""

# Example test data
test_data = {
    'Class': [
        {'version': 1, 'name': 'Class 1', 'class_id': 1},
        {'version': 1, 'name': 'Class 2', 'class_id': 2}
    ],
    'Tutor': [
        {'version': 1, 'name': 'Tutor 1', 'employee_id': 1, 'Class': [1]},
        {'version': 1, 'name': 'Tutor 2', 'employee_id': 2, 'Class': [2, 1]}
    ],
    'Student': [
        {'version': 1, 'name': 'Pupil 1', 'student_id': 1, 'Class': [1]},
        {'version': 1, 'name': 'Pupil 2', 'student_id': 2, 'Class': [2]},
        {'version': 1, 'name': 'Pupil 3', 'student_id': 3, 'Class': [1, 2]},
        {'version': 1, 'name': 'Pupil 4', 'student_id': 4, 'Class': [2]},
        {'version': 1, 'name': 'Pupil 5', 'student_id': 5, 'Class': [2]}
    ]
}

# Instead of reading from a file, I'll directly parse the YAML model string
yaml_model_content = yaml.safe_load(yaml_model)

# Run the main function to create classes and instantiate objects based on test data
instantiated_objects = main(yaml_model_content, test_data)

# Printing the results to verify the objects and their relationships
for class_type, instances in instantiated_objects.items():
    print(f"--- {class_type} instances ---")
    for instance in instances:
        print(f"{class_type}: {vars(instance)}")
