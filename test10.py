import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Dict, Any

# Sample YAML schema and data

# Parse the YAML schema and data
# parsed_schema = yaml.safe_load(yaml_schema)
parsed_schema = 'data/model.yaml'  # Your model schema YAML file

with open(parsed_schema, 'r') as file:
    schema_data = yaml.safe_load(file)

print(schema_data)
parsed_schema = schema_data


parsed_data = 'data/data.yaml'    # Your data YAML file

with open(parsed_data, 'r') as file:
        data = yaml.safe_load(file)

print(data)
parsed_data = data
# parsed_data = yaml.safe_load(yaml_data)

############################################################################

# Function to dynamically create a Pydantic model from the schema
def create_pydantic_model(class_name: str, fields: List[Dict[str, Any]], relationships: List[Dict[str, Any]] = None, valid_class_ids: List[int] = None):
    # Prepare the field annotations dictionary for the class
    annotations = {}
    
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

    # Dynamically create the model class
    class_dict = {'__annotations__': annotations, '__module__': __name__}
    
    # Add a field validator for the Tutor model (validate class_id in Class field)
    if class_name == 'Tutor' and valid_class_ids is not None:
        @field_validator('Class')
        def validate_class_ids(cls, v):
            invalid_ids = [cid for cid in v if cid not in valid_class_ids]
            if invalid_ids:
                raise ValueError(f"Invalid class_id(s): {invalid_ids}")
            return v
        class_dict['validate_class_ids'] = validate_class_ids

    # Create the model class
    model = type(class_name, (BaseModel,), class_dict)
    return model

# Step 1: Parse the schema to get the class names, attributes, and relationships
models = {}
valid_class_ids = []

# Create the Class model first, so we can extract the valid class_ids
for class_schema in parsed_schema:
    if isinstance(class_schema, dict):
        class_name = class_schema["name"]
        fields = class_schema.get("fields", [])
        relationships = class_schema.get("relationships", [])
        
        # Step 2: Dynamically create a Pydantic model for each class
        if class_name == "Class":
            ClassModel = create_pydantic_model(class_name, fields, relationships)
            models[class_name] = ClassModel
            
            # Extract valid class_ids from the class instances
            class_instances = parsed_data.get("Class", [])
            valid_class_ids = [item["class_id"] for item in class_instances]
            instances = [ClassModel(**item) for item in class_instances]
        else:
            models[class_name] = create_pydantic_model(class_name, fields, relationships, valid_class_ids)

# Step 3: Instantiate the dynamic models using the parsed data
instances = {}
for class_name, class_data in parsed_data.items():
    ModelClass = models[class_name]
    try:
        instances[class_name] = [ModelClass(**item) for item in class_data]
    except ValidationError as e:
        print(f"Validation failed for {class_name}:\n", e)

# Print the created instances
for class_name, class_instances in instances.items():
    print(f"Instances for {class_name}:")
    for instance in class_instances:
        print(instance)
