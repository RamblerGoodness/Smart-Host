import os
import importlib
import inspect

PLUGIN_REGISTRY = {}

plugin_dir = os.path.dirname(__file__)
for fname in os.listdir(plugin_dir):
    if fname.endswith('.py') and fname != '__init__.py':
        mod_name = f"plugins.{fname[:-3]}"
        mod = importlib.import_module(mod_name)
        for name, obj in inspect.getmembers(mod):
            if inspect.isfunction(obj):
                PLUGIN_REGISTRY[name] = obj

def list_tools():
    return list(PLUGIN_REGISTRY.keys())

def call_tool(name, *args, **kwargs):
    if name not in PLUGIN_REGISTRY:
        raise ValueError(f"Tool '{name}' not found.")
    return PLUGIN_REGISTRY[name](*args, **kwargs)
