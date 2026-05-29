from abc import ABC, abstractmethod
from itertools import product
from UI.utils import MachineInputReel
from UI.utils import MachineInput


# The main engine class that defines the logic of the Turing machine.
# Subclasses must implement the setup_tape and process_result methods.
class BaseTuringMachine(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        transitions: dict,
        initial_state: str,
        accept_states: set,
        reject_states: set,
        inputs: MachineInputReel = None,
        takes_input: bool = True,
        check_input_alphabet: bool = False,
        check_output_alphabet: bool = False,
        check_tape_alphabet: bool = False,
        input_alphabet=None,
        output_alphabet=None,
        tape_alphabet=None,
        detector_machine: bool = False,
    ):
        self.name = name
        self.description = description
        self.transitions = self._normalize_transitions(transitions)
        self.initial_state = initial_state
        self.accept_states = accept_states
        self.reject_states = reject_states
        self.takes_input = takes_input
        self.detector_machine = detector_machine
        self.inputs = inputs
        self.tape = {}
        self.head_position = 0
        self.current_state = initial_state
        self.halted = False
        self.accepted = False
        self.steps = 0
        self.tape_setup = False

        self.input_alphabet = input_alphabet
        self.output_alphabet = output_alphabet
        self.tape_alphabet = tape_alphabet

        if check_input_alphabet and input_alphabet is None:
            raise ValueError(
                "Input alphabet must be provided if check_input_alphabet is True"
            )
        if check_output_alphabet and output_alphabet is None:
            raise ValueError(
                "Output alphabet must be provided if check_output_alphabet is True"
            )
        if check_tape_alphabet and tape_alphabet is None:
            raise ValueError(
                "Tape alphabet must be provided if check_tape_alphabet is True"
            )

        self.check_input_alphabet = check_input_alphabet
        self.check_output_alphabet = check_output_alphabet
        self.check_tape_alphabet = check_tape_alphabet

        self.reset()

    @staticmethod
    def _split_symbol_spec(spec):
        if isinstance(spec, (list, tuple, set, frozenset)):
            symbols = list(spec)
            if not symbols:
                raise ValueError("Empty multi-symbol transition spec")
            return symbols
        if not isinstance(spec, str) or "," not in spec:
            return [spec]
        pieces = [p.strip() for p in spec.split(",")]
        if any(p == "" for p in pieces):
            raise ValueError(f"Empty symbol in multi-symbol transition spec: {spec!r}")
        return pieces

    def _normalize_transitions(self, transitions: dict) -> dict:
        expanded = {}
        for (state, symbol_spec), value in transitions.items():
            for symbol in self._split_symbol_spec(symbol_spec):
                key = (state, symbol)
                if key in expanded and expanded[key] != value:
                    raise ValueError(
                        f"Conflicting transitions for state {state!r} on symbol {symbol!r}"
                    )
                expanded[key] = value
        return expanded

    @abstractmethod
    def setup_tape(self) -> dict:
        """Abstract method to initialize the tape. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def process_result(self) -> str:
        """Abstract method to process the result after halting. Must be implemented by subclasses."""
        pass

    def read_tape(self):
        return self.tape.get(self.head_position, "_")

    def write_tape(self, symbol):
        self.tape[self.head_position] = symbol

    def move_head(self, direction):
        if direction == "R":
            self.head_position += 1
        elif direction == "L":
            self.head_position -= 1
        elif direction == "S":
            pass
        else:
            raise ValueError(f"Invalid head movement direction: {direction}")

    def step(self):
        if self.halted:
            raise ValueError("Machine has already halted. Please reset to run again.")

        current_symbol = self.read_tape()
        transition_key = (self.current_state, current_symbol)

        if transition_key not in self.transitions:
            self.halted = True
            self.accepted = False
            raise NotImplementedError(
                f"No transition defined for state '{self.current_state}' and symbol '{current_symbol}', halting machine."
            )

        new_state, new_symbol, direction = self.transitions[transition_key]
        self.write_tape(new_symbol)
        self.current_state = new_state
        self.move_head(direction)
        self.steps += 1

        if self.current_state in self.accept_states:
            self.halted = True
            self.accepted = True
        elif self.current_state in self.reject_states:
            self.halted = True
            self.accepted = False

    def get_tape_contents(self):
        if not self.tape:
            return f"[{self.read_tape()}]"
        min_index = min(min(self.tape.keys()), self.head_position)
        max_index = max(max(self.tape.keys()), self.head_position)
        tape_str = ""
        for i in range(min_index, max_index + 1):
            symbol = self.tape.get(i, "_")
            if i == self.head_position:
                tape_str += f"[{symbol}]"
            else:
                tape_str += f" {symbol} "
        return tape_str

    def get_current_state(self):
        return self.current_state

    def get_steps(self):
        return self.steps

    def check_inputs(self) -> bool:
        if not self.takes_input or self.inputs is None:
            return True

        if self.check_input_alphabet:
            for machineInput in self.inputs.get_inputs():
                if machineInput.answer is None:
                    continue
                for char in str(machineInput.answer):
                    if char not in self.input_alphabet:
                        raise ValueError(f"Invalid input symbol: {char}")
        return True

    def check_tape(self) -> bool:
        if not self.tape_setup:
            raise ValueError(
                "Tape has not been set up. Please run reset/setup_tape first."
            )

        if self.check_tape_alphabet:
            for symbol in self.tape.values():
                if symbol not in self.tape_alphabet:
                    raise ValueError(f"Invalid tape symbol: {symbol}")
        return True

    def check_output(self) -> bool:
        if not self.tape_setup:
            raise ValueError(
                "Tape has not been set up. Please run reset/setup_tape first."
            )
        if not self.halted:
            raise ValueError(
                "Machine has not been run yet. Please run the machine and halt it before checking the output."
            )
        if self.detector_machine:
            raise ValueError(
                "This machine is a detector machine and does not produce output."
            )

        if self.check_output_alphabet:
            for char in str(self.process_result()):
                if char not in self.output_alphabet:
                    raise ValueError(f"Invalid output symbol: {char}")
        return True

    def reset(self):

        self.tape = self.setup_tape()
        self.tape_setup = True

        self.check_inputs()
        self.check_tape()

        self.head_position = 0
        self.current_state = self.initial_state
        self.halted = False
        self.accepted = False
        self.steps = 0

        if self.current_state in self.accept_states:
            self.halted = True
            self.accepted = True
        elif self.current_state in self.reject_states:
            self.halted = True
            self.accepted = False

    def headless_run(self):
        self.reset()
        try:
            while not self.halted:
                self.step()
        except NotImplementedError:
            pass

        if not self.detector_machine:
            self.check_output()


class MultiTapeTuringMachine(BaseTuringMachine):
    def __init__(
        self,
        name: str,
        description: str,
        transitions: dict,
        initial_state: str,
        accept_states: set,
        reject_states: set,
        num_tapes: int,
        inputs: MachineInputReel = None,
        takes_input: bool = True,
        check_input_alphabet: bool = False,
        check_output_alphabet: bool = False,
        check_tape_alphabet: bool = False,
        input_alphabet=None,
        output_alphabet=None,
        tape_alphabet=None,
        detector_machine: bool = False,
    ):
        self.num_tapes = num_tapes
        self.tapes = [{} for _ in range(num_tapes)]
        self.head_positions = [0] * num_tapes

        super().__init__(
            name=name,
            description=description,
            transitions=transitions,
            initial_state=initial_state,
            accept_states=accept_states,
            reject_states=reject_states,
            inputs=inputs,
            takes_input=takes_input,
            check_input_alphabet=check_input_alphabet,
            check_output_alphabet=check_output_alphabet,
            check_tape_alphabet=check_tape_alphabet,
            input_alphabet=input_alphabet,
            output_alphabet=output_alphabet,
            tape_alphabet=tape_alphabet,
            detector_machine=detector_machine,
        )

    def _normalize_transitions(self, transitions: dict) -> dict:
        expanded = {}
        for (state, symbol_tuple), value in transitions.items():
            if not isinstance(symbol_tuple, tuple):
                raise ValueError(
                    f"Multi-tape transition key must use a tuple of symbols, got {symbol_tuple!r}"
                )
            per_tape_options = [self._split_symbol_spec(s) for s in symbol_tuple]
            for combo in product(*per_tape_options):
                key = (state, combo)
                if key in expanded and expanded[key] != value:
                    raise ValueError(
                        f"Conflicting transitions for state {state!r} on symbols {combo!r}"
                    )
                expanded[key] = value
        return expanded

    def read_tape(self):
        return tuple(
            tape.get(head, "_") for tape, head in zip(self.tapes, self.head_positions)
        )

    def write_tape(self, symbols: tuple):
        if len(symbols) != self.num_tapes:
            raise ValueError(
                f"Expected {self.num_tapes} symbols to write, got {len(symbols)}"
            )
        for i, symbol in enumerate(symbols):
            self.tapes[i][self.head_positions[i]] = symbol

    def move_head(self, directions: tuple):
        if len(directions) != self.num_tapes:
            raise ValueError(
                f"Expected {self.num_tapes} directions, got {len(directions)}"
            )
        for i, direction in enumerate(directions):
            if direction == "R":
                self.head_positions[i] += 1
            elif direction == "L":
                self.head_positions[i] -= 1
            elif direction == "S":
                pass
            else:
                raise ValueError(
                    f"Invalid head movement direction: {direction} on tape {i}"
                )

    def step(self):
        if self.halted:
            raise ValueError("Machine has already halted. Please reset to run again.")

        current_symbols = self.read_tape()
        transition_key = (self.current_state, current_symbols)

        if transition_key not in self.transitions:
            self.halted = True
            self.accepted = False
            raise NotImplementedError(
                f"No transition defined for state '{self.current_state}' and symbols '{current_symbols}', halting machine."
            )

        new_state, new_symbols, directions = self.transitions[transition_key]
        self.write_tape(new_symbols)
        self.current_state = new_state
        self.move_head(directions)
        self.steps += 1

        if self.current_state in self.accept_states:
            self.halted = True
            self.accepted = True
        elif self.current_state in self.reject_states:
            self.halted = True
            self.accepted = False

    def get_tape_contents(self) -> list:
        tape_strings = []
        for tape_idx, tape in enumerate(self.tapes):
            head_pos = self.head_positions[tape_idx]
            if not tape:
                tape_strings.append(f"[_]")
                continue

            min_index = min(min(tape.keys()), head_pos)
            max_index = max(max(tape.keys()), head_pos)
            tape_str = ""
            for i in range(min_index, max_index + 1):
                symbol = tape.get(i, "_")
                if i == head_pos:
                    tape_str += f"[{symbol}]"
                else:
                    tape_str += f" {symbol} "
            tape_strings.append(tape_str.strip())
        return tape_strings

    def check_tape(self) -> bool:
        if not self.tape_setup:
            raise ValueError(
                "Tape has not been set up. Please run reset/setup_tape first."
            )

        if self.check_tape_alphabet:
            for tape in self.tapes:
                for symbol in tape.values():
                    if symbol not in self.tape_alphabet:
                        raise ValueError(f"Invalid tape symbol: {symbol}")
        return True

    def reset(self):
        self.tapes = self.setup_tape()
        if not isinstance(self.tapes, list) or len(self.tapes) != self.num_tapes:
            raise ValueError(
                f"setup_tape must return a list of {self.num_tapes} dictionaries"
            )

        self.tape_setup = True
        self.tape = self.tapes[0] if self.tapes else {}

        self.check_inputs()
        self.check_tape()

        self.head_positions = [0] * self.num_tapes
        self.current_state = self.initial_state
        self.halted = False
        self.accepted = False
        self.steps = 0

        if self.current_state in self.accept_states:
            self.halted = True
            self.accepted = True
        elif self.current_state in self.reject_states:
            self.halted = True
            self.accepted = False


if __name__ == "__main__":
    print(
        "This is the base Turing machine class. Please implement a specific Turing machine by subclassing this and defining the transitions and tape setup."
    )
