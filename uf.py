from __future__ import annotations
import dataclasses
from typing import Optional

counter = iter(range(1000))

all_instrs = {}

@dataclasses.dataclass
class Op:
    id: int = dataclasses.field(default_factory=lambda: next(counter), init=False)
    forwarded: Optional[Op] = dataclasses.field(default=None, init=False)

    def __post_init__(self):
        all_instrs[self.name()] = self

    def find(self):
        result = self
        while (found := result.forwarded) is not None:
            if found is self:
                raise ValueError("Cycle detected")
            result = found
        return result

    def make_equal_to(self, y):
        self.find().forwarded = y

    def name(self):
        return f"v{self.id}"

@dataclasses.dataclass
class Var(Op):
    _name: str

    def __repr__(self):
        return self._name

@dataclasses.dataclass
class Const(Op):
    value: int

    def __repr__(self):
        return str(self.value)

    def name(self):
        return str(self.value)

@dataclasses.dataclass
class Add(Op):
    left: Op
    right: Op

    def __repr__(self):
        return f"{self.left.name()} + {self.right.name()}"

@dataclasses.dataclass
class Mul(Op):
    left: Op
    right: Op

    def __repr__(self):
        return f"{self.left.name()} * {self.right.name()}"

@dataclasses.dataclass
class Eq(Op):
    left: Op
    right: Op

    def __repr__(self):
        return f"{self.left.name()} == {self.right.name()}"


def equivalence_classes():
    result = {}
    for instr in all_instrs.values():
        result.setdefault(instr.find().name(), set()).add(instr.name())
    return result


def match(pred):
    eq = equivalence_classes()
    result = set()
    for instr in all_instrs.values():
        if pred(instr):
            result.update(eq[instr.find().name()])
    return [all_instrs[name] for name in result]


def is_add_1(instr):
    eq = equivalence_classes()
    instrs = all_instrs.copy()
    for instr_name in eq.get(instr.find().name(), []):
        op = instrs[instr_name]
        if not isinstance(op, Add):
            continue
        for left_name in eq.get(op.left.find().name(), []):
            for right_name in eq.get(op.right.find().name(), []):
                match (instrs[left_name], instrs[right_name]):
                    case (Const(1), _) | (_, Const(1)):
                        return True
    return False


trace = [
    x := Var("x"),
    y := Var("y"),
    z := Var("z"),
    xy := Add(x, y),
]
for instr in trace:
    print(f"{instr.name()} = {instr}")
print("---")
y.make_equal_to(Const(1))
z.make_equal_to(xy)
for op in match(is_add_1):
    print(op)
