from textual.app import App
from UI.views.mainview import MainMenu
from Engine.turing_engine import BaseTuringMachine
import importlib.util
import inspect
import os
import sys


def load_machines_from_folder(base_folder="Machines", exclude_folders=None):
    """
    Recursively scans the base_folder for any .py files and extracts
    classes that inherit from BaseTuringMachine, ignoring specified folders.
    """
    if exclude_folders is None:
        exclude_folders = ["example", "__pycache__", ".git"]

    loaded_machine_classes = []

    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.append(project_root)

    for root_dir, dirs, files in os.walk(base_folder):
        dirs[:] = [
            d for d in dirs if d.lower() not in [ex.lower() for ex in exclude_folders]
        ]

        for filename in files:
            if filename.endswith(".py") and not filename.startswith("__"):
                filepath = os.path.join(root_dir, filename)

                rel_path = os.path.relpath(filepath, project_root)
                module_name = rel_path.replace(os.sep, ".")[:-3]

                try:
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)

                        for name, obj in inspect.getmembers(module):
                            if (
                                inspect.isclass(obj)
                                and issubclass(obj, BaseTuringMachine)
                                and obj is not BaseTuringMachine
                            ):
                                loaded_machine_classes.append(obj)

                except Exception as e:
                    print(f"[Warning] Failed to load {filepath}: {e}")

    return loaded_machine_classes


class TuringSimulatorApp(App):
    def __init__(self, machines):
        super().__init__()
        self.machines = machines

    def on_mount(self) -> None:
        self.push_screen(MainMenu(self.machines))


def main():
    machine_classes = load_machines_from_folder()
    machines = [cls() for cls in machine_classes]
    if not machines:
        print(
            "No Turing machines found in the 'Machines' folder. Please add some and try again."
        )
        return
    app = TuringSimulatorApp(machines)
    app.run()


if __name__ == "__main__":
    main()
