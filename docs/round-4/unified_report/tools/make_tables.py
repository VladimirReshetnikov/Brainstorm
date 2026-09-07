"""Data behind the round-4 unified report.

Writes feature_matrix.csv, negative_suite.csv, question_tally.csv, lean_files.csv and
companion_runs.csv into the report directory and prints the counts quoted in the text.

Report order everywhere: Alder, Bryony, Clover, Fennel, Heather, Juniper, Laurel, Rowan, Sorrel.
Marks: Y = stated as a commitment, P = partial or implicit, N = absent.
"""
import csv
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
REPORTS = ["Alder", "Bryony", "Clover", "Fennel", "Heather", "Juniper", "Laurel", "Rowan", "Sorrel"]

# ---------------------------------------------------------------- commitment matrix
# (id, statement, marks in report order)
M = [
 # A. foundation
 ("A1", "Extend the elaborator's typing discipline first; the kernel is unchanged in the first implementation", "YYYYYYYYY"),
 ("A2", "Lean already expresses the properties; the extension is the checking discipline, not the logic", "YYYYYYYYY"),
 ("A3", "A primitive refinement former (pack, value, evidence, proof-directed weakening) is a later, measured experiment", "YYYYYYYYY"),
 ("A4", "No semantic subtyping or equality reflection in conversion; no CAS inside definitional equality", "YYYYYYYYY"),
 ("A5", "The objection to semantic conversion is predictability and trusted surface, not `a timeout means false'", "YYYYPYYYP"),
 ("A6", "Failure to infer a property is not evidence that it is false", "YYYYYYYYY"),
 ("A7", "Definitional functoriality of coercions is named as a separate metatheoretic experiment", "YYYNPNNPN"),
 # B. fixed object, evidence, sealing
 ("B1", "A proved property enriches the same term; the object is never rebound to a subtype locally", "YYYYYYYYY"),
 ("B2", "Weakening applies a proved implication; equality transports by elimination; other relations need a consumer theorem", "YYYYYYYYY"),
 ("B3", "An anchor is the elaborated term with its structures and context, never a printed name or a hash", "YYYYYYYYY"),
 ("B4", "Branch-local facts do not leak to siblings; leaving a branch exports an implication", "YYYYYYYYY"),
 ("B5", "A written preservation theorem: the core rules translate to ordinary Lean terms without new axioms", "YPYYYYPYY"),
 ("B6", "Three hole classes: meaning-bearing, proof, and authorized witness under a fixed specification", "YYYYYYYYY"),
 ("B7", "Hole classification is by dependency closure of the sealed target, not by the printed type of a metavariable", "YYYPPYPPY"),
 ("B8", "First implementation: the sealed target contains no metavariables at all (proof goals live in the term)", "NNNYNNNYN"),
 ("B9", "Providers run on a copy of the state; commit re-checks the returned term at the sealed target in the original context", "YYYYYPPYY"),
 # C. structures
 ("C1", "Selecting a structure (ring, topology, measure, action) is data, separate from inferring propositions", "YYYYYYYYY"),
 ("C2", "No global instance per derived fact; a local instance bridge only where an API demands one", "YYPYYYYYY"),
 ("C3", "A lexical structure context is proposed; its effect on generated preambles is explicitly unmeasured", "YYYYYYYYY"),
 ("C4", "Nonzero, regular, and unit are three predicates; a source denominator may vanish in positive characteristic", "YYYYYYYYY"),
 # D. behaviour
 ("D1", "A behavioural contract on a total function is: for all x, P x implies Q x (f x)", "YYYYYYYYY"),
 ("D2", "Contract variance: preconditions contravariant, postconditions covariant; no single strength rank", "YYYYYYYYY"),
 ("D3", "Composition retains the actual intermediate value and needs a bridge to the next precondition", "YYYYYYYYY"),
 ("D4", "Relational and whole-function laws (monotone, Lipschitz, naturality, inverse pair) are contracts on the function", "YYYYYYYYY"),
 ("D5", "A function on a refined domain and a total function with a contract are different interfaces", "YYYYYYYYY"),
 ("D6", "Sorting needs permutation and order; length preservation admits reversal and constant lists", "YYYYYYYYY"),
 ("D7", "Effects get a separate axis (Hoare logic, mvcgen); a timeout or cost is not a mathematical premise", "YYYYYYYYY"),
 ("D8", "A requirement transformer is a registered sufficient route, not a weakest precondition", "YPPPYNNYP"),
 ("D9", "A polymorphic Lean type yields no free theorem under classical choice", "NYYYYNNNY"),
 # E. relations and locality
 ("E1", "Equality on an open set at an interior point yields eventual equality; equality at the point does not", "YYYYYYYYY"),
 ("E2", "Almost-everywhere equality is indexed by its measure; its consumer is integral congruence, never point evaluation", "YYYYYYYYY"),
 ("E3", "Countably many a.e. statements combine; an uncountable family does not (the singleton-indicator trap)", "NYYYNYYYY"),
 ("E4", "A derivative jet loses one order: input N+1 for output N", "YYPYYYYYY"),
 ("E5", "A residual certificate identifies a jet of the selected root only with the branch condition and a unit derivative", "YNYPNNYYY"),
 ("E6", "Preservation is not reflection: X lies in (2X) over Q[X] but not over Z[X]; X^2-X vanishes on F_2", "NYYNYYNYN"),
 ("E7", "Complete solving needs soundness and coverage of the same predicate; a result kind is not a confidence ladder", "YYYYYYYYY"),
 ("E8", "An enclosure with equal endpoints may prove equality; a generic enclosure may not", "YNNYNNNYN"),
 # F. the residual telescope
 ("F1", "An unfinished step denotes a conditional term over its residual telescope; it is never indexed as a proof of its unconditional target", "YYYYYYYYY"),
 ("F2", "The residual is an ordered dependent telescope; sequential composition is substitution, not set union", "YYYYYYYYY"),
 ("F3", "Result states are distinct: proved, conditional, no route in the fragment, exhausted, unsupported, refuted", "YYYYYYYYY"),
 ("F4", "Exporting a conditional theorem is an explicit statement change; no hypothesis is added silently", "YYYYYYYYY"),
 ("F5", "A residual is an elaboration effect, not a runtime effect; a timeout never appears in the telescope", "YPYYYPYYY"),
 ("F6", "A term may itself be pending (needs proof arguments to be well typed), not merely a term with a pending property", "YPYPPPYPY"),
 # G. the antichain frontier
 ("G1", "Alternative sufficient supports are retained as an inclusion-minimal antichain, each with its own derivation", "YYNYNYYNY"),
 ("G2", "Termination is proved by the upward-closure measure, at most |Q| 2^|H| successful insertions", "YYNYNYYNY"),
 ("G3", "Relative completeness and schedule independence are proved for the fixed finite rule set", "YYYYYYYYY"),
 ("G4", "Derivation nodes are immutable and refer only to older nodes; a cyclic rule graph never yields a cyclic proof", "YYYYYYYYY"),
 ("G5", "Minimal supports are not weakest preconditions; diagnostics say `required by this route', not `necessary'", "YYYYYYYYY"),
 ("G6", "The exponential worst case (2^k incomparable routes) is stated; a truncated run is labelled incomplete", "YYNYNYYNY"),
 ("G7", "Offering the goal as its own repair is a tautological route, excluded from the default vocabulary", "YYNNNYYNN"),
 ("G8", "Method or support policy is applied before minimization, or labels are indexed by policy", "YYPYNYYPY"),
 ("G9", "Two completeness flags: grounding coverage of the profile, and frontier closure of the emitted manifest", "YYYYYYYYY"),
 ("G10", "An unseeded cycle proves nothing; an offered seed yields a conditional route and a known seed a closed one", "YYYYYYYYY"),
 ("G11", "A finite certificate characterises frontier completeness and is checked independently of the solver", "NNNNNYNNN"),
 ("G12", "Reopening a removed premise abstracts only the leaves that used it; unused premises add nothing", "NPNPNNYNP"),
 # H. grounding
 ("H1", "A finite typed term pool (target subterms, locals, named intermediates) bounds rule instantiation", "YYYYYYYYY"),
 ("H2", "An explicit combinatorial bound on candidate instantiations is stated", "YPYPYYYYY"),
 ("H3", "No fresh term generation inside closure; constructors only to an explicit depth or in a new epoch", "YYYYYYYYY"),
 ("H4", "Demand-driven backward slice from the goal, then forward closure on the slice", "YYYYYYYYY"),
 ("H5", "A registered rule is an ordinary theorem plus role metadata validated against its actual type", "YYYYYYYYY"),
 ("H6", "Existing automation (fun_prop, grind, arithmetic tactics, exact?) is a provider and a control, not reinvented", "YYYYYYYYY"),
 ("H7", "A provider's proof becomes a leaf in a new epoch; its failure creates no negative fact", "YYYYYYYYY"),
 # I. realizable observations
 ("I1", "Positive soundness, decision completeness, negative realization, and coverage are four separate contracts", "YYYYYYYYY"),
 ("I2", "A theorem: a finite realizable frame (basis, span, or generator set) decides affine equalities on the admissible image", "YNYPYPYYN"),
 ("I3", "On List Empty the models 0 and n agree; a positive length is not a witness", "YYYYYYYYY"),
 ("I4", "Correlated observations (a list and its reverse) need joint realization; (1,0) refutes nothing", "YYYYYPYYY"),
 ("I5", "An empty admissible domain is vacuous and distinct from an empty element type", "YNYNYNYYN"),
 ("I6", "A failing frame point is itself a concrete admissible counterexample", "YPYPYPYYP"),
 ("I7", "The model law is not the source law: a denotation theorem for the exact candidate is required; provider text is not a theorem", "YYYYYYYYY"),
 ("I8", "Refuting one completion does not refute the sketch", "YYYYYYYYY"),
 ("I9", "Affine determination decides equalities only; inequalities need cone or sign certificates", "YNNNYNYYN"),
 # J. evidence lifetime, rewriting, publication
 ("J1", "After simp: definitional reuse, or equality transport, or a consumer theorem or iff; never string matching", "YYYYYYYYY"),
 ("J2", "Rebuild the index per declaration first; typed context embeddings later; a hash or identifier is routing only", "YYYYYYYYY"),
 ("J3", "Dependent indices transport with their index equality (Fin n is not Fin m because a printer hides the index)", "YYYYYYYYY"),
 ("J4", "Every displayed assertion is checked; an unused false one blocks publication", "YYYYYYYYY"),
 ("J5", "Method fidelity is not token occurrence: a recipe tree or a support-restricted helper", "YYYYYYYYY"),
 ("J6", "Three acceptances: theorem validity, statement fidelity, method fidelity", "PYPYPYYYY"),
 ("J7", "A receipt is not a proof; replay the exact edit; a migration issues a new receipt", "YYYYYYYYY"),
 # K. computation
 ("K1", "Three lanes: verified algorithm, certificate with verified checker, proof-producing tactic; the target is fixed", "YYYYYYYYY"),
 ("K2", "The execution gap: a checker theorem is not evidence about native bytes; no native threshold is claimed", "YYYYYYYYY"),
 ("K3", "One typed reification interface (syntax, environment, bridge proof) shared by checkers; no untyped universal reifier", "YYYYYYYYY"),
 ("K4", "Arity is checked before pairing certificate components; a truncating zip changes the theorem", "YYYYNNYYN"),
 # L. worked examples and sources
 ("L1", "Frey helper: the second numerator needs only 2 | b and 4 <= p; interfaces are per coefficient", "YYYYYYYYY"),
 ("L2", "The satisfiable fixture (3,2,5) gives -53 and -486; no Fermat equation, primality, or coprimality", "YYYYYYYYY"),
 ("L3", "The four single-premise neighbours (3,2,4), (3,3,5), (3,2,3), (1,2,5) are exhibited", "NYYYYYYYY"),
 ("L4", "The first numerator needs only p >= 2", "NNYPNYPYN"),
 ("L5", "Autonomous derivative: hypotheses only on W(U); induction keeps the point quantified", "YNYYYYPYN"),
 ("L6", "Tensor family: finite free factors are the theorem's hypotheses; naturality is a law of the family; Q[X] shows finite indexing alone fails", "YYYYYPNYY"),
 ("L7", "Leant 3a40904b is the inspected revision; 823259f7 is attributed to the syntheses and was not retrievable", "YYYYYYYYY"),
 ("L8", "Verified is a callback receipt; epochs seal association; the Length adapter refuses source refutation", "YYYYYYYYY"),
 ("L9", "Whole-file line counts are a misleading baseline; the final wrapper is already short", "YYYYYYYYY"),
 ("L10", "A new nonalgebraic worked example beyond the round-3 set", "YYPYNYYNY"),
 # M. evaluation and evidence
 ("M1", "Arms L0..L4 plus a renderer control; L3 versus L2 is the decisive comparison", "YYYYYYYYY"),
 ("M2", "All inspected examples are development material; held-out tasks are chosen after the interface is frozen", "YYYYYYYYY"),
 ("M3", "A blind reading test is proposed and not run; no productivity number is claimed", "YYYYYYYYY"),
 ("M4", "Stopping rule: keep the library, services, or renderer if they explain the gains", "YYYYYYYYY"),
 ("M5", "No Lean toolchain was available to the author; shipped Lean is labelled uncompiled", "YYYYYYYYY"),
 ("M6", "The companion has an independently written oracle or replay checker", "YYPYPYYYY"),
 ("M7", "Executed counts are reported with their units and are not summed", "YYYYYYYYY"),
 ("M8", "The first Lean slice is the exact-quotient use site", "YYPYNPYYY"),
 ("M9", "Mechanizing the frontier checker itself in Lean is a named next deliverable", "NNPNNYNNP"),
]

# Rows that were already consensus in the round-3 syntheses (its matrix, corrections, or suite).
INHERITED = {"A1", "A2", "A3", "A4", "A6", "B1", "B2", "B3", "B4", "B5", "B6",
             "C1", "C2", "C3", "C4", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D9",
             "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "G5", "H5", "H6",
             "I1", "I3", "I7", "I8", "J3", "J4", "J5", "J7", "K1", "K2", "K4",
             "L1", "L2", "L5", "L6", "L8", "M1", "M2", "M3", "M4"}

# ---------------------------------------------------------------- negative suite
# (id, mutation, required response, inherits round-3 id or "", per-report source tokens)
# Tokens: E = executed by the shipped companion; T = listed in the report's own mutation table;
#         P = argued in prose or by a worked counterexample.
N = [
 ("S1", "Differentiate from equality at one point instead of on a neighbourhood", "Locality obligation stays open; f(t)=t, g(t)=0 at 0", "N1",
  dict(Alder="T", Bryony="P", Clover="T", Fennel="T", Heather="T", Juniper="T", Laurel="T", Rowan="T", Sorrel="T")),
 ("S2", "Specialise the induction hypothesis to one point before the successor step", "Request the set-wide or neighbourhood assertion", "N2",
  dict(Alder="T", Clover="T", Fennel="T", Heather="P", Juniper="T", Laurel="P", Rowan="T")),
 ("S3", "Invert a nonzero or regular element as if it were a unit; cast a source-nonzero denominator into positive characteristic", "Request the destination unit; no ring change", "N3",
  dict(Alder="P", Bryony="P", Clover="T", Fennel="P", Heather="T", Juniper="T", Laurel="T", Rowan="P", Sorrel="P")),
 ("S4", "Cast an inexact integer quotient, or drop one Frey divisibility premise", "Exactness obligation stays open; the four neighbours fail the corresponding divisibility", "N25",
  dict(Alder="T", Bryony="E", Clover="E", Fennel="E", Heather="T", Juniper="E", Laurel="E", Rowan="E", Sorrel="E")),
 ("S5", "Test an arithmetic contract only inside a contradictory Frey package", "Use the satisfiable helper context with fixture (3,2,5)", "N26",
  dict(Alder="P", Bryony="T", Clover="P", Fennel="T", Heather="P", Juniper="P", Laurel="T", Rowan="P", Sorrel="T")),
 ("S6", "Infer a finite free representing algebra from finite indexing alone", "Construction contract not established; Q[X] obstruction", "N49",
  dict(Alder="P", Bryony="P", Clover="T", Fennel="T", Heather="T", Juniper="P", Rowan="T", Sorrel="T")),
 ("S7", "Evaluate at a point from an a.e. fact, or change the measure beneath it", "Require a new relation or checked transport", "N34",
  dict(Alder="P", Bryony="E", Clover="T", Fennel="T", Heather="T", Juniper="P", Laurel="T", Rowan="P", Sorrel="T")),
 ("S8", "Merge an uncountable family of a.e. statements", "Uniform-null-set obligation remains", "N35",
  dict(Bryony="P", Clover="T", Fennel="T", Juniper="P", Laurel="T", Rowan="P", Sorrel="P")),
 ("S9", "Refute a List Empty length law with an unrealisable positive length", "No source refutation; admit the one-point frame", "N22",
  dict(Alder="E", Bryony="P", Clover="E", Fennel="T", Heather="E", Juniper="T", Laurel="E", Rowan="E", Sorrel="E")),
 ("S10", "Offer (1,0) as a witness against a law on a list and its reverse", "Not realizable on the diagonal; require joint realization", "N52",
  dict(Alder="E", Bryony="P", Clover="E", Fennel="T", Heather="E", Laurel="E", Rowan="E", Sorrel="P")),
 ("S11", "Reuse the unrestricted frame under a guard (even lengths, length exactly 100, nonempty lists)", "Recompute the frame for the guarded image: dimension may drop or not; old sound covers survive, old negative witnesses may not", "",
  dict(Clover="P", Heather="E", Laurel="P", Rowan="E", Synthesis="P")),
 ("S12", "Treat an empty admissible domain as an empty element type, or fabricate a base point", "Vacuous case handled by an emptiness proof; no base point", "",
  dict(Alder="P", Clover="P", Heather="P", Laurel="P", Rowan="E")),
 ("S13", "Refute one completion, then reject every completion of the sketch", "Only the completion is refuted", "N24",
  dict(Alder="P", Bryony="P", Clover="P", Fennel="P", Heather="P", Juniper="P", Laurel="P", Rowan="P", Sorrel="P")),
 ("S14", "Use a passive provider law (Length contract text) as a theorem", "Heuristic only, or a visibly conditional result", "N21",
  dict(Alder="P", Bryony="P", Clover="T", Fennel="P", Heather="T", Juniper="P", Laurel="T", Rowan="P", Sorrel="P")),
 ("S15", "Grant a polymorphic function a free theorem", "Require a uniformity theorem or a restricted grammar", "N23",
  dict(Bryony="P", Clover="P", Fennel="P", Heather="P", Sorrel="P")),
 ("S16", "An unseeded cycle P -> Q -> P", "Proves nothing; no closed derivation (a diagnostic engine may still list leaves)", "",
  dict(Alder="E", Bryony="E", Clover="E", Fennel="E", Heather="P", Juniper="E", Laurel="E", Rowan="E", Sorrel="E")),
 ("S17", "A seeded cycle, then deletion of its seed", "Known seed: closed; offered seed: conditional; deleted seed: nothing, unless reopened as an offer", "",
  dict(Alder="P", Bryony="E", Clover="P", Fennel="E", Juniper="E", Laurel="E", Rowan="E", Sorrel="E", Synthesis="P")),
 ("S18", "Use a result to justify the guard that authorises it", "Reject the cyclic derivation without a separate well-founded proof", "N10",
  dict(Alder="P", Bryony="P", Clover="P", Fennel="T", Heather="P", Juniper="T", Laurel="P", Rowan="P", Sorrel="P")),
 ("S19", "Offer the goal itself as a repair", "A tautological route, labelled as such, never progress", "",
  dict(Alder="P", Bryony="P", Juniper="E", Laurel="E")),
 ("S20", "Forge a support, alter the target, reorder premises, or corrupt a certificate node", "Independent checker rejects", "N14",
  dict(Alder="E", Bryony="E", Clover="E", Fennel="E", Heather="E", Juniper="E", Laurel="E", Rowan="E", Sorrel="E")),
 ("S21", "Omit one alternative route but mark the frontier complete", "Closure certificate fails", "",
  dict(Fennel="P", Juniper="E", Synthesis="E")),
 ("S22", "Stop enumeration at a budget limit", "Retained routes stay valid; coverage is marked incomplete; never a negation", "",
  dict(Alder="E", Bryony="P", Clover="E", Fennel="E", Heather="P", Juniper="E", Laurel="E", Rowan="E", Sorrel="E")),
 ("S23", "Reverse or shuffle the rule schedule", "Same support antichains or closure set", "",
  dict(Bryony="P", Clover="E", Fennel="P", Juniper="E", Laurel="P", Rowan="E", Sorrel="E")),
 ("S24", "Reuse a branch-local fact in a sibling branch", "Reject context reuse or export a scoped implication", "N9",
  dict(Alder="E", Bryony="P", Clover="E", Fennel="P", Heather="P", Juniper="T", Laurel="E", Rowan="E", Sorrel="E")),
 ("S25", "Replay after a rebuilt context, changed snapshot, or changed rule profile", "Refuse the stale epoch; recheck in the new context", "N51",
  dict(Alder="E", Bryony="E", Clover="E", Fennel="E", Heather="E", Juniper="E", Laurel="E", Rowan="E", Sorrel="E")),
 ("S26", "Remove a used versus an unused premise from a closed derivation", "Only the used premise reopens as a residual", "",
  dict(Bryony="P", Fennel="P", Laurel="E", Sorrel="P")),
 ("S27", "Filter a method policy after minimization", "A permitted route may have been discarded; filter before, or index labels by policy", "",
  dict(Alder="P", Clover="E", Fennel="E", Juniper="P", Laurel="P", Rowan="P", Sorrel="E")),
 ("S28", "Satisfy a required arithmetic method by a global contradiction", "Truth may hold; the method contract is unmet", "N45",
  dict(Alder="P", Bryony="T", Clover="T", Fennel="T", Heather="T", Juniper="T", Laurel="T", Rowan="T", Sorrel="T")),
 ("S29", "Publish an unused false intermediate assertion", "Document is not fully checked", "N42",
  dict(Alder="E", Bryony="P", Clover="T", Fennel="P", Heather="P", Juniper="T", Laurel="T", Rowan="P", Sorrel="T")),
 ("S30", "Reuse a fact after simp rewrote its anchor by matching a normalised string", "Require conversion, equality transport, or a consumer theorem", "N50",
  dict(Alder="P", Bryony="P", Clover="P", Fennel="P", Heather="P", Juniper="P", Laurel="P", Rowan="P", Sorrel="P")),
 ("S31", "Let proof search fill a meaning-bearing hole to ease the goal", "Reject the assignment; report ambiguity", "N12",
  dict(Alder="P", Bryony="P", Clover="T", Fennel="P", Heather="P", Juniper="P", Laurel="P", Rowan="P", Sorrel="P")),
 ("S32", "Change the measure, topology, structure, or index under unchanged notation", "Report a statement change; recheck affected evidence", "N11",
  dict(Alder="T", Bryony="T", Clover="T", Fennel="T", Heather="T", Juniper="T", Laurel="T", Rowan="T", Sorrel="T")),
 ("S33", "Differentiate a jet and keep the input precision", "Require the N+1 to N transformation", "N4",
  dict(Alder="P", Bryony="P", Fennel="P", Heather="P", Juniper="T", Laurel="T", Rowan="P", Sorrel="P")),
 ("S34", "Return the other exact root branch with a correct residual", "Residual passes; the constant-term condition fails", "N5",
  dict(Alder="E", Clover="P", Laurel="P", Rowan="P", Sorrel="P")),
 ("S35", "Substitute a formal coefficient theorem for an analytic identity", "Require the semantic analytic bridge", "",
  dict(Alder="P", Fennel="P", Juniper="T")),
 ("S36", "Run the inverse-derivative recipe with f'(0)=0, or with a discontinuous branch", "Nonvanishing and branch continuity are premises", "",
  dict(Juniper="P")),
 ("S37", "Descend along a non-surjective quotient map, or change the topology on the target", "Uniqueness or continuity conclusion reopens", "",
  dict(Juniper="P")),
 ("S38", "Request the logarithmic-derivative form at a zero factor", "Keep the exact target; expose the nonzero guards", "",
  dict(Fennel="T")),
 ("S39", "Replace the strict subgraph by the non-strict one in weighted Fubini", "Statement change; a point mass on the graph detects it", "",
  dict(Bryony="T")),
 ("S40", "Normalise a finite measure to mass one without a probability hypothesis", "Dirac mass two detects the change", "",
  dict(Sorrel="P")),
 ("S41", "Demand atomlessness for the Cauchy formula", "A point mass is a positive fixture; the demand weakens the theorem", "",
  dict(Sorrel="P")),
 ("S42", "Present an upper Lipschitz bound as the least constant", "Leastness stays open without the lower-bound argument", "N39",
  dict(Laurel="T", Sorrel="T")),
 ("S43", "Pair certificate components with a truncating zip", "Arity is checked first; use indexed vectors", "N14",
  dict(Bryony="P", Clover="P", Fennel="P", Laurel="P", Rowan="P")),
 ("S44", "Replay a rational ideal certificate for an integer ideal, or read coefficient inequality as functional inequality", "Preservation is not reflection", "N15",
  dict(Bryony="P", Clover="P", Heather="P", Juniper="P", Rowan="P")),
 ("S45", "Accept native bytes without execution evidence", "Kernel reduction or reconstruction; native needs its own policy", "N17",
  dict(Alder="P", Bryony="P", Clover="P", Fennel="P", Heather="P", Juniper="P", Laurel="P", Rowan="P", Sorrel="P")),
 ("S46", "Reuse a receipt or hash across an edit, a candidate change, or a toolchain migration", "New check, new receipt", "N43",
  dict(Alder="P", Bryony="P", Clover="T", Fennel="T", Heather="T", Juniper="T", Laurel="T", Rowan="T", Sorrel="T")),
 ("S47", "Accept a length-preserving candidate as a sorter", "Permutation and order are the specification", "N19",
  dict(Alder="P", Bryony="P", Clover="P", Fennel="P", Heather="P", Juniper="P", Laurel="P", Rowan="P", Sorrel="P")),
 ("S48", "Return a correct proof of a nearby weaker proposition", "Target mismatch; offer an explicit statement edit", "N46",
  dict(Alder="E", Bryony="E", Clover="E", Fennel="E", Heather="E", Juniper="E", Laurel="T", Rowan="E", Sorrel="E")),
 ("S49", "Write a cons literal over an empty element type", "Refused as a typing error, not a counterexample", "",
  dict(Alder="P", Heather="E", Rowan="P")),
 ("S50", "Borrow the affine theorem for a branching, filtering, or nonlinear candidate", "Outside the grammar; piecewise models need case coverage", "",
  dict(Clover="P", Heather="P", Laurel="P", Rowan="P")),
 ("S51", "Stop sampling when the observed rank stabilises and call it coverage", "Coverage is a theorem, not a stopping criterion", "",
  dict(Laurel="P")),
 ("S52", "Use affine equality at frame points to prove an inequality", "1-n is nonnegative at 0 and 1 only; use a cone certificate", "",
  dict(Alder="P", Heather="P", Laurel="P", Synthesis="P")),
 # families contributed by the parallel synthesis's adversarial probes
 ("S53", "Name a claim with a Lean keyword, or shadow an opened core name (compose, inj_comp), in an exported proof", "The plan checker passes and Lean rejects the export; emit hygienic, qualified identifiers and compile the exact output", "",
  dict(Synthesis="E")),
 ("S54", "Two routes, one already closed by available facts and one needing a new premise; export the smaller total support", "Rank residual work, not total support; never emit a conditional theorem where a closed proof exists", "",
  dict(Synthesis="E")),
 ("S55", "A diagnostic leaf frontier under an unseeded cycle (A -> A, A and B -> G) reports B", "Supplying B leaves G open; an explanation is not a sufficient contract", "",
  dict(Rowan="P", Synthesis="E")),
 ("S56", "Reuse an output directory after a later request fails or finds no route", "Old positive .lean files survive beside accurate negative metadata; a manifest must bind file, request, status and hash", "",
  dict(Synthesis="E")),
 ("S57", "Read a budgeted antichain as a subset of the final one", "A displayed support may later be dominated by the empty support; only the upward closure grows", "",
  dict(Laurel="P", Sorrel="P", Synthesis="E")),
]

# ---------------------------------------------------------------- the twenty questions
# (id, question, consensus answer, variants, marks in report order: Y explicit, P implicit, N absent)
Q = [
 ("T1", "What does the evidence index cost on a real file?",
  "Unmeasured by all nine; every companion reports finite-model counts only",
  "Clover measures 211 versus 16 ground instances in its model; Fennel, Juniper, Laurel measure the exponential family",
  "YYYPYPYYY"),
 ("T2", "Which registry rules fire?",
  "Only model traces: two rules for the fourth coefficient, one more for the second; no Mathlib histogram",
  "Clover: seven-rule registry fires two; Heather: one implication in the toy resolver",
  "YYYPYPYYY"),
 ("T3", "Does simp break the anchor?",
  "Three cases: definitional reuse, checked equality transport, consumer theorem or iff; keep the old anchor; never rekey by string",
  "Companions refuse all transport (Heather) or key on lexical context (Sorrel)",
  "YYYYYYYYY"),
 ("T4", "How is reification proved once for many checkers?",
  "Share a typed syntax, environment, and bridge proof interface; each checker keeps its own denotation theorem",
  "Bryony factors a semiring core with typed extensions; Rowan uses dependent vectors for arity",
  "YYYYYYYYY"),
 ("T5", "What is the completeness theorem for each Leant abstraction?",
  "Affine equality is complete relative to the admissible observation image, proved by a realizable frame; nothing is claimed for other contracts",
  "Rowan: finite unions of linear sets with constructed witnesses; Heather: rank lower bound; Alder: integer combinations into an abelian group",
  "YYYYYPYYY"),
 ("T6", "Where does almost-everywhere reasoning enter the row?",
  "As a relation indexed by its measure, consumed by the integral-congruence theorem at that measure; no point evaluation; countable versus uncountable families",
  "Alder: a pointwise upgrade under continuity and full support; Sorrel: the Cauchy formula's a.e. replacement",
  "YYYYYYYYY"),
 ("T7", "Does a lexical structure context shorten the FLT preambles?",
  "Proposed by all nine for meaning stability; measured by none",
  "",
  "YYYYYYYYY"),
 ("T8", "Can the closure theorem's rule generation be bounded?",
  "Yes: a finite typed term pool, first-order templates, and an explicit bound; completeness is relative to the materialised rules",
  "Sorrel adds constructor depth; Bryony adds epochs; Juniper adds two completeness flags",
  "YYYYYYYYY"),
 ("T9", "What does a reader recover from the compact view?",
  "A blind recovery test of domain, quantifiers, measure, branch, precision, and strength; not run",
  "",
  "YYYYYPYYY"),
 ("T10", "Is one implementation enough?",
  "No; every companion has a separately written oracle, and none is an independent team or a Lean implementation",
  "",
  "YYYPYPYYY"),
 ("Q1", "Which first use-site interface will we ship?",
  "One property-implicit exact-quotient binder and method application, compared with an ordinary Lean helper",
  "Heather ships the behavioural slice first; Clover and Juniper first port their finite engines",
  "YYYYYYYYY"),
 ("Q2", "What is the finite automatic fragment?",
  "Ground Horn rules over a finite term pool; the frontier antichain (or closure) is complete only for the materialised rules",
  "Six antichain engines; three closure-only engines",
  "YYYYYYYYY"),
 ("Q3", "What may inference decide about data?",
  "Only authorized witness holes under a fixed specification; meaning-bearing holes are sealed",
  "Fennel and Rowan seal a metavariable-free target; the rest classify by dependency closure",
  "YYYYYYYYY"),
 ("Q4", "How will required proof methods be checked?",
  "A recipe tree or support-restricted helper; policy filtered before minimization; token occurrence is insufficient",
  "Alder proposes a derivation automaton; Sorrel an intensional plan certificate",
  "YYYYYYYYY"),
 ("Q5", "Which behavioural bridge and completeness claim come first?",
  "The list grammar with a proved affine length model and a realizable frame for the actual input type",
  "Heather ships four frames; Rowan semilinear unions; Alder integer frames",
  "YYYYYYYYY"),
 ("Q6", "What authorizes negative Leant selection?",
  "A realized admissible witness with the negative transfer direction, or a proof of the negation; model witnesses stay model-relative",
  "",
  "YYYYYYYYY"),
 ("Q7", "Which nonalgebraic task is the first transfer test?",
  "Local differentiation as the development case; a held-out task chosen after the freeze",
  "Bryony: weighted Fubini; Sorrel: the Cauchy formula; Juniper: inverse derivatives and quotient descent; Laurel: sharp Lipschitz; Fennel: q-Pochhammer",
  "YYYYYYYYY"),
 ("Q8", "What evidence is retained and rechecked?",
  "Target, context, structures, candidate, proof or certificate, dependencies, policy; rebuild per declaration first",
  "Laurel reopens used premises; Clover keys on the whole source text",
  "YYYYYYYYY"),
 ("Q9", "What performance result would justify a larger checker or native execution?",
  "None claimed; measure index, firing, growth, and rebuild against existing tactics under a chosen policy first",
  "",
  "YYYYYPYYY"),
 ("Q10", "What outcome would end the separate-language experiment?",
  "If L1, L2, or the renderer explains the gains, ship those; L3 is the type-layer test; L4 is the syntax test",
  "",
  "YYYYYYYYY"),
]

# ---------------------------------------------------------------- Lean files compiled by this review
# (report, file, imports, lines, named theorems, result, warnings, elapsed ms)
LEAN = [
 ("Alder", "companion/generated/Locality.lean", "none", 18, 1, "compiles", 0, 77160),
 ("Alder", "companion/generated/Quotient.lean", "none", 81, 5, "compiles", 10, 6607),
 ("Bryony", "evidence/frey4/Requirements.lean", "none", 37, 2, "compiles", 2, 5193),
 ("Clover", "companion/CloverCore.lean", "none", 52, 7, "compiles; 7 theorems axiom-free", 0, 4226),
 ("Clover", "companion/GeneratedExamples.lean", "CloverCore", 43, 3, "compiles against the olean built here", 3, 21497),
 ("Fennel", "prototype/generated/query_0_route_0.lean", "none", 13, 1, "compiles", 7, 3127),
 ("Fennel", "prototype/generated/query_1_route_0.lean", "none", 11, 1, "compiles", 8, 4095),
 ("Fennel", "prototype/generated/query_1_route_1.lean", "none", 21, 1, "compiles", 3, 2826),
 ("Fennel", "prototype/generated/query_2_route_0.lean", "none", 21, 1, "compiles", 3, 2964),
 ("Heather", "companion/generated/UseSite.lean", "Mathlib", 8, 1, "compiles (cold Mathlib import)", 0, 689405),
 ("Heather", "companion/generated/diagonal_balance.lean", "Mathlib", 10, 1, "compiles; 3 unused simp arguments", 3, 91968),
 ("Heather", "companion/generated/empty_preserves.lean", "Mathlib", 14, 1, "compiles", 0, 84914),
 ("Heather", "companion/generated/even_reverse_length.lean", "Mathlib", 10, 1, "FAILS: simp closes the goal, the template's trailing omega has no goal; compiles once that line is removed", 3, 203293),
 ("Heather", "companion/generated/reverse_append_length.lean", "Mathlib", 10, 1, "compiles; 2 unused simp arguments", 2, 434349),
 ("Juniper", "companion/Generated.lean", "none", 53, 2, "compiles", 6, 16696),
 ("Laurel", "prototype/generated/alternatives.lean", "none", 29, 2, "compiles", 3, 8891),
 ("Laurel", "prototype/generated/cycle.lean", "none", 10, 0, "compiles (no theorem: unseeded cycle)", 0, 11897),
 ("Laurel", "prototype/generated/frey_a4.lean", "none", 34, 2, "compiles", 2, 67257),
 ("Laurel", "prototype/generated/quotient.lean", "none", 48, 3, "compiles", 4, 11098),
 ("Sorrel", "SelectedPlan.lean", "Init", 23, 1, "compiles", 2, 7875),
]

# New experiments run by this review: (file, imports, lines, theorems, examples, result, elapsed ms)
NEW = [
 ("ListImage.lean", "none", 62, 4, 3, "compiles, no warnings; axiom audit below", 10522),
 ("FreyRoutes.lean", "Mathlib", 133, 13, 7, "compiles; 4 unused-variable lints; the five queried theorems depend on propext, Classical.choice, Quot.sound", 220514),
]

# The parallel synthesis's follow-up files, recompiled here: (file, imports, expected, result, elapsed ms)
CODEX = [
 ("ListImageAxioms.lean", "none", "accept; four axiom queries", "accepted; length_image and empty_one_point_frame use propext, inhabited_two_point_frame adds Quot.sound, diagonal_frame adds Classical.choice", 8075),
 ("FreySharper.lean", "Mathlib", "accept; cast_a2_sharper under p >= 2", "accepted; four theorems and two examples; four axiom queries report propext and Quot.sound, three of them also Classical.choice", 517101),
 ("HeatherEvenRepaired.lean", "Mathlib", "accept (all_goals omega)", "accepted; six lints (unused simp arguments, unused tactic)", 36799),
 ("SorrelSelectionProbe.lean", "Init", "accept (valid conditional theorem)", "accepted", 7001),
 ("KeywordClaim.lean", "CloverCore", "reject (claim named theorem)", "rejected as expected (1 error)", 10404),
 ("ShadowCompose.lean", "CloverCore", "reject (claim shadows compose)", "rejected as expected (6 errors)", 30201),
 ("ShadowRule.lean", "CloverCore", "reject (claim shadows inj_comp)", "rejected as expected (1 error)", 19054),
]

# ---------------------------------------------------------------- companion reruns (this review, Python 3.14.4)
# (report, command, reported by the author, reproduced here, elapsed ms)
RUNS = [
 ("Alder", "test_alder.py", "all families pass; 64 unary graphs, 4,096 configurations, 13,824 probes, 46,875 frame comparisons, 33 coefficients", "identical counts", 3541),
 ("Bryony", "test_bryony.py", "23 methods; 400 systems; 3,873 subsets; 2,800 comparisons; 1,835 certificates; 288 triples", "identical counts", 1419),
 ("Clover", "unittest test_clover_slice; affine_basis.py; compare_profiles.py", "35 methods; 1,576 assertion checks; 211 versus 16 instances", "identical counts", 2313),
 ("Fennel", "test_fennel.py; stress_frontiers.py", "27 tests; 2,000 graphs; 12,872 comparisons; 1,820 certificates; routes 4, 16, 64, 256, 1,024", "identical counts", 2885),
 ("Heather", "test_heather.py; use_site_demo.py", "18 methods; 7,500 comparisons; 466 witnesses; 14 refusals", "18 pass; the demo fails under a cp1252 default locale and passes with PYTHONUTF8=1", 1659),
 ("Juniper", "test_frontier.py; inverse_polynomials.py", "32 tests; 400 profiles; 6,400 assignments; 2,800 frontiers; polynomials through order six", "identical counts", 3278),
 ("Laurel", "test_core.py; bench_frontier.py", "19 methods; 32,768 profiles; 98,304 frontiers; 98,400 derivations; 308 triples; about 2.4 s", "identical counts in 20.3 s", 20336),
 ("Rowan", "test_rowan.py; rowan_model.py", "32 tests; 12,675 comparisons; 4,374 decisions; 139 fixtures", "identical counts; demo gives -53 and -486", 1379),
 ("Sorrel", "sorrel_model.py --test", "31 tests; 80 systems; 1,280 subsets; 7,680 comparisons; 517 certificates", "identical counts", 638),
]


def tex(s):
    s = str(s)
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}"),
                 ("|", r"$\mid$"), ("<=", r"$\le$"), (">=", r"$\ge$"), ("->", r"$\to$")]:
        s = s.replace(a, b)
    return s


MARK = {"Y": r"\Yy", "P": r"\Pp", "N": r"\Nn"}


def write_tex(name, lines):
    path = os.path.join(OUT, name)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("% generated by tools/make_tables.py; do not edit\n")
        f.write("\n".join(lines) + "\n")
    return path



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
    write_csv("feature_matrix.csv", ["id", "commitment"] + REPORTS + ["stated_in_round3_syntheses"], rows)
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
        print("  %-8s Y=%2d P=%2d N=%2d" % (r, *per[r]))
    split = [rid for rid, _, mk in M if mk.count("N") >= 3]
    print("  rows with >=3 N:", " ".join(split))

    # suite
    rows = []
    inc = 0
    singles = 0
    core = []
    new_fam = 0
    executed = 0
    for nid, mut, resp, inh, src in N:
        k = len([r for r in src if r in REPORTS])
        inc += k
        if k == 1:
            singles += 1
        if k >= 5:
            core.append(nid)
        if not inh:
            new_fam += 1
        if any(v == "E" for v in src.values()):
            executed += 1
        rows.append([nid, mut, resp, inh, k] + [src.get(r, "") for r in REPORTS] + [src.get("Synthesis", "")])
    write_csv("negative_suite.csv", ["id", "mutation", "required_response", "inherits_round3", "reports"] + REPORTS + ["parallel_synthesis"], rows)
    print("suite families=%d report_incidences=%d singletons=%d new_families=%d executed_somewhere=%d core(>=5)=%d: %s" % (
        len(N), inc, singles, new_fam, executed, len(core), " ".join(core)))
    print("  from parallel synthesis: E=%d P=%d" % (sum(1 for *_, s in N if s.get("Synthesis") == "E"), sum(1 for *_, s in N if s.get("Synthesis") == "P")))
    per = {r: [0, 0, 0] for r in REPORTS}
    for *_, src in N:
        for r, v in src.items():
            if r in per:
                per[r]["ETP".index(v)] += 1
    for r in REPORTS:
        print("  %-8s E=%2d T=%2d P=%2d total=%2d" % (r, *per[r], sum(per[r])))

    # questions
    rows = []
    for qid, q, cons, var, mk in Q:
        assert len(mk) == 9, qid
        rows.append([qid, q, cons, var, mk.count("Y"), mk.count("P")] + list(mk))
    write_csv("question_tally.csv", ["id", "question", "consensus", "variants", "explicit", "implicit"] + REPORTS, rows)
    print("questions=%d explicit-all=%d" % (len(Q), sum(1 for *_, mk in Q if mk == "Y" * 9)))

    # lean
    write_csv("lean_files.csv", ["report", "file", "imports", "lines", "theorems", "result", "warnings", "elapsed_ms"], [list(x) for x in LEAN])
    write_csv("new_experiments.csv", ["file", "imports", "lines", "theorems", "examples", "result", "elapsed_ms"], [list(x) for x in NEW])
    write_csv("codex_followups.csv", ["file", "imports", "expected", "result", "elapsed_ms"], [list(x) for x in CODEX])
    ok = sum(1 for x in LEAN if x[5].startswith("compiles"))
    print("lean shipped files=%d lines=%d theorems=%d compile=%d warnings=%d" % (
        len(LEAN), sum(x[3] for x in LEAN), sum(x[4] for x in LEAN), ok, sum(x[6] for x in LEAN)))
    print("  per report:", " ".join("%s=%d" % (r, sum(1 for x in LEAN if x[0] == r)) for r in REPORTS))

    # companion reruns
    write_csv("companion_runs.csv", ["report", "command", "reported", "reproduced", "elapsed_ms"], [list(x) for x in RUNS])
    print("companion runs=%d" % len(RUNS))

    # LaTeX rows
    lines = []
    prev = ""
    for rid, text, marks in M:
        if prev and rid[0] != prev:
            lines.append(r"\addlinespace[2pt]")
        prev = rid[0]
        lines.append("%s & %s & %s & %s\\\\" % (rid, tex(text), " & ".join(MARK[c] for c in marks),
                                              r"$\dagger$" if rid in INHERITED else ""))
    write_tex("matrix_rows.tex", lines)
    lines = []
    for qid, q, cons, var, mk in Q:
        if qid == "Q1":
            lines.append(r"\midrule")
        lines.append("%s & %s & %s & %s & %d\\\\" % (qid, tex(q), tex(cons), tex(var), mk.count("Y")))
    write_tex("question_rows.tex", lines)
    lines = []
    prev = ""
    for rep, f, imp, ln, th, res, w, ms in LEAN:
        if prev and rep != prev:
            lines.append(r"\addlinespace[2pt]")
        prev = rep
        lines.append(r"%s & \code{%s} & %s & %d & %d & %s & %s\\" % (rep, f, imp, ln, th, tex(res), "{:,}".format(ms) if ms else ""))
    write_tex("lean_rows.tex", lines)
    lines = []
    for rep, cmd, rep_c, repro, ms in RUNS:
        lines.append(r"%s & \code{%s} & %s & %s & %s\\" % (rep, cmd, tex(rep_c), tex(repro), "{:,}".format(ms)))
    write_tex("run_rows.tex", lines)
    lines = []
    for nid, mut, resp, inh, src in N:
        lines.append("%s & %s & %s & %s & %s & %s\\\\" % (nid, tex(mut), tex(resp), inh, " & ".join(src.get(r, "") for r in REPORTS), src.get("Synthesis", "")))
    write_tex("suite_rows.tex", lines)
    lines = []
    for f, imp, ln, th, ex, res, ms in NEW:
        lines.append(r"\code{%s} & %s & %d & %d & %d & %s & %s\\" % (f, imp, ln, th, ex, tex(res), "{:,}".format(ms)))
    lines.append(r"\midrule")
    for f, imp, exp, res, ms in CODEX:
        lines.append(r"\code{%s} & %s & & & & %s & %s\\" % (f, imp, tex(exp + "; " + res), "{:,}".format(ms) if ms else ""))
    write_tex("new_rows.tex", lines)


if __name__ == "__main__":
    main()
