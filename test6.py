from pydantic import BaseModel, create_model, Field, field_validator
from typing import Optional, List, get_args
from graphviz import Digraph
import yaml
from icecream import ic




# Shared store to keep track of valid class IDs for validation purposes
class ValidIDStore:

    """
    ValidIDStore is a singleton class that serves as a central place to store valid class_ids and check their existence during validation. The goal is to ensure that the class_ids in the Tutor and Student models are valid and exist in the store.

    Here’s how the ValidIDStore is structured:

    Singleton Pattern: It ensures that only one instance of ValidIDStore exists. This is useful for keeping a global reference to valid class_ids across different models.

    Methods:
        add_class(class_id, class_instance): Adds a class_id and its instance to the store.
        check_class(class_id): Checks if a class_id exists in the store. If it doesn’t exist, it raises an error.
    """

    _instance = None
    valid_class_ids = set()

    @staticmethod
    def get_instance():
        if ValidIDStore._instance is None:
            ValidIDStore._instance = ValidIDStore()
        return ValidIDStore._instance

    @classmethod
    def add_class(cls, class_id, class_instance):
        cls.get_instance().valid_class_ids.add(class_id)
        print(cls.get_instance().valid_class_ids)
        #cls.get_instance().valid_class_ids[class_id] = class_instance

    @classmethod
    def check_class(cls, class_id):
        if class_id not in cls.get_instance().valid_class_ids:
            raise ValueError(f"Invalid class_id: {class_id}")
        return class_id


def generate_pydantic_classes_with_validation(yaml_file):
    with open(yaml_file, 'r') as file:
        model_data = yaml.safe_load(file)

    classes = {}

    for item in model_data:
        fields = {}
        relationships = {}
        class_name = item['name']

        # Define fields
        fields = {
            field['name']: (field['type'], None) if field['type'].startswith('Optional') else (field['type'], ...) 
                for field in item['fields']
        }

        # Define relationships (optional)
        if 'relationships' in item:
            relationships = {
                relationship['attribute']: (List[classes[relationship['target']]], ...)
                if relationship['schema'] == 'many_to_many' else (classes[relationship['target']], ...)
                for relationship in item['relationships']
            }

        # Combine fields and relationships
        fields.update(relationships)
        ic(fields)

        # Create the dynamic model
        dynamic_class = create_model(class_name, **fields)
        ic(dynamic_class)
        ic(dynamic_class.model_fields.keys())


        """
        When you create models dynamically using pydantic.create_model, you need to attach validators to fields that reference class_ids. 
        These validators ensure that the class_id exists in ValidIDStore before accepting the data.

        @field_validator('Class', mode='before')
        The @field_validator decorator is a Pydantic decorator that defines a validator for a specific field in a Pydantic model.

            Field being validated: 'Class' refers to the name of the field being validated.
            mode='before': This means that the validation occurs before the field is set on the model. It's often used to modify or validate incoming data before it is processed or assigned to the model field.
        
        This means that the function validate_class_ids will be called before Pydantic assigns any values to the 'Class' field during the creation of the object.

        """

        # Add custom validator for Class field in Tutor and Student
        if 'Class' in fields:
            # Validator for 'Class' field
            @field_validator('Class', mode='before')
            def validate_class_ids(cls, v: list):
                # Validate that each class ID exists in ValidIDStore
                if isinstance(v, list):
                    for class_id in v:
                        ValidIDStore.check_class(class_id)  # Call to ValidIDStore
                return v

            setattr(dynamic_class, 'validate_class_ids', validate_class_ids) # The validate_class_ids function is attached to the dynamic model via setattr(dynamic_class, 'validate_class_ids', validate_class_ids). This ensures that the validation is triggered for the Class field during model instantiation.
            #Trigger Validation During Instantiation: When you create an instance of this dynamic class, Pydantic will automatically call the validator, so the code inside validate_class_ids will run.

        classes[class_name] = dynamic_class

        ic(classes[class_name])
        ic(classes[class_name].model_fields.keys())

    return classes


def generate_graphviz_schema(model_classes):
    """
    Generates a Graphviz representation of the model schema.
    """
    dot = Digraph()

    for _, cls in model_classes.items():
        # print(cls.__name__)
        dot.node(cls.__name__, cls.__name__)

    for _, cls in model_classes.items():
        for field_name, field_info in cls.__fields__.items():
            if  (field_type := get_args(field_info.annotation)):
                field_type = get_args(field_info.annotation)[0]
                # print(get_args(field_info.annotation)[0])
            else:
                field_type = field_info.annotation
                # print(field_info.annotation)
            if issubclass(field_type, BaseModel):
                # print(cls.__name__ + " : ", field_name)
                dot.edge(cls.__name__, field_type.__name__, label=field_name)

    dot.render('output/test5', format='png', cleanup=True)



def load_and_validate_data(yaml_file, generated_classes):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)
    
    ic(data)

    objects = {}
    for class_name, items in data.items():
        class_type = generated_classes[class_name]

        # Validate each item in the data list against the generated Pydantic model
        validated_items = []
        for item in items:
            # Attempt to instantiate the class, this will trigger the validation (including class_id check)
            try:
                #are_all_class_ids_valid = all(class_id in ValidIDStore['valid_class_ids'] for class_id in tutor_class_list)
                validated_item = class_type(**item)
                validated_items.append(validated_item)
            except ValueError as e:
                print(f"Validation error in {class_name} data: {e}")
        
        # Store validated data
        objects[class_name] = validated_items

    return objects


# Load classes first so we can store them in ValidIDStore
def load_classes(yaml_file, generated_classes):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    for class_data in data.get('Class', []):
        class_instance = generated_classes['Class'](**class_data)
        ValidIDStore.add_class(class_instance.class_id, class_instance)

# Example usage
model_yaml_file = 'data/model.yaml'  # Your model schema YAML file
data_yaml_file = 'data/data.yaml'    # Your data YAML file

# Step 1: Generate classes with validation rules
generated_classes = generate_pydantic_classes_with_validation(model_yaml_file)

# Load the classes first and store them in ValidIDStore
load_classes(data_yaml_file, generated_classes)
ic(ValidIDStore.valid_class_ids)

# Step 2: Generate a graph representation of the model schema (optional)
generate_graphviz_schema(generated_classes)

# Step 3: Load and validate data
validated_data = load_and_validate_data(data_yaml_file, generated_classes)

# Print out validated data
for class_name, instances in validated_data.items():
    print(f"\nClass: {class_name}")
    for instance in instances:
        print(instance)
