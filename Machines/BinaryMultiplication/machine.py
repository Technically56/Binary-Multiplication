import os
import sys

from UI.utils import MachineInputReel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.turing_engine import BaseTuringMachine


class BinaryMultiplier(BaseTuringMachine):
    BLANK = "_"

    def __init__(self, inputs: MachineInputReel = None):
        name = "Binary Multiplier (Shift & Add)"
        description = (
            "Multiplies two binary numbers in the format '<a>*<b>=' "
            "(e.g. '101*11='). Implemented using the Shift-and-Add "
            "algorithm."
        )

        if inputs is None:
            inputs = MachineInputReel()
        inputs.add_input("First Binary Number")
        inputs.add_input("Second Binary Number")

        transitions = self._build_transitions()
        initial_state = "q_start"
        accept_states = {"q_accept"}
        reject_states = {"q_reject"}
        takes_input = True

        input_alphabet = {"0", "1"}
        tape_alphabet = {"0", "1", "*", "=", "_", "d", "m", "n", "s", "t"}

        super().__init__(
            name,
            description,
            transitions,
            initial_state,
            accept_states,
            reject_states,
            inputs=inputs,
            takes_input=takes_input,
            check_input_alphabet=True,
            check_tape_alphabet=True,
            input_alphabet=input_alphabet,
            tape_alphabet=tape_alphabet,
        )

    @staticmethod
    def _build_transitions():
        T = {}
        B_sym = BinaryMultiplier.BLANK

        for sym in ("0", "1", "*"):
            T[("q_start", sym)] = ("q_start", sym, "R")
        T[("q_start", "=")] = ("check_b_bit", "=", "L")

        T[("check_b_bit", "d")] = ("check_b_bit", "d", "L")
        T[("check_b_bit", "0")] = (
            "find_star_scan_left",
            "d",
            "L",
        )
        T[("check_b_bit", "1")] = ("seek_star_left_for_add", "d", "L")
        T[("check_b_bit", "*")] = ("q_accept", "*", "S")
        for sym in ("0", "1", "d"):
            T[("seek_star_left_for_add", sym)] = ("seek_star_left_for_add", sym, "L")
        T[("seek_star_left_for_add", "*")] = ("seek_unmarked_a_left", "*", "L")

        for sym in ("m", "n"):
            T[("seek_unmarked_a_left", sym)] = ("seek_unmarked_a_left", sym, "L")
        T[("seek_unmarked_a_left", "0")] = ("to_p_a0_c0", "m", "R")
        T[("seek_unmarked_a_left", "1")] = ("to_p_a1_c0", "n", "R")
        T[("seek_unmarked_a_left", B_sym)] = ("q_reject", B_sym, "R")

        for a in (0, 1):
            for c in (0, 1):
                st = f"to_p_a{a}_c{c}"
                for sym in ("0", "1", "m", "n", "*", "d"):
                    T[(st, sym)] = (st, sym, "R")
                T[(st, "=")] = (f"scan_p_a{a}_c{c}", "=", "R")
        for a in (0, 1):
            for c in (0, 1):
                st = f"scan_p_a{a}_c{c}"
                T[(st, "s")] = (st, "s", "R")
                T[(st, "t")] = (st, "t", "R")
                for p_val, p_sym in [(0, "0"), (1, "1"), (0, B_sym)]:
                    total = a + c + p_val
                    bit, new_c = total % 2, total // 2
                    write_sym = "s" if bit == 0 else "t"
                    T[(st, p_sym)] = (f"ret_c{new_c}", write_sym, "L")

        for c in (0, 1):
            st = f"ret_c{c}"
            for sym in ("s", "t", "=", "d", "0", "1"):
                T[(st, sym)] = (st, sym, "L")
            T[(st, "*")] = (f"seek_unmarked_a_left_c{c}", "*", "L")
        for c in (0, 1):
            st = f"seek_unmarked_a_left_c{c}"
            for sym in ("m", "n"):
                T[(st, sym)] = (st, sym, "L")
            T[(st, "0")] = (f"to_p_a0_c{c}", "m", "R")
            T[(st, "1")] = (f"to_p_a1_c{c}", "n", "R")

        T[("seek_unmarked_a_left_c0", B_sym)] = ("restore_sweep_right", B_sym, "R")
        T[("seek_unmarked_a_left_c1", B_sym)] = ("final_carry_to_p", B_sym, "R")
        for sym in ("0", "1", "m", "n", "*", "d"):
            T[("final_carry_to_p", sym)] = ("final_carry_to_p", sym, "R")
        T[("final_carry_to_p", "=")] = ("final_carry_scan_p", "=", "R")

        T[("final_carry_scan_p", "s")] = ("final_carry_scan_p", "s", "R")
        T[("final_carry_scan_p", "t")] = ("final_carry_scan_p", "t", "R")
        T[("final_carry_scan_p", "1")] = (
            "final_carry_scan_p",
            "s",
            "R",
        )
        T[("final_carry_scan_p", "0")] = ("find_left_blank", "t", "L")
        T[("final_carry_scan_p", B_sym)] = ("find_left_blank", "t", "L")

        for sym in ("s", "t", "0", "1", "=", "d", "*", "m", "n"):
            T[("find_left_blank", sym)] = ("find_left_blank", sym, "L")
        T[("find_left_blank", B_sym)] = ("restore_sweep_right", B_sym, "R")

        T[("restore_sweep_right", "m")] = ("restore_sweep_right", "0", "R")
        T[("restore_sweep_right", "n")] = ("restore_sweep_right", "1", "R")
        T[("restore_sweep_right", "s")] = ("restore_sweep_right", "0", "R")
        T[("restore_sweep_right", "t")] = ("restore_sweep_right", "1", "R")
        for sym in ("0", "1", "*", "d", "="):
            T[("restore_sweep_right", sym)] = ("restore_sweep_right", sym, "R")

        T[("restore_sweep_right", B_sym)] = ("find_star_scan_left", B_sym, "L")
        for sym in ("0", "1", "d", "="):
            T[("find_star_scan_left", sym)] = ("find_star_scan_left", sym, "L")
        T[("find_star_scan_left", "*")] = ("shift_hold_star", "0", "R")

        shift_symbols = ("0", "1", "*", "d", "=")
        name_map = {"0": "0", "1": "1", "*": "star", "d": "d", "=": "eq"}

        for hold_sym in shift_symbols:
            safe_hold_state = f"shift_hold_{name_map[hold_sym]}"
            for read_sym in shift_symbols:
                safe_next_state = f"shift_hold_{name_map[read_sym]}"
                T[(safe_hold_state, read_sym)] = (safe_next_state, hold_sym, "R")

            T[(safe_hold_state, B_sym)] = ("scan_left_to_eq", hold_sym, "S")

        for sym in ("0", "1"):
            T[("scan_left_to_eq", sym)] = ("scan_left_to_eq", sym, "L")
        T[("scan_left_to_eq", "=")] = ("check_b_bit", "=", "L")

        return T

    def setup_tape(self) -> dict:
        num1 = "101"
        num2 = "11"

        if self.inputs:
            input_list = self.inputs.get_inputs()
            if len(input_list) >= 2:
                ans1 = input_list[0].answer
                ans2 = input_list[1].answer
                if ans1 is not None and ans1.strip() != "":
                    num1 = ans1.strip()
                if ans2 is not None and ans2.strip() != "":
                    num2 = ans2.strip()

        input_str = f"{num1}*{num2}="

        self.tape = {}
        pad_left, pad_right = 20, 200
        for i in range(-pad_left, 0):
            self.tape[i] = self.BLANK
        for i, ch in enumerate(input_str):
            self.tape[i] = ch
        for i in range(len(input_str), len(input_str) + pad_right):
            self.tape[i] = self.BLANK

        self.tape_setup = True
        self.check_inputs()
        self.check_tape()
        return self.tape

    def process_result(self) -> str:
        eq_pos = next((p for p in sorted(self.tape) if self.tape[p] == "="), None)
        if eq_pos is None:
            return ""

        lsb_first = []
        pos = eq_pos + 1
        while self.tape.get(pos) in ("0", "1"):
            lsb_first.append(self.tape[pos])
            pos += 1

        if not lsb_first:
            return "0 (decimal: 0)"

        msb_first = "".join(reversed(lsb_first))
        decimal = int(msb_first, 2)
        normalized = bin(decimal)[2:]
        return f"{normalized} (decimal: {decimal})"


if __name__ == "__main__":
    print(
        "Binary Multiplier Turing Machine. Input format '<a>*<b>=' (e.g. "
        "'101*11='). Automatically evaluates LSB-first outputs."
    )
