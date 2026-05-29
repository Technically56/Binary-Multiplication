from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static
from UI.views.machineview import TuringMachineView
from textual.containers import Vertical
from textual.containers import Grid
from UI.views.inputview import InputView

class MainMenu(Screen):
    DEFAULT_CSS = """
    MainMenu {
        align: center middle;
        background: $background;
    }

    #main-container {
        width: 68;
        height: auto;
        padding: 1 2;
        border: round $background;
        background: $surface;
    }

    #title {
        text-align: center;
        height: auto;
        color: $primary;
        text-style: bold;
    }

    #subtitle {
        text-align: center;
        height: auto;
        color: $text-muted;
        padding-bottom: 1;
    }

    #machine-grid {
        grid-size: 1;
        grid-gutter: 1;
        height: auto;
        padding: 1 0;
    }

    #machine-grid Button {
        height: 3;
        width: 100%;
    }

    #footer-hint {
        text-align: center;
        height: auto;
        padding-top: 1;
        color: $text-muted;
        text-style: italic;
    }
    """

    def __init__(self, machines):
        super().__init__()
        self.machines = machines

    def compose(self) -> ComposeResult:
        with Vertical(id="main-container"):
            yield Static("Turing Machine Simulator", id="title")
            yield Static("Select a machine to simulate", id="subtitle")
            with Grid(id="machine-grid"):
                for i, machine in enumerate(self.machines):
                    yield Button(machine.name, id=f"machine-{i}")
            yield Static(
                "[dim]↑↓ navigate · enter to select · q to quit[/dim]", id="footer-hint"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id and btn_id.startswith("machine-"):
            idx = int(btn_id.split("-")[1])
            selected_machine = self.machines[idx]

            self.app.push_screen(InputView(selected_machine))

    def on_key(self, event) -> None:
        if event.key == "q":
            self.app.exit()
