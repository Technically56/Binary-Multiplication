import string
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Horizontal, VerticalScroll, HorizontalScroll, Container
from termaid import render as termaid_render
from Engine.turing_engine import BaseTuringMachine, MultiTapeTuringMachine


class TuringMachineView(Screen):
    DEFAULT_CSS = """
    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    #machine-info {
        height: auto;
        padding-bottom: 1;
        content-align: center middle;
    }
    #graph-scroll {
        height: 1fr;
        width: 100%;
        overflow: auto;
        scrollbar-gutter: stable;
    }
    #graph-widget {
        height: auto;
        width: auto;
        overflow:auto;
    }
    #tape-scroll {
        height: auto;
        max-height: 5;
        background: $surface;
        scrollbar-gutter: stable;
        align: center middle;
    }
    #tape-view {
        content-align: center middle;
        padding: 1;
        text-style: bold;
        height: auto;
        width: auto;
    }
    #control-panel {
        height: auto;
        align: center middle;
        padding-top: 1;
    }
    #alert-view {
        content-align: center middle;
        padding: 1;
        text-style: bold;
        height: auto;
    }
    #result-view {
        content-align: center middle;
        padding: 1;
        text-style: bold;
        height: auto;
    }
    #steps-view{
        content-align: center middle;
        padding: 1;
        text-style: bold;
        height: auto;
    }
    """

    def __init__(self, machine: BaseTuringMachine):
        super().__init__()
        self.machine = machine
        self.machine.reset()

    def _render_graph(self) -> str:
        mermaid = render_termaid_graph(
            self.machine.transitions, self.machine.current_state
        )
        return termaid_render(mermaid, gap=14, padding_x=6)

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="main-container"):
            yield Static(
                f"[bold]{self.machine.name}[/bold]\n{self.machine.description}",
                id="machine-info",
            )

            with Container(id="graph-scroll"):
                yield Static(self._render_graph(), id="graph-widget")

            with HorizontalScroll(id="tape-scroll"):
                tape_content = self.machine.get_tape_contents()
                if isinstance(self.machine, MultiTapeTuringMachine):
                    tape_display = "\n".join(tape_content)
                else:
                    tape_display = tape_content
                yield Static(tape_display, id="tape-view", markup=False)
            yield Static("", id="alert-view")
            if not self.machine.detector_machine:
                yield Static("", id="result-view")
            yield Static(
                f"[dodgerblue]Steps: {self.machine.get_steps()}[/dodgerblue]",
                id="steps-view",
            )
            with Horizontal(id="control-panel"):
                yield Button("Back", id="back-btn", variant="error")
                yield Button("Reset", id="reset-btn", variant="warning")
                yield Button("Step", id="step-btn", variant="primary")
                yield Button("Run to End", id="run-btn", variant="success")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        if btn_id == "back-btn":
            self.app.pop_screen()
        elif btn_id == "reset-btn":
            self.machine.reset()
            alert_static = self.query_one("#alert-view", Static)
            alert_static.update("[goldenrod]Machine reset[/goldenrod]!")
            result_static = self.query_one("#result-view", Static)
            result_static.update("")
            steps_static = self.query_one("#steps-view", Static)
            steps_static.update(
                f"[dodgerblue]Steps: {self.machine.get_steps()}[/dodgerblue]"
            )
            self.refresh_view()
        elif btn_id == "step-btn":
            try:
                self.machine.step()
                steps_static = self.query_one("#steps-view", Static)
                steps_static.update(
                    f"[dodgerblue]Steps: {self.machine.get_steps()}[/dodgerblue]"
                )
                if self.machine.accepted:
                    alert_static = self.query_one("#alert-view", Static)
                    alert_static.update(
                        "[mediumseagreen]Machine accepted the input![/mediumseagreen]"
                    )
                    if not self.machine.detector_machine:
                        result_static = self.query_one("#result-view", Static)
                        result_static.update(
                            f"[mediumseagreen]Result: {self.machine.process_result()}[/mediumseagreen]"
                        )
                elif self.machine.halted and not self.machine.accepted:
                    alert_static = self.query_one("#alert-view", Static)
                    alert_static.update(
                        "[indianred]Result: Machine rejected the input![/indianred]"
                    )
                elif not self.machine.halted and not self.machine.accepted:
                    alert_static = self.query_one("#alert-view", Static)
                    alert_static.update("[dodgerblue]Step Taken![/dodgerblue]")
            except (NotImplementedError, ValueError) as e:
                alert_static = self.query_one("#alert-view", Static)
                alert_static.update(f"[red]Error: {str(e)}[/red]")
            self.refresh_view()
        elif btn_id == "run-btn":
            try:
                while not self.machine.halted:
                    self.machine.step()
                steps_static = self.query_one("#steps-view", Static)
                steps_static.update(
                    f"[dodgerblue]Steps: {self.machine.get_steps()}[/dodgerblue]"
                )
                alert_static = self.query_one("#alert-view", Static)
                if self.machine.accepted:
                    alert_static.update(
                        "[mediumseagreen]Machine accepted the input![/mediumseagreen]"
                    )
                    if not self.machine.detector_machine:
                        result_static = self.query_one("#result-view", Static)
                        result_static.update(
                            f"[mediumseagreen]Result: {self.machine.process_result()}[/mediumseagreen]"
                        )
                else:
                    alert_static.update(
                        "[indianred]Machine rejected the input![/indianred]"
                    )
                    if not self.machine.detector_machine:
                        result_static = self.query_one("#result-view", Static)
                        result_static.update("")  # Clear result if rejected
            except (NotImplementedError, ValueError) as e:
                alert_static = self.query_one("#alert-view", Static)
                alert_static.update(f"[red]Error: {str(e)}[/red]")
            self.refresh_view()

    def refresh_view(self) -> None:
        """Dynamically updates the Tape and Graph widgets on the screen."""

        tape_content = self.machine.get_tape_contents()
        if isinstance(self.machine, MultiTapeTuringMachine):
            tape_display = "\n".join(tape_content)
        else:
            tape_display = tape_content

        tape_static = self.query_one("#tape-view", Static)
        tape_static.update(tape_display)

        self.query_one("#graph-widget", Static).update(self._render_graph())

        if self.machine.halted:
            self.query_one("#step-btn", Button).disabled = True
            self.query_one("#run-btn", Button).disabled = True
        else:
            self.query_one("#step-btn", Button).disabled = False
            self.query_one("#run-btn", Button).disabled = False


def render_termaid_graph(transitions: dict, current_state: str = None) -> str:
    graph = "flowchart TB\n"
    all_states = []
    seen = set()
    for (state, _), (new_state, _, _) in transitions.items():
        for s in (state, new_state):
            if s not in seen:
                seen.add(s)
                all_states.append(s)

    for state in all_states:
        if state == current_state:
            graph += f'    {state}["► {state} ◄"]\n'
        else:
            graph += f'    {state}["{state}"]\n'

    grouped = {}
    for (state, symbol), (new_state, new_symbol, direction) in transitions.items():
        key = (state, new_state)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append((symbol, new_symbol, direction))

    def format_symbol_set(symbols: set) -> str:
        rem = set(symbols)
        parts = []

        digits = set(string.digits)
        if digits.issubset(rem):
            parts.append("0-9")
            rem -= digits

        uppercase = set(string.ascii_uppercase)
        if uppercase.issubset(rem):
            parts.append("A-Z")
            rem -= uppercase

        lowercase = set(string.ascii_lowercase)
        if lowercase.issubset(rem):
            parts.append("a-z")
            rem -= lowercase

        if rem:
            sorted_rem = sorted(list(rem))
            if len(sorted_rem) <= 5:
                parts.extend(sorted_rem)
            else:
                parts.append(",".join(sorted_rem[:3]) + f"...({len(sorted_rem)} total)")

        return ",".join(parts)

    for (state, new_state), trans_list in grouped.items():
        behaviors = {}
        for symbol, new_symbol, direction in trans_list:
            b_key = ("same", direction) if symbol == new_symbol else (new_symbol, direction)
            if b_key not in behaviors:
                behaviors[b_key] = set()
            behaviors[b_key].add(symbol)

        label_parts = []
        for (new_sym, direction), symbols in behaviors.items():
            syms_str = format_symbol_set(symbols)
            if new_sym == "same":
                label_parts.append(f"{syms_str}/same,{direction}")
            else:
                label_parts.append(f"{syms_str}/{new_sym},{direction}")

        label = " | ".join(label_parts)
        graph += f'    {state} -->|"{label}"| {new_state}\n'

    return graph
