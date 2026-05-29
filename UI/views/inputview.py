from textual.screen import Screen
from textual.widgets import Button, Static, Input
from textual import on
from Engine.turing_engine import BaseTuringMachine
from UI.utils import MachineInputReel
from textual.containers import Vertical, Horizontal, VerticalScroll
from textual.app import ComposeResult
from UI.views.machineview import TuringMachineView


class InputView(Screen):
    DEFAULT_CSS = """
    InputView {
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

    #input-title {
        text-align: center;
        height: auto;
        color: $primary;
        text-style: bold;
        padding-bottom: 1;
    }

    #no-input-msg {
        text-align: center;
        height: auto;
        color: $text-muted;
        padding: 1 0;
    }

    #fields-container {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
    }

    .input-label {
        color: $text;
        text-style: bold;
        margin-top: 1;
    }

    .input-field {
        margin-bottom: 1;
        width: 100%;
    }

    #control-panel {
        height: auto;
        align: center middle;
        padding-top: 1;
    }

    #control-panel Button {
        margin: 0 1;
    }

    #alert-msg {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-top: 1;
    }
    """

    def __init__(self, machine: BaseTuringMachine):
        super().__init__()
        self.machine = machine

    def compose(self) -> ComposeResult:
        if (
            self.machine.takes_input
            and self.machine.inputs
            and len(self.machine.inputs.get_inputs()) > 0
        ):
            with VerticalScroll(id="main-container"):
                yield Static(
                    f"Input required for {self.machine.name}", id="input-title"
                )
                with VerticalScroll(id="fields-container"):
                    for machine_input in self.machine.inputs.get_inputs():
                        yield Static(
                            f"Enter input for {machine_input.input_query}:",
                            classes="input-label",
                        )
                        yield Input(
                            placeholder="Enter value",
                            id=f"input-field-{machine_input.id}",
                            classes="input-field",
                        )
                with Horizontal():
                    yield Static("", id="alert-msg")
                with Horizontal(id="control-panel"):
                    yield Button("Back", id="back-btn", variant="error")
                    yield Button("Start Machine", id="start-btn", variant="success")
        else:
            with Vertical(id="main-container"):
                yield Static(
                    f"Input required for {self.machine.name}", id="input-title"
                )
                yield Static("No input required for this machine.", id="no-input-msg")
                with Horizontal(id="control-panel"):
                    yield Button("Back", id="back-btn", variant="error")
                    yield Button("Start Machine", id="start-btn", variant="success")

    @on(Input.Submitted)
    def save_inputs(self, event: Input.Submitted):
        if self.machine.inputs:
            input_id = event.input.id
            if input_id and input_id.startswith("input-field-"):
                machine_input_id = int(input_id.split("-")[-1])
                machine_input = self.machine.inputs.get_input_by_id(machine_input_id)
                if machine_input:
                    machine_input.process_input(answer=event.value)

    @on(Button.Pressed)
    def handle_buttons(self, event: Button.Pressed):
        if event.button.id == "back-btn":
            alert_static = self.query_one("#alert-msg", Static)
            alert_static.update("")
            self.app.pop_screen()
        elif event.button.id == "start-btn":
            alert_static = self.query_one("#alert-msg", Static)
            alert_static.update("")
            if self.machine.inputs:
                for input_widget in self.query(Input):
                    input_id = input_widget.id
                    if input_id and input_id.startswith("input-field-"):
                        machine_input_id = int(input_id.split("-")[-1])
                        machine_input = self.machine.inputs.get_input_by_id(
                            machine_input_id
                        )
                        if machine_input:
                            machine_input.process_input(answer=input_widget.value)
            try:
                self.machine.reset()
                self.app.push_screen(TuringMachineView(self.machine))
            except ValueError as e:
                try:
                    alert = self.query_one("#alert-msg", Static)
                    alert.update(f"[indianred]Error: {str(e)}[/indianred]")
                except Exception:
                    pass
