#!/usr/bin/env python3
"""Exact differential-polynomial reference for inverse derivatives.

Computes P_1=1, P_(n+1)=u_1 D(P_n)-(2n-1)u_2 P_n, where
D(u_j)=u_(j+1). Coefficients are exact integers. This Python program is not
formally verified; the article proves the recurrence mathematically. It does
not assert that a particular analytic function meets the hypotheses.
"""
from __future__ import annotations
import json
from pathlib import Path

Exponent = tuple[int, ...]
Polynomial = dict[Exponent, int]

def add(p: Polynomial, q: Polynomial) -> Polynomial:
    r = dict(p)
    for e, c in q.items():
        r[e] = r.get(e, 0) + c
        if r[e] == 0:
            del r[e]
    return r

def scale(p: Polynomial, c: int) -> Polynomial:
    return {e: a*c for e,a in p.items() if a*c}

def variable_mul(p: Polynomial, j: int) -> Polynomial:
    r = {}
    for e,c in p.items():
        f=list(e); f[j]+=1; r[tuple(f)]=c
    return r

def differential(p: Polynomial) -> Polynomial:
    r: Polynomial = {}
    for e,c in p.items():
        for j in range(len(e)-1):
            if e[j]:
                f=list(e); f[j]-=1; f[j+1]+=1
                r=add(r,{tuple(f):c*e[j]})
        if e[-1]:
            raise ValueError('insufficient variable arity for differentiation')
    return r

def polynomials(order: int) -> list[Polynomial]:
    if not 1 <= order <= 12:
        raise ValueError('reference cap: order must be between 1 and 12')
    p: Polynomial = {(0,)*(order+1):1}
    out=[p]
    for n in range(1,order):
        p=add(variable_mul(differential(p),0),
              scale(variable_mul(p,1),-(2*n-1)))
        out.append(p)
    return out

def render(p: Polynomial) -> str:
    terms=[]
    for e,c in sorted(p.items(),reverse=True):
        monomial='*'.join(f'u{j+1}'+(f'^{k}' if k!=1 else '') for j,k in enumerate(e) if k)
        terms.append(str(c)+(('*'+monomial) if monomial else ''))
    return ' + '.join(terms).replace('+ -','- ') or '0'

def main() -> None:
    ps=polynomials(6); arity=7
    def poly(*terms):
        return {tuple(e)+(0,)*(arity-len(e)):c for c,e in terms}
    expected=[poly((1,())), poly((-1,(0,1))),
              poly((3,(0,2)),(-1,(1,0,1))),
              poly((-15,(0,3)),(10,(1,1,1)),(-1,(2,0,0,1)))]
    assert ps[:4]==expected
    # Two structural invariants proved by the recurrence in the article:
    # ordinary degree n-1, and sum_j j*exponent_j = 2n-2.
    terms_checked=0
    for n,p in enumerate(ps,1):
        for exponents in p:
            assert sum(exponents)==n-1
            assert sum((j+1)*e for j,e in enumerate(exponents))==2*n-2
            terms_checked+=1
    result={'order':6,'first_four_formula_comparisons':4,
            'monomial_invariant_checks':2*terms_checked,
            'polynomials':[{'n':n,'terms':len(p),'P':render(p)} for n,p in enumerate(ps,1)],
            'status':'exact Python reference; not kernel-checked analytic identities'}
    Path(__file__).with_name('inverse-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
