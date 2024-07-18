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


def match_add_1():
    # Find matches for add(x, 1) or add(1, x)
    eq = equivalence_classes()
    result = []
    instrs = all_instrs.copy()
    for instr in instrs.values():
        if not isinstance(instr, Add):
            continue
        for left_name in eq.get(instr.left.find().name(), []):
            for right_name in eq.get(instr.right.find().name(), []):
                left = all_instrs[left_name]
                right = all_instrs[right_name]
                if isinstance(left, Const) and left.value == 1:
                    result.append(Add(left, right))
                if isinstance(right, Const) and right.value == 1:
                    result.append(Add(left, right))
    return result


trace = [
    x := Var("x"),
    y := Var("y"),
    a := Add(x, Const(1)),
    b := Add(y, Const(1)),
    c := Add(y, Const(1)),
    Add(a, b),
    Add(c, Const(2)),
]
print(equivalence_classes())
a.make_equal_to(b)
print(equivalence_classes())
for op in match_add_1():
    print(op)
for op in trace:
    print(f"{op.name()} = {op.find()}")
