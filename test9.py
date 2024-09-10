import yaml
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any

# Sample YAML schema and data
yaml_schema = """
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
    - schema: one_to_many  # A Tutor can be related to many Classes
      target: Class        # The related model is 'Class'
      attribute: Class     # This refers to a field in Tutor that holds class IDs
      type: List[int]      # The type is a list of integers, representing class IDs
      reference_field: class_id  # Explicitly specifying the reference field in the target model.
"""

yaml_data = """
Class:
  - version: 1
    name: Class 1
    class_id: 1
  - version: 1
    name: Class 2
    class_id: 2
Tutor:
  - version: 1
    name: Tutor 1
    employee_id: 1
    Class:
      - 1
  - version: 1
    name: Tutor 2
    employee_id: 2
    Class:
      - 2
      - 1
"""

# Parse the YAML schema and data
parsed_schema = yaml.safe_load(yaml_schema)
parsed_data = yaml.safe_load(yaml_data)

# Function to dynamically create a Pydantic model from the schema
def create_pydantic_model(class_name: str, fields: List[Dict[str, Any]], relationships: List[Dict[str, Any]] = None):
    # Prepare the field annotations dictionary for the class
    annotations = {}
    default_values = {}
    
    # Handle fields in the schema
    for field in fields:
        field_name = field["name"]
        field_type = eval(field["type"])  # Convert the string 'int'/'str' into actual Python types
        annotations[field_name] = field_type
    
    # Handle relationships (e.g., one-to-many, many-to-one)
    if relationships:
        for relationship in relationships:
            relationship_attr = relationship["attribute"]
            relationship_type = eval(relationship["type"])
            annotations[relationship_attr] = relationship_type

    # Create a class with dynamic annotations and inherit from BaseModel
    model = type(class_name, (BaseModel,), {'__annotations__': annotations, '__module__': __name__})
    return model

# Step 1: Parse the schema to get the class names, attributes, and relationships
models = {}
for class_schema in parsed_schema:
    class_name = class_schema["name"]
    fields = class_schema.get("fields", [])
    relationships = class_schema.get("relationships", [])
    
    # Step 2: Dynamically create a Pydantic model for each class
    DynamicModel = create_pydantic_model(class_name, fields, relationships)
    
    # Save the model for future reference (e.g., when resolving relationships)
    models[class_name] = DynamicModel

# Step 3: Instantiate the dynamic models using the parsed data
instances = {}
for class_name, class_data in parsed_data.items():
    ModelClass = models[class_name]
    instances[class_name] = [ModelClass(**item) for item in class_data]

# Print the created instances
for class_name, class_instances in instances.items():
    print(f"Instances for {class_name}:")
    for instance in class_instances:
        print(instance)
