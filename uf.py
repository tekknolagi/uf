from __future__ import annotations
import dataclasses
from typing import Optional

counter = iter(range(1000))

@dataclasses.dataclass
class Op:
    id: int = dataclasses.field(default_factory=lambda: next(counter), init=False)
    forwarded: Optional[Op] = dataclasses.field(default=None, init=False)

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


trace = [
    x := Var("x"),
    y := Var("y"),
    a := Add(x, Const(1)),
    b := Add(y, Const(1)),
    c := Add(y, Const(1)),
]
a.make_equal_to(b)
for op in trace:
    print(f"{op.name()} = {op}")
