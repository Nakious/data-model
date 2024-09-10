import yaml
from pydantic import BaseModel
from typing import Dict, Any

# Sample YAML schema and data
yaml_schema = """
- name: Class
  type: str
  fields:
    - name: version
      type: int
    - name: name
      type: str
    - name: class_id
      type: int
"""

yaml_data = """
Class:
  - version: 1
    name: Class 1
    class_id: 1
  - version: 1
    name: Class 2
    class_id: 2
"""

# Parse the YAML schema and data
parsed_schema = yaml.safe_load(yaml_schema)
parsed_data = yaml.safe_load(yaml_data)

# Function to dynamically create a Pydantic model from the schema
def create_pydantic_model(class_name: str, fields: Dict[str, Any]):
    # Prepare the field annotations dictionary for the class
    annotations = {}
    for field in fields:
        field_name = field["name"]
        field_type = eval(field["type"])  # Convert the string 'int'/'str' into actual Python types
        annotations[field_name] = field_type
    
    # Create a class with dynamic annotations and inherit from BaseModel
    model = type(class_name, (BaseModel,), {'__annotations__': annotations, '__module__': __name__})
    return model

# Step 1: Parse the schema to get the class names and attributes
for class_schema in parsed_schema:
    class_name = class_schema["name"]
    fields = class_schema["fields"]
    
    # Step 2: Dynamically create a Pydantic model
    DynamicModel = create_pydantic_model(class_name, fields)
    
    # Step 3: Instantiate the dynamic model using the parsed data
    class_data = parsed_data[class_name]
    instances = [DynamicModel(**item) for item in class_data]
    
    # Print the created instances
    for instance in instances:
        print(instance)
