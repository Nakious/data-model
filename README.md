For Wayne...

This is the first commit of some semi working example scripts, there is much to do!

The overall aim is to demonstrate:
- Loading a dynamic class model from yaml into RAM
  - Class model must be able to version classes with different attributes on different versions
  - Class model must be able to define relationships and if they are mandatory or not
- Export visual representation of that model
- Load data into the model and vallidate correctness of data, mandatory relationships must exist, invalid objects (lacking mandatory atributes) fail to import etc.
- Visualise the loaded data
- Store imported data in DB (sqlite for example) with a version/date so that each successive run/import can produce a diff from the current "baseline"

## TODO

Everything