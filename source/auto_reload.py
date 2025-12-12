import ast
import importlib
import os
import sys
import types
from typing import List


def reload_recursively_from(name: str):
    def recursive_reload(module: types.ModuleType, current_stack: List[str]):
        indent = "  " * (len(current_stack) + 1)
        print(f"{indent}Reloading module: {module.__name__}")

        dependencies = get_dependency_names(module)
        print(f"{indent}Found dependencies: {dependencies}")

        # Reload imported modules first
        for import_name in dependencies:
            if not import_name.startswith(f"{name}."):
                continue

            if import_name in current_stack:
                print("Skipping to avoid circular dependency:", current_stack + [module.__name__])
                continue

            try:
                dep_module = importlib.import_module(import_name)
                recursive_reload(dep_module, current_stack + [module.__name__])
            except ModuleNotFoundError:
                print(f"WARNING: Module not found for import: {import_name}")

        # Finally, reload the module
        importlib.reload(module)

    print(f"Reloading all modules with prefix: '{name}'")
    entry = sys.modules[name]
    recursive_reload(entry, [])


def get_imports_from_source(module: types.ModuleType):
    path = module.__file__
    if not path or not path.endswith(".py") or not os.path.exists(path):
        return []

    with open(path, "r") as f:
        tree = ast.parse(f.read(), filename=path)

    imports = []

    is_package = hasattr(module, "__path__")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # Example: import submodule
            for n in node.names:
                imports.append(n.name)

        elif isinstance(node, ast.ImportFrom):
            # Example: from .submodule import something
            if not node.module:
                continue

            if node.level > 0:
                # Relative import
                name_split = module.__name__.split(".")
                names_to_remove = node.level - 1 if is_package else node.level
                relative_to = ".".join(name_split[: len(name_split) - names_to_remove])
                imports.append(f"{relative_to}.{node.module}")
            elif node.module:
                # Absolute import
                imports.append(node.module)

    return imports


def get_dependency_names(module: types.ModuleType) -> List[str]:
    dependencies = set()

    # Get from AST if possible
    for import_name in get_imports_from_source(module):
        dependencies.add(import_name)

    return sorted(list(dependencies))
