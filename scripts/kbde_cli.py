#!/usr/bin/env python3


from kbde import kbde_cli

cli = kbde_cli.KbdeCli()
cli.run()

exit()

# Try to import all modules in kbde and look for a scripts.py

for module_info in modules:
    print(module_info)

    # Import that module


    # Get the submodules for this module
    
    # Check the module for a "scripts" submodule

    print("    ", submodule_info)
    # Import scripts module
    scripts_module = importlib.import_module(f"kbde.{module_info.name}.scripts")

    for name, obj in inspect.getmembers(scripts_module):
        
        if inspect.isclass(obj) and isinstance(obj, kbde_cli.Command):
            print(name, obj)
