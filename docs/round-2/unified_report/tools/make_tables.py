#!/usr/bin/env python3
"""Generate the data artifacts of the round-2 unified report.

Outputs (written next to the report):
  feature_matrix.csv   design commitments x nine reports (Y explicit, P partial or implicit, N absent)
  negative_suite.csv   the nine adversarial suites deduplicated into canonical mutations with provenance
  question_tally.csv   modal answers to the 22 round-1 questions and the notable variations
It also prints LaTeX table bodies that were pasted into unified_report.tex, so the two stay in step.
The marks are this reviewer's readings of the nine texts; every mark can be checked against the cited report.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
R = ["Locus", "Accord", "Cadence", "Concord", "Facet", "Meridian", "Noema", "Prism", "Vantage"]

# ---------------------------------------------------------------- feature matrix
M = [
 ("Inherited foundation", "A1", "Lean remains the checking host; no new kernel or logic", "YYYYYYYYY"),
 ("Inherited foundation", "A2", "Statement meaning is fixed before search; a producer cannot instantiate a meaning-bearing hole", "YYYYYYYYY"),
 ("Inherited foundation", "A3", "Obligations are ordered dependent telescopes with witness scope", "YYYYYYYYY"),
 ("Inherited foundation", "A4", "Methods are ordinary theorems with roles behind a project-owned wrapper", "YYYYYYYYY"),
 ("Inherited foundation", "A5", "A named reason constrains the proof; an open search reason does not", "YYYYYYYYY"),
 ("Inherited foundation", "A6", "Publication checks every formal assertion, including unused ones", "YYYYYYYYY"),
 ("Inherited foundation", "A7", "Two frontends over one typed record; a library or document view is a successful outcome", "YYYYYYYYY"),
 ("Inherited foundation", "A8", "Three-treatment evaluation with shared infrastructure and explicit cost accounting", "YYYYYYYYY"),
 ("Inherited foundation", "A9", "The corpus audit is a lexical classification, not a savings estimate", "YYYYYYYYY"),
 ("Inherited foundation", "A10", "Edits are classified as evidence, plan, object, or statement changes", "YYYYYYYYY"),
 ("Result contracts", "B1", "A computed answer is a value together with a proof of a fixed specification", "YYYYYYYYY"),
 ("Result contracts", "B2", "An explicit taxonomy of result kinds with forbidden promotions", "YYYYYYYYY"),
 ("Result contracts", "B3", "A witness is not a complete solution set; coverage is separate evidence", "YYYYYYYYY"),
 ("Result contracts", "B4", "A conditional result is an implication; guards are never promoted to hypotheses", "YYYYYYYYY"),
 ("Result contracts", "B5", "An enclosure is not an equality; an interval containing zero decides nothing", "YYYYYYYYY"),
 ("Result contracts", "B6", "A product identity is not an irreducible factorization", "YYYYPYYYY"),
 ("Result contracts", "B7", "Finite jet, full series identity, and analytic function are three different claims", "YYYYYYYYY"),
 ("Result contracts", "B8", "The mathematical kind of a result is separated from its validation state", "PYYYPYPYY"),
 ("Verified CAS", "C1", "Two lanes: a verified algorithm, and a verified checker of an untrusted certificate", "YYYYYYYYY"),
 ("Verified CAS", "C2", "A third lane: proof-producing tactics, or a candidate followed by an ordinary proof", "PPPYYYPYP"),
 ("Verified CAS", "C3", "The execution gap: a correctness theorem does not certify a particular native run", "YYYYYYYYY"),
 ("Verified CAS", "C4", "Native-computation axioms are audited by inventory, not by a blacklisted name", "YYYYYYYYY"),
 ("Verified CAS", "C5", "Reification is part of the proof boundary; opaque atoms carry exact identities", "YYYYYYYYY"),
 ("Verified CAS", "C6", "Ideal-membership certificates with their limits stated (no negative result; powers need regularity)", "YYYYYYYYY"),
 ("Verified CAS", "C7", "Accepted evidence must not depend on a remote service surviving (the polyrith lesson)", "NNYYNYYYY"),
 ("Verified CAS", "C8", "A small verified core (exact scalars, polynomials, finite sums, jets), not a universal simplifier", "YYYYYYYYY"),
 ("Verified CAS", "C9", "Search-free replay is not computation-free; checking cost is measured", "YYYYYYYYY"),
 ("Verified CAS", "C10", "Certificate size, degree, and checker cost are bounded in the protocol", "YYPPPYYPY"),
 ("Representations and definitions", "D1", "The mathematical object is a stable anchor; a representation is a certified relation to it", "YYYYYYYYY"),
 ("Representations and definitions", "D2", "Exact presentations are distinguished from information-losing observations", "YYYYYPYYY"),
 ("Representations and definitions", "D3", "Preservation along a map is distinguished from reflection back", "YYYYYYYYY"),
 ("Representations and definitions", "D4", "Guards compose as an ordered dependent telescope at the retained intermediate object", "YYYYYYYYY"),
 ("Representations and definitions", "D5", "Coherence: routes are pinned; agreement is anchor- or observation-relative; conflicts need selection", "YYYYYYYYY"),
 ("Representations and definitions", "D6", "Unit is not nonzero; a CAS may not strengthen a ring to a field", "YYYYYYYYY"),
 ("Representations and definitions", "D7", "Guarded natural subtraction and exact division as the three-view stress test", "YYYYYYYYY"),
 ("Representations and definitions", "D8", "Definition packages or templates generate proof obligations, never hidden axioms", "YYYYYYYYY"),
 ("Representations and definitions", "D9", "A normalized-coefficient (EGF) interface as an early package", "NPYPPNNYY"),
 ("Representations and definitions", "D10", "A precision calculus for jets: differentiation loses one order; substitution needs a zero constant", "YPYYYPYYY"),
 ("Representations and definitions", "D11", "Demand-driven precision planning; precision is part of the cache key", "YNPYPPYYY"),
 ("Representations and definitions", "D12", "A residual certificate identifies a finite jet with an implicitly defined series", "YNPYPYNNN"),
 ("Representations and definitions", "D13", "Partial expressions (domain, value) as an explicit opt-in semantics beside total operations", "YPPPPYPPP"),
 ("Representations and definitions", "D14", "No global canonical form; CAS results never enter definitional equality", "YYYYYYYYY"),
 ("Negative evidence and Leant", "E1", "Fragment exhaustion or a safety flag is not a negation; adequacy needs a theorem", "YYYYYYYYY"),
 ("Negative evidence and Leant", "E2", "Excluded middle as the example separating non-derivability from negation", "NNNYYNNNY"),
 ("Negative evidence and Leant", "E3", "The exact displayed edit is replayed; a smaller goal count is not completion", "YYYYYYYYY"),
 ("Negative evidence and Leant", "E4", "Leant stays a Haskell service behind a Lean-owned adapter with opaque handles", "YYYYYYYYY"),
 ("Negative evidence and Leant", "E5", "One budget for the whole request; cancellation; stale origins rejected; disposable workers", "YYYYYYYYY"),
 ("Negative evidence and Leant", "E6", "Shared metavariables are committed transactionally", "YYYPYYYYY"),
 ("Negative evidence and Leant", "E7", "A type is not a behavioral specification; finite tests certify only themselves", "YYYYYYYYY"),
 ("Negative evidence and Leant", "E8", "Leant is measured on compositions, separately from single-lemma lookup", "YYYYYYYYY"),
 ("Worked material", "F1", "Binomial inversion kernel with additive-group generality preserved", "YYYYYYYYY"),
 ("Worked material", "F2", "Autonomous derivatives with range-local hypotheses preserved", "YYYYYYYYY"),
 ("Worked material", "F3", "Abel series coefficients over an arbitrary commutative rational algebra", "NYYYYNYYN"),
 ("Worked material", "F4", "Lambert-type derivative polynomials and their recurrence", "NNYYNYNYN"),
 ("Worked material", "F5", "Radical denesting with a branch certificate", "YYYYYYYYY"),
 ("Worked material", "F6", "A certified rational enclosure of an isolated real root", "YNYPYPYYP"),
 ("Worked material", "F7", "Parameter-dependent complete solving with branch coverage", "NPYYPYNNY"),
 ("Worked material", "F8", "A ProveIt file beyond the three that the round-1 syntheses discussed", "YNNNNYYNY"),
]
assert all(len(m[3]) == 9 for m in M)


def write_matrix():
    with open(os.path.join(OUT, "feature_matrix.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["group", "id", "commitment"] + R + ["explicit", "explicit_or_partial"])
        for g, i, d, s in M:
            w.writerow([g, i, d] + list(s) + [s.count("Y"), s.count("Y") + s.count("P")])
    tot = len(M)
    unan = sum(1 for m in M if m[3].count("Y") == 9)
    seven = sum(1 for m in M if m[3].count("Y") >= 7)
    inh = [m for m in M if m[0] == "Inherited foundation"]
    new = [m for m in M if m[0] != "Inherited foundation"]
    print("matrix rows=%d unanimous=%d >=7:%d | inherited rows=%d unanimous=%d | new rows=%d unanimous=%d >=7:%d" % (
        tot, unan, seven, len(inh), sum(1 for m in inh if m[3].count("Y") == 9),
        len(new), sum(1 for m in new if m[3].count("Y") == 9), sum(1 for m in new if m[3].count("Y") >= 7)))
    sym = {"Y": r"\Yy", "P": r"\Pp", "N": r"\Nn"}
    print("% ---- feature matrix body")
    lastg = None
    for g, i, d, s in M:
        if g != lastg:
            print(r"\midrule\multicolumn{12}{@{}l}{\emph{%s}}\\" % g)
            lastg = g
        print("%s & %s & %s & %d\\\\" % (i, d, " & ".join(sym[c] for c in s), s.count("Y")))


# ---------------------------------------------------------------- consolidated negative suite
# canonical mutation, required behaviour, per-report identifiers (absent = not in that report's table)
N = [
 ("M1", "Omit the inclusive endpoint of a finite reindexing", "Coverage fails at the endpoint; the advertised method is not silently replaced by another proof",
  dict(Locus="T01", Accord="A1", Cadence="r4", Concord="r1", Facet="T4", Meridian="F1", Prism="N1", Vantage="V18")),
 ("M2", "Use a non-injective index map as a bijection", "Reject, or switch visibly to a multiplicity-aware theorem", dict(Locus="T02", Accord="A2")),
 ("M3", "Apply the finite reindexing method to an infinite sum", "Require the summability or rearrangement contract", dict(Locus="T03", Accord="A3")),
 ("M4", "Replace neighbourhood equality by equality at one point before differentiating", "Derivative transfer stays open naming the missing eventual equality; no global smoothness is added",
  dict(Locus="T04", Accord="A16", Cadence="r8", Concord="r5", Facet="T5", Meridian="A3", Noema="r2", Prism="N6", Vantage="V17")),
 ("M5", "Exchange a limit and an integral from pointwise convergence alone", "The analytic theorem's hypotheses remain explicit obligations", dict(Locus="T05", Vantage="V19")),
 ("M6", "Cancel a nonzero non-unit, or use a power certificate, in a ring with zero divisors", "Require unit or regularity evidence; do not strengthen the ring",
  dict(Locus="T06", Concord="r8", Facet="T6", Meridian="V3", Vantage="V11")),
 ("M7", "Cancel a denominator that can vanish, or evaluate a cancelled expression at the excluded point", "Keep the guard, split cases, or return a piecewise result; never publish the unconditional equality",
  dict(Locus="T07", Accord="A6", Cadence="r1", Facet="T1", Meridian="D1", Noema="r1", Prism="N4", Vantage="V10")),
 ("M8", "Forget the domain of a partial function after normalizing it", "Extension is a new object with its own agreement theorem", dict(Locus="T08", Meridian="D2")),
 ("M9", "Return the negative radical candidate with the correct square", "Reject the principal-root specification despite identical squares",
  dict(Locus="T09", Accord="A9", Cadence="r3", Concord="r6", Facet="T9", Noema="r9", Prism="N11", Vantage="V12")),
 ("M10", "Return the formal root with the wrong constant coefficient", "Reject the branch condition of the root specification", dict(Locus="T10")),
 ("M11", "Request a coefficient beyond the certified precision of a jet", "Expose the failed index bound; recompute or refine", dict(Locus="T11", Accord="A13", Vantage="V6")),
 ("M12", "Differentiate a jet and keep its input precision", "Lower the output order or request one more input coefficient",
  dict(Locus="T12", Cadence="r7", Concord="r4", Facet="T8", Noema="r3", Prism="N8", Vantage="V7")),
 ("M13", "Read a formal identity or jet as an analytic statement", "Require a convergence, realization, or remainder theorem",
  dict(Locus="T13", Accord="A15", Facet="T15", Noema="r5", Prism="N9", Vantage="V9")),
 ("M14", "Promote finitely many agreeing coefficients to a series identity or a universal formula", "Retain only the finite statement; the universal claim stays open",
  dict(Accord="A12", Cadence="r6", Facet="T7", Meridian="F2", Noema="r4")),
 ("M15", "Present verified roots as the complete solution set, or omit a root", "Soundness may pass; completeness or coverage must fail",
  dict(Locus="T14", Accord="A10", Cadence="r2", Concord="r7", Facet="T10", Meridian="C2", Noema="r10", Prism="N10", Vantage="V13")),
 ("M16", "Reuse a branch-local fact in a sibling branch, possibly through a cache", "Reject the context embedding regardless of printed similarity",
  dict(Locus="T15", Accord="A19", Facet="T14", Noema="r11", Prism="N14", Vantage="V5")),
 ("M17", "Deliver a valid result after undo or an origin change", "Mark it stale; it cannot mutate the current state",
  dict(Locus="T19", Accord="A23", Cadence="r10", Concord="r10", Facet="T14", Noema="r11", Prism="N14", Vantage="V23")),
 ("M18", "Change an instance or definition while the printed statement is unchanged", "Invalidate the seal and display the semantic change", dict(Locus="T16", Meridian="P3", Noema="r18", Prism="N18")),
 ("M19", "Import a second package with a conflicting convention or method name", "Explicit selection; no silent shadowing", dict(Accord="A25", Cadence="r14")),
 ("M20", "Let proof search instantiate a meaning-bearing statement hole", "Keep the statement unresolved or request a visible source change", dict(Locus="T17")),
 ("M21", "Cache or display suggested tactic text that differs from the tactic that was probed", "Replay the exact displayed edit from the same origin before calling it verified",
  dict(Locus="T18", Accord="A22", Cadence="r11", Concord="r10", Meridian="L2", Noema="r15", Prism="N19", Vantage="V21")),
 ("M22", "Treat a reduction in visible goals as theorem completion", "Report local progress; completion needs the root term", dict(Locus="T20", Vantage="V22")),
 ("M23", "Admit an unapproved axiom transitively, or forge an evidence tag", "Fail the publication policy even if the term typechecks",
  dict(Locus="T21", Accord="A24", Meridian="P2", Noema="r17", Prism="N20")),
 ("M24", "Accept a verified algorithm's native output without checked execution, or alter one returned coefficient", "The algorithm theorem alone is insufficient for that output",
  dict(Facet="T13", Vantage="V25")),
 ("M25", "Insert a false but unused intermediate assertion", "Reject the document even if the final theorem has another proof",
  dict(Locus="T22", Accord="A20", Cadence="r12", Facet="T11", Meridian="P1", Noema="r16", Prism="N16", Vantage="V20")),
 ("M26", "Add a constructor to a datatype handled by a structural plan", "Recompute coverage; do not reuse the stale constructor list", dict(Locus="T23")),
 ("M27", "Present search exhaustion, a timeout, or a missing status field as a refutation", "Return a non-logical outcome unless a negation is checked at the original target",
  dict(Locus="T24", Accord="A21", Cadence="r13", Facet="T12", Meridian="L3", Noema="r14", Prism="N15", Vantage="V24")),
 ("M28", "Supply a finite behavioral test for a universal specification", "Retain the finite fact; the universal obligation stays open", dict(Locus="T25")),
 ("M29", "Introduce a competing representation route", "Preserve the selected route, request a choice, or apply a checked coherence theorem", dict(Locus="T26", Meridian="V2", Vantage="V4")),
 ("M30", "Reflect an equality back along a non-injective map (modulo two, or evaluation over a finite field)", "Require reflection evidence; a homomorphism alone is insufficient",
  dict(Facet="T2,T3", Noema="r13", Vantage="V3")),
 ("M31", "Retrieve the benchmark target through an alias", "The run is invalid under the declared dependency exclusion", dict(Locus="T27", Vantage="V26")),
 ("M32", "Commit incompatible shared data assignments from sibling obligations", "Reject the transaction and restore the origin", dict(Locus="T28", Accord="A18", Meridian="L4")),
 ("M33", "Transport natural subtraction or natural division to a ring or field without its guard", "Expose the order or divisibility obligation; the natural value is not the field value",
  dict(Accord="A4,A5", Meridian="V1", Noema="r6", Prism="N2,N3", Vantage="V1,V2")),
 ("M34", "Corrupt one coefficient of a certificate (membership witness, recurrence, Sturm remainder)", "The checker rejects it regardless of the producer's report",
  dict(Accord="A8", Concord="r3", Meridian="A1", Vantage="V14")),
 ("M35", "Strengthen an additive group or rational algebra to a field to make a normalizer applicable", "A statement change, never a proof improvement",
  dict(Cadence="r5", Concord="r2", Noema="r7", Prism="N12")),
 ("M36", "Replace an arbitrary solution of a functional equation by the canonical construction", "Require an equality or uniqueness bridge, or keep the arbitrary object",
  dict(Accord="A17", Noema="r8", Prism="N13")),
 ("M37", "Feed a noncommutative expression to a commutative normalizer", "Reject the missing algebraic capability", dict(Accord="A7")),
 ("M38", "Display an enclosure as an exact decimal, or infer a sign from an interval containing zero", "The certificate stores exact bounds; a zero-containing interval is inconclusive",
  dict(Accord="A26", Cadence="r9", Concord="r9", Meridian="C3", Vantage="V16")),
 ("M39", "Solve a parameterized equation without its singular branch", "Report a conditional answer or require branch coverage", dict(Cadence="r1", Meridian="D3", Vantage="V15")),
 ("M40", "Label multiplied-back factors as irreducible", "Irreducibility needs separate evidence", dict(Meridian="C1")),
 ("M41", "Use a membership witness with rational coefficients for an integer ideal", "Reject the coefficient-domain mismatch", dict(Meridian="C4")),
 ("M42", "Acknowledge a semantic notice and treat it as discharging a guard", "A notice records a convention; it never discharges an obligation", dict(Prism="N17")),
 ("M43", "Use a result to establish the guard that justifies it", "Reject cyclic or ill-scoped assembly", dict(Noema="r12")),
 ("M44", "Bind a provider's expression to the wrong origin because names coincide", "Reject the typed origin binding", dict(Meridian="L1")),
 ("M45", "Remove an analytic hypothesis such as the non-pole condition, or use a rational form at its pole", "Expose the unresolved requirement; the header must not strengthen itself",
  dict(Meridian="A2", Prism="N7")),
 ("M46", "Substitute a series with nonzero constant term into the simple composition rule", "Generate the admissibility obligation or use a stronger precision theorem", dict(Accord="A14", Vantage="V8")),
 ("M47", "Use a conditional result unconditionally, or exchange dependent witness quantifiers", "Reject the scope or dependency change", dict(Facet="T16")),
 ("M48", "Force an already-short corollary into a longer narrative", "New syntax must not add declarations or explanation", dict(Concord="r11")),
 ("M49", "Multiply a strict inequality by a merely nonnegative factor", "Require strict positivity or handle the zero case", dict(Prism="N5")),
 ("M50", "Infer equality of algebraic numbers from a shared defining polynomial", "Require matching root identity or isolation evidence", dict(Accord="A11")),
 ("M51", "Specialize a guarded generic computation at a value where the guard fails", "Reinstantiate the guard and locate its origin", dict(Meridian="D4")),
]


def write_suite():
    with open(os.path.join(OUT, "negative_suite.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "mutation", "required_behaviour", "suites"] + R)
        for i, m, b, prov in N:
            w.writerow([i, m, b, len(prov)] + [prov.get(r, "") for r in R])
    counts = sorted(((len(p), i) for i, _, _, p in N), reverse=True)
    print("suite rows=%d provenance entries=%d core(>=7)=%s five-or-six=%s" % (
        len(N), sum(len(p) for *_, p in N), [i for c, i in counts if c >= 7], [i for c, i in counts if 5 <= c <= 6]))
    print("% ---- suite body (rows in at least five suites)")
    for i, m, b, prov in sorted(N, key=lambda x: -len(x[3])):
        if len(prov) >= 5:
            print("%s & %s & %s & %d\\\\" % (i, m, b, len(prov)))


# ---------------------------------------------------------------- question tally
Q = [
 ("S1", "Smallest useful step contract", "An ordinary theorem behind a project-owned wrapper with roles; a richer computational interface only for algorithms, certificates, dependent outputs, or precision", "Cadence and Prism name three implementation families (theorem, computation, structural plan); Locus adds a fourth request purpose (tactic edit)"),
 ("S2", "Does a stated reason constrain the proof?", "Yes for a named method; an explicit open search does not; a different proof is a visible plan edit", "Unanimous"),
 ("S3", "Which choices may automation make?", "Proof evidence and certified representation changes of the same retained object; new witnesses, branches, motives, structures, and statements are reviewable", "Prism adds delegation by specification as a third automatic class"),
 ("S4", "What does a verified suggestion guarantee?", "The exact displayed edit replayed from its origin, with progress, root completion, and policy as separate receipts", "Cadence and Meridian enumerate four statuses; Prism three; Locus and Vantage give step-by-step protocols"),
 ("S5", "How is infrastructure cost counted?", "Share every wrapper, algorithm, and checker with the Lean baseline; report L, A_i, R_i and observed reuse", "Unanimous; Facet adds a five-arm nested design"),
 ("S6", "How do views compose?", "Ordered dependent guards at the retained intermediate object; pinned routes; coherence only at a shared anchor or registered observation", "Vantage and Prism prove anchor-relative coherence; Cadence proves it per observation; none proposes global confluence"),
 ("S7", "What protects statement fidelity?", "Render domains, quantifier dependence, structures, branches, precision; notices are distinct from obligations", "Unanimous"),
 ("S8", "What survives replay and upgrades?", "Retained terms or certificates are authoritative for the pinned environment; source is a companion; an upgrade yields a new receipt", "Prism names three replay levels; Meridian three retained evidence forms"),
 ("S9", "How do definitions and observational replacement enter?", "Specification templates with proved interface lemmas and pinned representatives; replacement only with explicit transport evidence", "First template differs: formal series (Locus, Concord, Facet, Noema), partial expressions and polynomials (Meridian), EGF coordinates (Prism, Vantage), finite sums and jets (Accord, Cadence)"),
 ("S10", "What belongs in the published view?", "Choices and substantial premises visible; routine evidence collapsed but present; rejected alternatives optional", "Unanimous; Prism adds a representation view; Meridian proposes contract-surprise and guard-surprise measures"),
 ("B1", "Document view or input form?", "Both, over one typed record; lift existing Lean first; keep only the view if authoring does not improve", "Unanimous"),
 ("B2", "How much of the routine profile is routine?", "Instrument actual attempts under fixed budgets; lexical counts cannot answer", "Unanimous"),
 ("B3", "Where does analysis plumbing belong?", "A composite ordinary theorem for locality and derivative transfer; symbolic differentiation is a separate provider", "Unanimous"),
 ("B4", "Do annotated theorems survive refactoring?", "Roles on a project-owned typed wrapper checked against the telescope; neither position nor binder name alone", "Unanimous; Prism proposes a versioned wrapper schema"),
 ("B5", "How is a notice dismissed?", "Per resolved expression or explicit project convention, keyed to meaning; dismissal never discharges a guard; a semantic change invalidates it", "Unanimous"),
 ("B6", "What is the unit of replay?", "A typed node with retained evidence in a pinned environment; certificate replay and term replay are distinct modes", "Unanimous"),
 ("B7", "Is Leant's three-way outcome enough for every provider?", "Adopt a structured taxonomy, keep abstraction diagnostics separate from proof dependencies, require checked negative evidence", "Concord, Facet, and Vantage add the excluded-middle argument that non-derivability is not negation"),
 ("B8", "Is structural synthesis worth an adapter?", "Measure compositions separately from single-lemma lookup; keep the adapter optional", "Unanimous"),
 ("B9", "What does a data hole look like when published?", "The accepted object and its full specification; alternatives are optional exploration history", "Unanimous"),
 ("B10", "Where does the definition layer start?", "Two or three templates (formal series, finite family, algebraic object, EGF), not a definition language", "Same spread as S9"),
 ("B11", "Who owns conflicting contracts?", "Namespaced, versioned packages with owners; lexical selection; never import order", "Unanimous"),
 ("B12", "What is the stopping rule?", "A library, certificate API, or document renderer is a success; new syntax must earn its place in the shared-library comparison", "Unanimous"),
]


def write_questions():
    with open(os.path.join(OUT, "question_tally.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "question", "modal_answer", "variation"])
        for row in Q:
            w.writerow(row)
    print("questions=%d" % len(Q))


if __name__ == "__main__":
    write_matrix()
    write_suite()
    write_questions()
