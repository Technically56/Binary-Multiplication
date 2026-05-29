class MachineInput:
    def __init__(self, input_query: str):
        self.input_query = input_query
        self.answer = None
        self.error = None
        self.id = id(self)

    def process_input(self, answer: str = None, error: str = None):
        self.answer = answer
        self.error = error


class MachineInputReel:
    def __init__(self):
        self.inputs = {}

    def add_input(self, machine_input: str):
        input_obj = MachineInput(machine_input)
        self.inputs[input_obj.id] = input_obj

    def get_inputs(self) -> list[MachineInput]:
        return list(self.inputs.values())

    def get_input_by_id(self, input_id: int) -> MachineInput:
        return self.inputs.get(input_id)
