"""Executable reference model for a deliberately small Moraine contract fragment.

This is NOT a Lean plugin, a security sandbox, or a Lean-verified checker.
It checks exact universal length laws for a closed List[Nat] expression grammar.
The accompanying article proves the mathematical model's soundness and completeness.
Only the Python standard library is needed (Python 3.9+).
"""
from dataclasses import dataclass
from typing import Optional, Tuple, Sequence

MAX_ARITY = 64
MAX_DEPTH = 64
MAX_NODES = 10000
MAX_BITS = 4096

class Refusal(ValueError):
    """A request was unsupported, malformed, or did not match its certificate."""

@dataclass(frozen=True)
class Expr:
    op: str
    children: Tuple['Expr', ...] = ()
    index: Optional[int] = None
    value: Optional[int] = None

@dataclass(frozen=True)
class Affine:
    constant: int
    coefficients: Tuple[int, ...]

    def at(self, lengths: Sequence[int]) -> int:
        if len(lengths) != len(self.coefficients):
            raise Refusal('length-vector arity mismatch')
        for n in lengths:
            _nat(n, 'input length')
        return self.constant + sum(a*n for a, n in zip(self.coefficients, lengths))

@dataclass(frozen=True)
class Request:
    epoch: str
    arity: int
    expression: Expr
    specification: Affine

@dataclass(frozen=True)
class Certificate:
    epoch: str
    arity: int
    expression: Expr
    normal_form: Affine

@dataclass(frozen=True)
class Receipt:
    request: Request
    normal_form: Affine
    validation: str = 'python-reference-check; not Lean-kernel-checked'


def _nat(n: int, role: str) -> None:
    if type(n) is not int or n < 0 or n.bit_length() > MAX_BITS:
        raise Refusal(role + ' must be a bounded-size natural number')


def _arity(k: int) -> None:
    if type(k) is not int or not 0 <= k <= MAX_ARITY:
        raise Refusal('unsupported arity')


def _form(a: Affine, k: int) -> None:
    if type(a) is not Affine or type(a.coefficients) is not tuple:
        raise Refusal('malformed affine form')
    if len(a.coefficients) != k:
        raise Refusal('coefficient arity mismatch')
    _nat(a.constant, 'constant')
    for x in a.coefficients:
        _nat(x, 'coefficient')


def normal_form(expression: Expr, arity: int) -> Affine:
    """Reconstruct the length law; no provider-supplied assertion is trusted."""
    _arity(arity)
    nodes = [0]
    def visit(e: Expr, depth: int) -> Affine:
        nodes[0] += 1
        if depth > MAX_DEPTH or nodes[0] > MAX_NODES:
            raise Refusal('structural resource limit')
        if type(e) is not Expr or type(e.op) is not str or type(e.children) is not tuple:
            raise Refusal('malformed expression')
        counts = {'input': 0, 'nil': 0, 'cons': 1,
                  'append': 2, 'reverse': 1, 'map_succ': 1}
        if e.op not in counts or len(e.children) != counts[e.op]:
            raise Refusal('unsupported operator or child arity')
        if e.op == 'input':
            if type(e.index) is not int or not 0 <= e.index < arity or e.value is not None:
                raise Refusal('invalid input index')
            return Affine(0, tuple(int(i == e.index) for i in range(arity)))
        if e.index is not None:
            raise Refusal('unexpected index')
        if e.op == 'cons':
            _nat(e.value, 'cons value')
        elif e.value is not None:
            raise Refusal('unexpected value')
        if e.op == 'nil':
            return Affine(0, (0,) * arity)
        children = [visit(c, depth + 1) for c in e.children]
        if e.op in ('reverse', 'map_succ'):
            return children[0]
        if e.op == 'cons':
            out = Affine(children[0].constant + 1, children[0].coefficients)
        else:
            x, y = children
            # Both vectors were constructed with the same checked arity.
            out = Affine(x.constant + y.constant,
                         tuple(x.coefficients[i] + y.coefficients[i] for i in range(arity)))
        _form(out, arity)
        return out
    return visit(expression, 0)


def propose(request: Request) -> Certificate:
    """Untrusted producer. Verification below independently reconstructs its law."""
    return Certificate(request.epoch, request.arity, request.expression,
                       normal_form(request.expression, request.arity))


def verify(request: Request, certificate: Certificate) -> Receipt:
    if type(request) is not Request or type(certificate) is not Certificate:
        raise Refusal('wrong protocol object')
    if type(request.epoch) is not str or not request.epoch:
        raise Refusal('missing epoch')
    _arity(request.arity)
    _arity(certificate.arity)
    _form(request.specification, request.arity)
    _form(certificate.normal_form, certificate.arity)
    # Validate bounded syntax BEFORE structural equality of two expression trees.
    expected = normal_form(request.expression, request.arity)
    normal_form(certificate.expression, certificate.arity)
    if certificate.epoch != request.epoch:
        raise Refusal('scope/epoch mismatch')
    if certificate.arity != request.arity:
        raise Refusal('request arity mismatch')
    if certificate.expression != request.expression:
        raise Refusal('different source object, even if length laws agree')
    if certificate.normal_form != expected:
        raise Refusal('false reconstructed law')
    if expected != request.specification:
        raise Refusal('requested universal contract is false in this fragment')
    return Receipt(request, expected)


def distinguishing_lengths(a: Affine, b: Affine) -> Optional[Tuple[int, ...]]:
    """Complete counterexample procedure for unequal nonnegative affine forms.

    The zero vector detects unequal constants. Otherwise a basis vector detects
    an unequal coefficient. This is not bounded random testing.
    """
    if (type(a) is not Affine or type(b) is not Affine
            or type(a.coefficients) is not tuple or type(b.coefficients) is not tuple):
        raise Refusal('malformed affine form')
    k = len(a.coefficients)
    _arity(k)
    _form(a, k)
    _form(b, k)
    if a.constant != b.constant:
        return (0,) * k
    for i in range(k):
        if a.coefficients[i] != b.coefficients[i]:
            return tuple(int(i == j) for j in range(k))
    return None


def evaluate(e: Expr, inputs: Sequence[Sequence[int]]) -> Tuple[int, ...]:
    """Independent concrete interpreter used only by regression experiments."""
    normal_form(e, len(inputs))  # Enforce the same public syntax domain.
    values = tuple(tuple(xs) for xs in inputs)
    for xs in values:
        for n in xs:
            _nat(n, 'list element')
    def go(t: Expr) -> Tuple[int, ...]:
        if t.op == 'input':
            return values[t.index]
        if t.op == 'nil':
            return ()
        if t.op == 'cons':
            return (t.value,) + go(t.children[0])
        if t.op == 'append':
            return go(t.children[0]) + go(t.children[1])
        if t.op == 'reverse':
            return go(t.children[0])[::-1]
        if t.op == 'map_succ':
            return tuple(x + 1 for x in go(t.children[0]))
        raise AssertionError('validated syntax invariant')
    return go(e)
