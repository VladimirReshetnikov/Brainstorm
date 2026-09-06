"""Data behind the round-3 unified report.

Writes feature_matrix.csv, negative_suite.csv, question_tally.csv, lean_cores.csv
into the report directory and prints the counts quoted in the text.

Report order everywhere: Basalt, Fiber, Gneiss, Karst, Moraine, Obsidian, Schist, Tephra, Trellis.
Marks: Y = stated as a commitment, P = partial or implicit, N = absent.
"""
import csv
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
REPORTS = ["Basalt", "Fiber", "Gneiss", "Karst", "Moraine", "Obsidian", "Schist", "Tephra", "Trellis"]

# ---------------------------------------------------------------- commitment matrix
# (id, statement, marks in report order)
M = [
 ("A1", "Extend the elaborator's typing discipline first; the kernel is unchanged in the first implementation", "YYYYYYYYY"),
 ("A2", "Lean already expresses the properties (subtypes, structures, dependent functions); no new logic is claimed", "YYYYYYYYY"),
 ("A3", "A primitive kernel refinement is a later, measured experiment, never a prerequisite", "PYYYYYYYY"),
 ("A4", "No semantic subtyping or equality reflection in conversion; no CAS inside definitional equality", "YYYYYYYYY"),
 ("A5", "No principal or strongest refinement is promised; automatic inference is a bounded fragment", "YYYYYYYYY"),
 ("A6", "Failure to infer a property is not evidence that it is false", "YYYYYYYYY"),
 ("B1", "A proved property enriches the same term; the object is never rebound to a subtype locally", "YYYYYYYYY"),
 ("B2", "Packaging into a subtype or record happens only at an interface boundary", "YYYYYYYYY"),
 ("B3", "Weakening a refinement applies a proved implication and preserves the value", "YYYYYYYYY"),
 ("B4", "Several properties of one carrier are a conjunction, not an intersection of unrelated types", "YYYYYYYYY"),
 ("B5", "Equality transports properties by elimination; any other relation needs its registered transport theorem", "YYYYYYYYY"),
 ("B6", "An anchor is the elaborated term with its structures and context, never a printed name", "YYYYYYYYY"),
 ("B7", "Branch-local facts do not leak to siblings; leaving a branch exports an implication, not the fact", "YYYYYYYYY"),
 ("B8", "A written relative-soundness theorem: the core rules translate to ordinary Lean terms without new axioms", "YYYYYYYYY"),
 ("B9", "Meaning-bearing holes are frozen before search; a delegated data hole is allowed only under a fixed specification", "YYYYYYYYY"),
 ("C1", "Selecting a structure (ring, topology, action) is data and is separate from inferring propositions about it", "YYYYYYYYY"),
 ("C2", "No global instance per derived fact; a local instance bridge is inserted only where an API demands one", "YYYYYYYYY"),
 ("C3", "A lexical structure context or manifest fixes the dictionaries a block uses", "PPPYPPYYY"),
 ("C4", "Nonzero, regular, and unit are three predicates; no silent field assumption", "YYYYPYYYY"),
 ("D1", "A behavioral contract on a total function is: for all x, P x implies Q x (f x)", "YYYYYYYYY"),
 ("D2", "Contract variance: preconditions contravariant, postconditions covariant; no single strength rank", "YYYYYPYYY"),
 ("D3", "Composition retains the actual intermediate value and needs a bridge to the next precondition", "YYYYYYYYY"),
 ("D4", "Relational and higher-order laws (monotone, respects, naturality, inverse pair) are contracts on the whole function", "YYYYYYYYY"),
 ("D5", "A function on a refined domain and a total function with a contract are different interfaces", "YYYYYPYYY"),
 ("D6", "Sorting needs permutation and order; length preservation admits reversal and constant lists", "YYYYYYYYY"),
 ("D7", "Effectful programs get a separate axis (Hoare logic, mvcgen); a timeout or cost is not a mathematical premise", "PPYPPYYPY"),
 ("D8", "Existence in Prop does not yield executable data without a construction or a declared choice", "YYYYYYYYY"),
 ("E1", "Equality on an open set at an interior point yields eventual equality; equality at the point does not", "YYYYYYYYY"),
 ("E2", "Almost-everywhere equality is a further distinct relation with its own consumers", "YYYNNYNNN"),
 ("E3", "A derivative jet loses one order: input N+1 for output N", "YYYYYYYYY"),
 ("E4", "Residual certificates identify a jet of the selected root only with matching constant term and unit derivative", "YYYYPYYYY"),
 ("E5", "A universal claim needs the quantifier; finitely many prefixes, coefficients, or tests do not deliver it", "YYYYYYYYY"),
 ("E6", "Preservation is not reflection: X lies in (2X) over Q[X] but not over Z[X]", "YYYNNYNYY"),
 ("E7", "Complete solving needs soundness and coverage of the same predicate", "YYYYNYYYY"),
 ("E8", "An enclosure with equal endpoints may prove equality; a generic enclosure may not", "YYYNNYNYY"),
 ("E9", "Quantitative contracts (closeness, Lipschitz transfer, vanishing error) propagate demanded precision backward", "NYNNYNNNY"),
 ("F1", "Inference is demand-driven from the premises of the chosen method", "YYYYYYYYY"),
 ("F2", "A small forward closure of cheap consequences; no saturation over all consequences", "YYPPYYYYY"),
 ("F3", "A registered rule is an ordinary theorem plus role metadata validated against its actual type", "YYYYYYYYY"),
 ("F4", "The obligation graph is acyclic; a result never justifies its own guard; induction is a separate checked rule", "YYYYYYYYY"),
 ("F5", "Diagnostics name the missing mathematical premise and say `required by this method', not `necessary'", "YYYYYYYYY"),
 ("F6", "Existing automation (fun_prop, grind, aesop, mvcgen) is a named component or baseline", "PPPPYYPPP"),
 ("F7", "A named reason binds the method used; `search' or `hint' delegates it visibly", "YYYYYYYYY"),
 ("G1", "A polynomial certificate checker is specified with a denotation into an arbitrary commutative ring", "YYYYNYPYP"),
 ("G2", "Arity is checked before any zip; a truncating zip is not an interface", "YYYYYYNYY"),
 ("G3", "Reification binds atoms to exact elaborated terms and proves the bridge to the original goal", "YYYYYYPYY"),
 ("G4", "Execution of the checker is a separate obligation; native evaluation needs an axiom audit, not a name blacklist", "YYYYYYYYY"),
 ("G5", "grobner is a bounded proof-producing provider and control; no certificate export is assumed", "PYYYPYYYY"),
 ("G6", "A certificate for p^k does not give p = 0; a rational witness is not an integer witness", "YYPYNPYYP"),
 ("G7", "Imported Lean keeps total operations; partial expressions are an explicit, domain-carrying package", "YYYYYYYYY"),
 ("G8", "No native-versus-kernel threshold is claimed from the round-2 timings", "YYYYYYYYY"),
 ("H1", "Leant's Verified wrapper is a callback receipt, not behavioral evidence or a kernel proof", "YYYYYYYYY"),
 ("H2", "Leant's Length handoff and behavioral selection are real infrastructure, read from source", "YYYYYYYYY"),
 ("H3", "A provider law becomes evidence only when paired with a Lean theorem about the exact provider term", "YPPPYPPYY"),
 ("H4", "An abstract counterexample must be realizable at the source type (the List Empty case)", "YNPYPPPYN"),
 ("H5", "A checked counterexample refutes one candidate, never the existence of a correct one", "YYYPYPPYY"),
 ("H6", "Non-derivability in a calculus is not negation of the original proposition", "YYYYYYYYY"),
 ("H7", "A tactic suggestion is verified only by replaying the exact displayed edit at its origin", "YYYYYYYYY"),
 ("H8", "Measure Leant on generated obligations, separating single-lemma lookup from composition", "YYYYYYYYY"),
 ("H9", "Polymorphism is not parametricity in classical Lean; no free theorem is inferred", "YNNNNNNYN"),
 ("I1", "The FLT Frey package is cited as evidence that Lean already bundles mathematical properties", "NYYYNYYYY"),
 ("I2", "Frey coefficients: integer division and rational division agree only under proved divisibility", "NYYYNYYYY"),
 ("I3", "The generated instance preamble is environment cost, not mathematical verbosity", "NYYYNNYYY"),
 ("I4", "The terminal FLT contradiction is already short and must stay short", "PYNYNNYYY"),
 ("I5", "The autonomous-derivative theorem is kept as a locality control", "YYYPYYYYP"),
 ("I6", "PROOF-PATH names are not statement strengths; interfaces bind to exact declarations", "YYYYNPYYY"),
 ("J1", "Evaluation arms separate library, services, property typing, and surface syntax", "YYYYYYYYY"),
 ("J2", "Development examples are not held-out tests", "YYYYYYYYY"),
 ("J3", "A blind reading test precedes the expanded view", "YYYYYYYYY"),
 ("J4", "Every displayed assertion is checked, including ones the final proof does not use", "YYYYYYYYY"),
 ("J5", "The default display shows every condition that changes the claim", "YYYYYYYYY"),
 ("J6", "Merging: new properties of one object coexist; different witnesses or structures are semantic conflicts", "YYYYYYYNN"),
 ("J7", "Upgrades recheck at the destination toolchain with a new receipt", "YYYYYYYYY"),
 ("J8", "A library-only or renderer-only outcome is a success; syntax must earn its place", "YYYYYYYYY"),
 ("J9", "No productivity or compression number is claimed", "YYYYYYYYY"),
 ("J10", "The report states that its Lean file was not compiled and that its companion is finite evidence", "YYYYYYYYY"),
]

# Rows that were already consensus in the round-2 syntheses (the round-2 matrix or its promotion table).
INHERITED = {"A6", "B7", "B9", "C4", "E1", "E3", "E4", "E5", "E6", "E7", "E8", "F4", "F7",
             "G1", "G3", "G4", "G5", "G6", "G7", "G8", "H1", "H6", "H7", "H8", "I5",
             "J1", "J2", "J3", "J4", "J5", "J7", "J8", "J9"}

# ---------------------------------------------------------------- negative suite
# (id, mutation, required response, inherits round-2 id or "", per-report source rows)
N = [
 ("N1", "Differentiate from equality at one point instead of on a neighbourhood", "The derivative step stays open naming the missing eventual equality", "M4",
  dict(Basalt="Local differentiation", Fiber="T5", Gneiss="Point equality differentiated", Moraine="Point equality", Obsidian="Neighbourhood equality", Schist="Local differentiation", Tephra="Locality", Trellis="Local transport")),
 ("N2", "Specialise the induction hypothesis to one point before the successor step", "The successor step cannot claim an on-set or neighbourhood equality", "",
  dict(Moraine="Induction hypothesis")),
 ("N3", "Invert a nonzero or regular element as if it were a unit", "Cancellation may use regularity; inversion needs unit evidence", "M6",
  dict(Fiber="T15", Gneiss="Nonunit cancellation", Karst="T9", Tephra="Algebraic structure")),
 ("N4", "Differentiate a jet and keep the input precision", "Lower the output order or request one more input coefficient", "M12",
  dict(Basalt="Precision", Gneiss="Overstated jet precision", Karst="T11", Obsidian="Extra derivative coefficient", Schist="Jet differentiation", Tephra="Jet precision")),
 ("N5", "Return the wrong root branch, or use a nonunit derivative, with a correct residual", "Reject the residual bridge at the branch or unit premise", "M10",
  dict(Basalt="Root observation", Gneiss="Wrong residual-root branch", Karst="T12", Schist="Residual certificate", Tephra="Regular branch")),
 ("N6", "Present a finite jet as an exact or analytic identity", "Keep the finite guarantee; the infinite claim stays open", "M13",
  dict(Fiber="T20", Gneiss="Jet presented as exact", Trellis="Observation kind")),
 ("N7", "Count a witness plus coverage as complete solving", "Demand soundness for every listed solution", "M15",
  dict(Basalt="Complete solving", Fiber="T21", Gneiss="Incomplete root set", Tephra="Complete solving")),
 ("N8", "Infer equality from an interval with unequal endpoints, or reject it when they coincide", "Accept only the equal-endpoint bridge", "M38",
  dict(Basalt="Enclosure", Fiber="T22", Gneiss="Noncollapsed bounds")),
 ("N9", "Reuse a branch-local fact in a sibling branch by printed name or cache", "Reject the context embedding", "M16",
  dict(Basalt="Revision", Fiber="T16", Gneiss="Wrong anchor or sibling scope", Karst="T1, T3", Moraine="Sibling branch", Obsidian="Sibling branch", Schist="Refinement scope", Tephra="Scope", Trellis="Context discipline")),
 ("N10", "Use a result to justify the guard that authorises it", "Reject cyclic assembly; induction uses a checked rule", "M43",
  dict(Gneiss="Self-justifying guard", Karst="T16", Moraine="Self-conditional guard", Obsidian="Own prerequisite", Schist="Guard handling", Tephra="Guard dependency", Trellis="Rule closure")),
 ("N11", "Change the selected structure, action, measure, or instance under unchanged notation", "Old evidence is unusable without a transport theorem; report a statement change", "M18",
  dict(Fiber="T17", Karst="T2", Moraine="Different action or scalar structure", Obsidian="Different measure or topology", Schist="Structure choice", Tephra="Chosen action", Trellis="Structure stability")),
 ("N12", "Let proof search fill a meaning-bearing hole to ease the goal", "Keep the statement unresolved", "M20",
  dict(Gneiss="Meaning-bearing hole")),
 ("N13", "Combine a curve, level, and transfer proof chosen in incompatible witness scopes", "Reject the flattened existentials", "M47",
  dict(Gneiss="Data chosen in one branch")),
 ("N14", "Corrupt a certificate coefficient or mismatch multiplier arity", "The checker rejects before any zip", "M34",
  dict(Basalt="Certificate shape", Fiber="T12, T13", Gneiss="Certificate corruption", Karst="T13", Moraine="Corrupt coefficients, truncation", Obsidian="Corrupted multipliers", Schist="Corrupted certificate", Tephra="Polynomial witness", Trellis="Corrupted coefficients, length")),
 ("N15", "Offer a rational multiplier for an integer ideal", "Reject the coefficient-domain change", "M41",
  dict(Basalt="Ring capability", Obsidian="Noninteger coefficients", Tephra="Coefficient domain")),
 ("N16", "Feed a noncommutative expression to the commutative checker", "Reject the missing ring contract", "M37",
  dict(Basalt="Ring capability", Obsidian="Missing commutative-ring contract")),
 ("N17", "Accept a native byte-string result without execution evidence or outside the axiom profile", "Algorithm correctness alone authorises nothing", "M24",
  dict(Gneiss="Native result without execution evidence", Karst="T14", Moraine="Native evaluation vs axiom profile")),
 ("N18", "Reify an opaque atom under the wrong valuation, or merge two atoms with one name", "Rebuild and prove the original-expression bridge", "M44",
  dict(Fiber="T23", Karst="T15", Trellis="Distinct atom applications")),
 ("N19", "Accept a length-preserving candidate as a sorter", "Permutation and order obligations stay open", "M28",
  dict(Basalt="Abstraction strength", Fiber="T8, T9", Karst="T5", Moraine="Candidate retained by a filter", Schist="Behavioral synthesis", Trellis="Function synthesis")),
 ("N20", "Use a finite sample bank or model-relative result as a universal proof", "Retain bounded evidence only", "M28",
  dict(Fiber="T10", Gneiss="Finite behavioral sampling", Schist="Construction")),
 ("N21", "Use a passive provider law (Length contract metadata) as a theorem", "No proof authority without a Lean theorem about the exact provider", "",
  dict(Basalt="Behavior", Tephra="Behavioral abstraction")),
 ("N22", "Refute a List Empty contract with an unrealisable positive length", "Not a refutation; a typed concrete input is required", "",
  dict(Basalt="Negative evidence", Karst="T6", Tephra="Counterexample")),
 ("N23", "Grant a polymorphic function a free theorem", "No automatic uniformity in classical Lean", "",
  dict(Tephra="Uniformity")),
 ("N24", "Refute one completion, then reject every completion of the sketch", "Require a universally scoped exclusion or label the heuristic", "",
  dict(Fiber="T11")),
 ("N25", "Cast an inexact integer quotient as a rational quotient, or drop a Frey divisibility premise", "Require divisibility and a nonzero denominator; show the failing neighbour", "M33",
  dict(Fiber="T1, T2, T3, T4", Gneiss="Integer quotient cast", Karst="T10", Obsidian="Remove a divisibility premise", Schist="Frey-model transport", Trellis="Exact quotient cast")),
 ("N26", "Test an arithmetic contract only inside a contradictory package", "Mark the run vacuous; test under satisfiable premises", "",
  dict(Fiber="T24", Obsidian="Contradictory package")),
 ("N27", "Extract an executable enumeration from proposition-valued finiteness", "The proposition-level theorem succeeds; execution needs data", "",
  dict(Karst="T4")),
 ("N28", "Extend a function on a refined domain to the whole carrier without data", "Restriction of a total function succeeds; extension needs a construction", "",
  dict(Karst="T7")),
 ("N29", "Restrict a map or an action to a subset without the preservation proof, or induce a group on a set omitting zero", "Supply the map-into or closure proof; no structure otherwise", "",
  dict(Karst="T8", Tephra="Subtype structure")),
 ("N30", "Reverse a one-sided inverse on sequences without prefix locality (the left shift)", "No finite-restriction adapter; identify the missing causality", "",
  dict(Gneiss="One-sided inverse on sequences", Tephra="Prefix observation, Finite algebra")),
 ("N31", "Label objectwise equivalences natural, or a diagram exact, from vertex data alone", "The naturality, square, or middle-exactness obligation stays open", "",
  dict(Basalt="Diagram transport, Middle exactness, Tensor exactness", Moraine="Objectwise equivalences, Inverse law omitted")),
 ("N32", "Label endpoint deletion as equality, or reindex negative indices through toNat", "Accept the norm-error contract; the bijection obligation fails", "",
  dict(Moraine="Endpoint deletion, toNat collision")),
 ("N33", "Exchange a sum and an integral from pointwise convergence", "The L1-summable family contract is required; the pulse series refutes the weaker rule", "M5",
  dict(Obsidian="Pointwise convergence")),
 ("N34", "Change the measure or topology under an integrability or domination fact", "Require a transport theorem", "",
  dict(Fiber="T6", Obsidian="Different measure")),
 ("N35", "Merge uncountably many almost-everywhere statements, or take an a.e. derivative for an everywhere one", "Require a separate uniform theorem; the Dirac step CDF refutes the promotion", "",
  dict(Basalt="Derivative scope", Fiber="T7")),
 ("N36", "Apply CDF reflection symmetry to a measure with an atom", "Return the atom-corrected identity; unconditional symmetry fails for Dirac", "",
  dict(Basalt="Boundary mass")),
 ("N37", "Run the orbital-comparison argument with q = 1, or without the common base value", "The contraction route fails; distinct fixed points are possible", "",
  dict(Schist="Probability uniqueness, Generic orbital comparison")),
 ("N38", "Infer independence from equal marginals", "Reject; a certified joint law is required", "",
  dict(Schist="Independence")),
 ("N39", "Present an upper Lipschitz bound as the least constant", "Leastness needs an attainment witness", "",
  dict(Trellis="Fabius upper bound")),
 ("N40", "Give a prime exponent oddness without excluding 2, or reflect divisibility through a zeroth power", "Reject; the premise p > 0 or p not 2 is required", "",
  dict(Trellis="Prime refinement, Behavioral reflection")),
 ("N41", "Treat a normalised tuple as equal to the original, or export exponent preservation that was never proved", "Require the construction relation; the indexed result stays unproved", "",
  dict(Obsidian="Normalised tuple, Exponent preservation")),
 ("N42", "Publish an unused false intermediate assertion", "Reject that node even though the final theorem has another proof", "M25",
  dict(Basalt="Publication", Fiber="T19", Gneiss="Unused false assertion", Karst="T17", Obsidian="Unused false assertion", Tephra="Publication")),
 ("N43", "Replay a stale result, or a displayed edit that differs from the probed one", "Exact-origin transactional replay; stale results cannot commit", "M21",
  dict(Basalt="Revision", Fiber="T18", Gneiss="Displayed edit differs", Karst="T18", Moraine="Candidate changes a fixed object", Obsidian="Candidate changed after analysis", Tephra="Origin")),
 ("N44", "Reuse a success badge across a toolchain or structure change", "Recheck meaning and destination policy; issue a new receipt", "M23",
  dict(Gneiss="Toolchain or structure changes", Obsidian="Execution assumptions changed")),
 ("N45", "Offer a different proof for a step that named a required method", "Report a method mismatch, not success", "",
  dict(Tephra="Method fidelity")),
 ("N46", "Return a correct fact that is not the sealed target", "Reject at the target check", "",
  dict(Gneiss="Wrong result target")),
 ("N47", "Differentiate a totalised derivative expression without existence evidence, or a quotient without its denominator guards", "Request HasDerivAt evidence; the numerator identity does not discharge the guards", "M45",
  dict(Trellis="Derivative law")),
 ("N48", "Use a nonnegative real where a nonzero one is required", "Request the missing strictness", "",
  dict(Tephra="Refinement implication")),
]

# ---------------------------------------------------------------- the twenty questions
# (id, question, consensus, variants, marks in report order: Y explicit answer, P implicit, N absent)
Q = [
 ("R1", "How is a reflective checker proved sound in practice?",
  "Executable coefficient data, a denotation into an arbitrary commutative ring, normalisation and operation lemmas, checker soundness, and a separate reification bridge",
  "Schist compiles an affine instance with its original-target bridge; Moraine compiles a length model; the sparse polynomial checker is proved on paper by five reports and formalised by none", "YYYYPYYYY"),
 ("R2", "Where does grobner sit?",
  "A bounded proof-producing provider and control; retain its proof term; assume no certificate export; failure is not negation",
  "Unanimous among the eight that answer", "YYYYNYYYY"),
 ("R3", "What is the accounting layer over Lean's own workspace?",
  "An index into Lean's context: role metadata, source-to-evidence links, observation origins, receipts; no competing logical store",
  "Unanimous", "YYYYYYYYY"),
 ("R4", "Partial or total by default?",
  "Total operations when importing Lean; an explicit partial-expression package whose domain is part of the type",
  "Unanimous", "YYYYYYYYY"),
 ("R5", "Which package first, measured?",
  "A small end-to-end slice with a proved checker and one property package; the inspected files are development material, not held out",
  "First package differs: exact Frey quotients (Fiber, Obsidian, Karst second), sparse polynomial checker (Basalt, Karst, Gneiss, Tephra), an affine checker (Schist, Trellis), a bundle adapter for coinduced invariants (Moraine), ideal-preserving maps (Basalt)", "YYYYYYYYY"),
 ("R6", "When does the accelerated profile earn its axiom?",
  "No threshold is claimed; measure on the actual checker after the strict route exists; policy is decided before speed",
  "Unanimous", "YYYYPYYYY"),
 ("R7", "How do accepted certificates survive a toolchain upgrade?",
  "Recheck in the destination environment, inspect the actual axiom inventory, issue a new receipt; a renamed axiom is not an allowlist edit",
  "Unanimous", "YYYYYYYYY"),
 ("R8", "What does Leant contribute to the examples specifically?",
  "Structural composition of generated obligations, measured separately from single-lemma lookup; behavioral results only through Lean-checked contracts",
  "Basalt, Karst, and Tephra add the realisability bridge; Moraine adds a complete affine length criterion; Fiber adds backward constraints on holes", "YYYYYYYYY"),
 ("R9", "Can the fifty-one mutations be executed?",
  "Finite Python subsets were executed; the paired Lean suite is an explicit backlog; every rejection needs a positive neighbour",
  "Unanimous", "YYYYPYYYY"),
 ("R10", "Is nine the right number?",
  "No; fewer reports, each implementing the same small interface, plus adversarial review",
  "Tephra: independent implementations of one interface; Gneiss: a few implementations with distinct goals; Karst and Basalt: the gate is a compiled end-to-end slice", "YYYYPYYYY"),
 ("Q1", "What is the first task?",
  "As R5: one compiled slice with a proved checker and one property package",
  "Same spread as R5", "YYYYPYYYY"),
 ("Q2", "What is the result vocabulary?",
  "Ordinary Lean predicates with typed indices (domain, filter, measure, precision, branch, completeness); extensible, not a fixed ladder",
  "Unanimous", "YYYYYYYYY"),
 ("Q3", "What is the trusted execution route?",
  "Kernel reduction or proof-producing reconstruction; native evaluation is an audited optional profile",
  "Unanimous", "YYYYYYYYY"),
 ("Q4", "What may an author delegate by specification?",
  "Any witness satisfying a frozen specification, without a notice per candidate; never a changed domain, branch, structure, or quantifier",
  "Unanimous", "YYYYYYYYY"),
 ("Q5", "How visible is a conditional result?",
  "Its condition is shown by default; a blind reading test decides whether the default suffices",
  "Unanimous", "YYYYYYYYY"),
 ("Q6", "May representations change automatically?",
  "Only through registered relation-specific theorems that retain the selected route; no global planning",
  "Obsidian allows silent substitution of one exact normaliser for another under the same guarantee and policy", "YYYYPYYYY"),
 ("Q7", "How does Leant report negative outcomes?",
  "A taxonomy: unsupported, exhausted, non-derivable in a calculus, model-relative counterexample, checked refutation at the original target",
  "Unanimous", "YYYYYYYYY"),
 ("Q8", "What is the first definition interface?",
  "One package with proved interface lemmas: exact quotients, CDF observations, characteristic profiles, representing families, or phase functions",
  "Spread as R5", "YYYYYYYYY"),
 ("Q9", "What evidence survives migration?",
  "Retained terms or certificates at a pin; a new receipt after rechecking the statement, dependencies, and policy",
  "Unanimous", "YYYYYYYYY"),
 ("Q10", "What result would keep only the library?",
  "If the shared-library arm explains the gains, ship the packages and stop the syntax",
  "Unanimous", "YYYYYYYYY"),
]

# ---------------------------------------------------------------- compiled Lean cores
# (report, file, lines, theorems, warnings, axiom summary, elapsed ms)
LEAN = [
 ("Basalt", "companions/ContractCore.lean", 74, 2, "3 (defProp linter)", "2 theorems axiom-free", 3805),
 ("Fiber", "CoreEncoding.lean", 67, 3, "0", "3 theorems axiom-free", 3731),
 ("Gneiss", "GneissCore.lean", 81, 2, "4 (defProp linter)", "2 theorems axiom-free", 5385),
 ("Karst", "examples/KarstCore.lean", 114, 11, "0", "11 theorems axiom-free", 3237),
 ("Moraine", "companion/Contracts.lean", 194, 16, "0", "14 axiom-free; model_sound and promote_model_spec use propext", 8815),
 ("Schist", "SchistCore.lean", 140, 8, "0", "5 axiom-free; eval_nf, check_sound, original_target use propext", 7465),
 ("Tephra", "TephraCore.lean", 119, 6, "0", "6 theorems axiom-free", 3566),
]


def write_csv(name, header, rows):
    path = os.path.join(OUT, name)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


def main():
    # matrix
    rows = []
    for rid, text, marks in M:
        assert len(marks) == 9, rid
        rows.append([rid, text] + list(marks) + ["yes" if rid in INHERITED else "no"])
    write_csv("feature_matrix.csv", ["id", "commitment"] + REPORTS + ["stated_in_round2_syntheses"], rows)
    unanimous = [rid for rid, _, mk in M if mk == "Y" * 9]
    fresh_unanimous = [r for r in unanimous if r not in INHERITED]
    inh_unanimous = [r for r in unanimous if r in INHERITED]
    print("matrix rows=%d unanimous=%d inherited_rows=%d fresh_rows=%d" % (
        len(M), len(unanimous), len(INHERITED), len(M) - len(INHERITED)))
    print("  unanimous inherited=%d unanimous fresh=%d" % (len(inh_unanimous), len(fresh_unanimous)))
    print("  fresh unanimous:", " ".join(fresh_unanimous))
    per = {r: [0, 0, 0] for r in REPORTS}
    for _, _, mk in M:
        for r, c in zip(REPORTS, mk):
            per[r]["YPN".index(c)] += 1
    for r in REPORTS:
        print("  %-9s Y=%2d P=%2d N=%2d" % (r, *per[r]))

    # suite
    rows = []
    inc = 0
    singles = 0
    core = []
    new_fam = 0
    for nid, mut, resp, inh, src in N:
        k = len(src)
        inc += k
        if k == 1:
            singles += 1
        if k >= 5:
            core.append(nid)
        if not inh:
            new_fam += 1
        rows.append([nid, mut, resp, inh, k] + [src.get(r, "") for r in REPORTS])
    write_csv("negative_suite.csv", ["id", "mutation", "required_response", "inherits_round2", "reports"] + REPORTS, rows)
    print("suite families=%d incidences=%d singletons=%d new_families=%d core(>=5)=%d: %s" % (
        len(N), inc, singles, new_fam, len(core), " ".join(core)))

    # questions
    rows = []
    for qid, q, cons, var, mk in Q:
        assert len(mk) == 9, qid
        rows.append([qid, q, cons, var, mk.count("Y"), mk.count("P")] + list(mk))
    write_csv("question_tally.csv", ["id", "question", "consensus", "variants", "explicit", "implicit"] + REPORTS, rows)
    print("questions=%d explicit-all=%d" % (len(Q), sum(1 for *_, mk in Q if mk == "Y" * 9)))

    # lean
    write_csv("lean_cores.csv", ["report", "file", "lines", "theorems", "warnings", "axioms", "elapsed_ms"], [list(x) for x in LEAN])
    print("lean files=%d lines=%d theorems=%d" % (len(LEAN), sum(x[2] for x in LEAN), sum(x[3] for x in LEAN)))


if __name__ == "__main__":
    main()
