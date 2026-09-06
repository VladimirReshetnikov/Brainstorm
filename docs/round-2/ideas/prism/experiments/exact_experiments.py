#!/usr/bin/env python3
"""Exact arithmetic experiments accompanying the Prism design article.

This is an executed Python model, NOT a formally verified checker or a Lean
implementation.  It checks finite algebraic evidence using fractions.Fraction.
The universal mathematical arguments are in the article.  All randomness is
seeded and all reported tests are deterministic.  Requires Python >= 3.9.
"""
from __future__ import annotations
import argparse
import json
import math
import random
from fractions import Fraction as Q
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

Poly = Tuple[Q, ...]  # Ascending coefficient order; zero is the empty tuple.

def poly(xs: Iterable[Q]) -> Poly:
    a = list(map(Q, xs))
    while a and a[-1] == 0:
        a.pop()
    return tuple(a)

def add(a: Poly, b: Poly) -> Poly:
    return poly((a[i] if i < len(a) else Q(0)) +
                (b[i] if i < len(b) else Q(0))
                for i in range(max(len(a), len(b))))

def scale(c: Q, a: Poly) -> Poly:
    return poly(c*x for x in a)

def sub(a: Poly, b: Poly) -> Poly:
    return add(a, scale(Q(-1), b))

def mul(a: Poly, b: Poly) -> Poly:
    if not a or not b:
        return ()
    out = [Q(0)]*(len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return poly(out)

def power(a: Poly, n: int) -> Poly:
    if n < 0:
        raise ValueError('polynomial powers require a nonnegative exponent')
    out = poly([1])
    while n:
        if n & 1:
            out = mul(out, a)
        a = mul(a, a)
        n //= 2
    return out

def deriv(a: Poly) -> Poly:
    return poly(i*a[i] for i in range(1, len(a)))

def evaluate(a: Poly, x: Q) -> Q:
    out = Q(0)
    for c in reversed(a):
        out = out*x + c
    return out

def generate_lambert(count: int) -> List[Poly]:
    """Candidate producer. The independent algebraic check below uses quotients."""
    if count < 1:
        raise ValueError('count must be positive')
    result = [poly([1])]
    for n in range(1, count):
        p = result[-1]
        result.append(sub(mul(poly([1, 1]), deriv(p)),
                          mul(poly([3*n - 1, n]), p)))
    return result

def check_lambert_step(n: int, p: Poly, candidate: Poly) -> bool:
    """Check the cross-multiplied rational derivative identity.

    For B=(1+w)^(2n-1), the rational part of
      (d/dw [exp(-n*w)*p/B])*exp(-w)/(1+w)
    is (p'*B-p*B'-n*p*B)/(B^2*(1+w)).
    Equality with candidate/(1+w)^(2n+1) is checked by cross multiplication.
    The analytic interpretation REQUIRES w != -1 and the usual derivative laws.
    This function certifies neither that guard nor the analytic laws in Lean.
    """
    if n < 1:
        return False
    w1 = poly([1, 1])
    b = power(w1, 2*n - 1)
    numerator = sub(sub(mul(deriv(p), b), mul(p, deriv(b))),
                    scale(Q(n), mul(p, b)))
    left = mul(numerator, power(w1, 2*n + 1))
    right = mul(candidate, mul(mul(b, b), w1))
    return left == right

def rat_text(x: Q) -> str:
    return str(x.numerator) if x.denominator == 1 else f'{x.numerator}/{x.denominator}'

# Dual numbers over Q: (a,b) represents a+b*epsilon with epsilon^2=0.
Dual = Tuple[Q, Q]
ZERO: Dual = (Q(0), Q(0))
def dadd(a: Dual, b: Dual) -> Dual:
    return (a[0]+b[0], a[1]+b[1])
def dmul(a: Dual, b: Dual) -> Dual:
    return (a[0]*b[0], a[0]*b[1]+a[1]*b[0])
def dscale(c: Q, a: Dual) -> Dual:
    return (c*a[0], c*a[1])
def dsum(xs: Iterable[Dual]) -> Dual:
    z = ZERO
    for x in xs:
        z = dadd(z, x)
    return z

def run(outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    counts = {}
    certs = {'scope': 'Finite exact arithmetic; not a formal proof artifact.'}
    ps = generate_lambert(9)
    assert ps[:4] == [poly([1]), poly([-2,-1]), poly([9,8,2]),
                      poly([-64,-79,-36,-6])]
    assert all(check_lambert_step(n, ps[n-1], ps[n]) for n in range(1,9))
    counts['lambert_cross_multiplied_steps'] = 8
    for n in range(1,9):
        bad = add(ps[n], poly([1]))
        assert not check_lambert_step(n, ps[n-1], bad)
    assert not check_lambert_step(0, ps[0], ps[1])
    counts['lambert_mutations_rejected'] = 9
    certs['lambert_polynomials_ascending'] = [list(map(rat_text,p)) for p in ps]

    count = 0
    for n in range(25):
        for j in range(25):
            lhs = sum((-1)**(n-k)*math.comb(n,k)*math.comb(k,j)
                      for k in range(j,n+1))
            assert lhs == int(n == j)
            count += 1
    counts['binomial_orthogonality_pairs'] = count
    # Finite universes here exercise general-ring transport, not a universal proof.
    count = 0
    for modulus in (4,6,8):
        for n in range(16):
            for j in range(16):
                lhs = sum((-1)**(n-k)*math.comb(n,k)*math.comb(k,j)
                          for k in range(j,n+1)) % modulus
                assert lhs == int(n == j) % modulus
                count += 1
    counts['binomial_zero_divisor_ring_pairs'] = count

    rng = random.Random(20260905)
    count = 0
    for _ in range(40):
        a = [(Q(rng.randrange(-5,6)), Q(rng.randrange(-5,6))) for _ in range(13)]
        b = [(Q(rng.randrange(-5,6)), Q(rng.randrange(-5,6))) for _ in range(13)]
        for n in range(13):
            egf_product = dsum(dmul(dscale(Q(1,math.factorial(k)),a[k]),
                                    dscale(Q(1,math.factorial(n-k)),b[n-k]))
                               for k in range(n+1))
            binomial = dsum(dscale(Q(math.comb(n,k)),dmul(a[k],b[n-k]))
                            for k in range(n+1))
            assert egf_product == dscale(Q(1,math.factorial(n)),binomial)
            assert dscale(Q(math.factorial(n)), dscale(Q(1,math.factorial(n)),a[n])) == a[n]
            count += 1
    counts['egf_dual_number_coefficient_checks'] = count
    counts['egf_dual_number_roundtrip_checks'] = count

    for n in range(1,21):
        f = poly([0]*n+[1])
        assert all(c == 0 for c in f[:n])  # f == 0 to precision n.
        assert deriv(f)[n-1] == n          # differentiation loses a coefficient.
    counts['jet_precision_counterexamples'] = 20

    p = poly([-1,-1,0,1])
    lo,hi = Q(1324717,10**6),Q(1324718,10**6)
    flo,fhi = evaluate(p,lo),evaluate(p,hi)
    assert flo < 0 < fhi and Q(1) < lo < hi < Q(2)
    assert hi-lo == Q(1,10**6)
    certs['root_bracket'] = {'polynomial':list(map(rat_text,p)),
                            'lower':rat_text(lo),'upper':rat_text(hi),
                            'value_lower':rat_text(flo),'value_upper':rat_text(fhi),
                            'midpoint':rat_text((lo+hi)/2),
                            'midpoint_error_bound':rat_text((hi-lo)/2),
                            'analytic_bridge':'IVT and strict increase on [1,2], proved in the article.'}
    counts['root_endpoint_signs'] = 2
    assert max(2-3,0) != Q(2)-Q(3)
    assert Q(1//2) != Q(1,2)
    def total_div(a: Q,b: Q) -> Q:
        return a/b if b else Q(0)
    assert total_div(Q(1)**2-1,Q(1)-1) != Q(1)+1
    assert total_div(Q(1)**2-1,Q(1)-1) == 0
    counts['guard_counterexamples'] = 3
    results = {
        'status':'passed',
        'runtime':'Python standard-library exact rational arithmetic',
        'formal_verification':False,
        'lean_or_leant_executed':False,
        'seed':20260905,
        'counts':counts,
        'total_reported_checks':sum(counts.values()),
        'limitations':[
            'Finite tests are not proofs of the universal mathematical theorems.',
            'Python arithmetic and this checker have not been formally verified.',
            'Analytic bridges and guards are paper proofs, not checked by this program.',
            'No claim is made about language usability or Lean integration performance.'
        ]}
    (outdir/'certificates.json').write_text(json.dumps(certs,indent=2)+'\n',encoding='utf-8')
    (outdir/'results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    return results

def main() -> None:
    if not __debug__:
        raise SystemExit('Run without -O: this experiment uses assertions as checks.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print(json.dumps(run(args.out),indent=2))

if __name__ == '__main__':
    main()
