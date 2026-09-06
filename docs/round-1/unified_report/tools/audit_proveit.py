#!/usr/bin/env python3
"""Heuristic, text-level audit of tactic usage in a Lean 4 corpus.

Classifies each tactic invocation (a proof line whose first token is a tactic
keyword, or a `calc` step) into coarse families that mirror the taxonomy the
nine design reports under docs/ideas converge on:

  ASSERT   author-stated intermediate facts (have/obtain/calc steps/suffices/let/set)
  OBLIG    one-line obligations: `have ... := by <decision procedure>` and similar
  CAST     casts and representation transport (push_cast, exact_mod_cast, Nat.cast_*, algebraMap, map_*)
  INDEX    finite-sum / interval / index management (sum_range_succ, mem_range, sum_congr, Ico/Icc, powerset)
  ANALYSIS filter/derivative/continuity/integral plumbing (filter_upwards, fun_prop, EventuallyEq, HasDerivAt, nhds)
  SIDE     arithmetic/order side-condition procedures (omega, linarith, nlinarith, positivity, norm_num, bound, decide, gcongr)
  NORM     algebraic normalization (ring, field_simp, linear_combination, abel, module)
  REPR     syntactic reshaping with no new mathematics (change, show, unfold, dsimp, funext, ext, congr, convert, conv)
  REWRITE  rw/simp with ordinary library lemmas (library-interface work)
  STRUCT   logical plumbing: intro, refine, apply, exact, constructor, cases, induction, by_cases, ...

This is a heuristic on source text, not an InfoTree analysis; it cannot see
what a tactic actually did.  It estimates proportions; it certifies nothing.

Usage:  python audit_proveit.py <root-dir> [--sample <file> ...]
Writes audit_results.json in the current directory and prints a summary.
"""
import sys, re, json, os, statistics, collections

CAST_LEMMA = re.compile(r"(Nat\.cast|Int\.cast|Rat\.cast|Complex\.ofReal|ofReal|algebraMap|\bmap_(mul|add|sum|pow|sub|neg|one|zero|natCast|intCast|prod|div|inv)\b|smul_eq_mul|nsmul_eq_mul|zsmul_eq_mul|\bcoe_|_coe\b|natCast|intCast|ratCast|\bcast_|NNReal\.coe|ENNReal\.|toReal|\bzify\b|\bqify\b)")
INDEX_LEMMA = re.compile(r"(sum_range_succ|prod_range_succ|Finset\.range|mem_range|mem_Icc|mem_Ico|mem_Ioc|sum_congr|prod_congr|sum_Ico|Ico_|Icc_|Fin\.sum_univ|sum_univ|sum_image|sum_bij|sum_nbij|sum_add_distrib|sum_sub_distrib|mul_sum|sum_mul|sum_comm|sum_sigma|sum_product|powerset|card_|sum_filter|sum_ite|sum_const|sum_empty|sum_singleton|sum_insert|range_succ|Finset\.sum|Finset\.prod|sum_div|sum_smul|smul_sum|sum_neg_distrib|Finset\.induction|geom_sum|sum_range_reflect|sum_range_id)")
ANALYSIS_LEMMA = re.compile(r"(HasDerivAt|HasFDerivAt|\bderiv\b|iteratedDeriv|EventuallyEq|eventuallyEq|Eventually|eventually|\bnhds\b|𝓝|Filter\.|Tendsto|tendsto|intervalIntegral|integral_|Integrable|Continuous|continuous|Differentiable|differentiable|MeasureTheory|\bae_|Measurable|measurable|IsOpen|isOpen|mem_nhds|Metric\.|dist_|norm_|‖|HasSum|Summable|tsum|ContDiff|contDiff|Real\.exp|Real\.log|Real\.sqrt|Real\.cos|Real\.sin|Real\.pi)")
NATSUB_LEMMA = re.compile(r"(Nat\.sub_|Nat\.succ_sub|Nat\.add_sub|tsub_|Nat\.lt_succ|Nat\.le_|Nat\.lt_|Nat\.succ_le|Nat\.pos_|Nat\.div_|Nat\.mod_|Nat\.pow_|Nat\.choose|Nat\.factorial|Nat\.sqrt|Nat\.even|Nat\.odd|Nat\.two_mul|Nat\.mul_)")

HEAD_CLASS = {
  'push_cast':'CAST','norm_cast':'CAST','exact_mod_cast':'CAST','zify':'CAST','qify':'CAST','lift':'CAST',
  'apply_mod_cast':'CAST','rw_mod_cast':'CAST','simp_mod_cast':'CAST',
  'omega':'SIDE','linarith':'SIDE','nlinarith':'SIDE','positivity':'SIDE','norm_num':'SIDE','norm_num1':'SIDE',
  'bound':'SIDE','decide':'SIDE','interval_cases':'SIDE','fin_cases':'SIDE','polyrith':'SIDE','gcongr':'SIDE',
  'mono':'SIDE','cancel_denoms':'SIDE',
  'ring':'NORM','ring_nf':'NORM','ring1':'NORM','field_simp':'NORM','linear_combination':'NORM','abel':'NORM',
  'abel_nf':'NORM','module':'NORM','noncomm_ring':'NORM','group':'NORM',
  'filter_upwards':'ANALYSIS','fun_prop':'ANALYSIS','continuity':'ANALYSIS','measurability':'ANALYSIS',
  'change':'REPR','show':'REPR','unfold':'REPR','dsimp':'REPR','funext':'REPR','ext':'REPR','congr':'REPR',
  'convert':'REPR','conv':'REPR','conv_lhs':'REPR','conv_rhs':'REPR','delta':'REPR',
  'rw':'REWRITE','rewrite':'REWRITE','erw':'REWRITE','rwa':'REWRITE','simp':'REWRITE','simpa':'REWRITE',
  'simp_all':'REWRITE','simp?':'REWRITE','simp_rw':'REWRITE',
  'have':'ASSERT','obtain':'ASSERT','rcases':'ASSERT','let':'ASSERT','set':'ASSERT','calc':'ASSERT',
  'suffices':'ASSERT','replace':'ASSERT','haveI':'ASSERT','letI':'ASSERT','choose':'ASSERT',
  'intro':'STRUCT','rintro':'STRUCT','refine':'STRUCT','apply':'STRUCT','exact':'STRUCT','constructor':'STRUCT',
  'use':'STRUCT','cases':'STRUCT','induction':'STRUCT','by_cases':'STRUCT','by_contra':'STRUCT','left':'STRUCT',
  'right':'STRUCT','exfalso':'STRUCT','subst':'STRUCT','symm':'STRUCT','trans':'STRUCT','specialize':'STRUCT',
  'generalize':'STRUCT','revert':'STRUCT','clear':'STRUCT','classical':'STRUCT','infer_instance':'STRUCT',
  'all_goals':'STRUCT','any_goals':'STRUCT','try':'STRUCT','first':'STRUCT','repeat':'STRUCT','iterate':'STRUCT',
  'split':'STRUCT','split_ifs':'STRUCT','next':'STRUCT','case':'STRUCT','aesop':'STRUCT','tauto':'STRUCT',
  'trivial':'STRUCT','rfl':'STRUCT','assumption':'STRUCT','contradiction':'STRUCT','exact?':'STRUCT',
  'apply?':'STRUCT','nomatch':'STRUCT','match':'STRUCT','push_neg':'STRUCT','contrapose':'STRUCT',
  'contrapose!':'STRUCT','absurd':'STRUCT','exists':'STRUCT',"refine'":'STRUCT',"induction'":'STRUCT',
  "cases'":'STRUCT','nofun':'STRUCT','exacts':'STRUCT','grind':'STRUCT','peel':'STRUCT','wlog':'STRUCT',
  'by_contra!':'STRUCT',
}
INLINE_OBLIG = re.compile(r":=\s*by\s+(omega|linarith|nlinarith|positivity|norm_num|simp|simpa|decide|exact_mod_cast|push_cast|norm_cast|ring|ring_nf|field_simp|bound|fun_prop|continuity|measurability|gcongr|abel|linear_combination|aesop|trivial|rfl)\b[^\n]*$")
INLINE_HEAD = re.compile(r":=\s*by\s+([A-Za-z_?!']+)")
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+|nonrec\s+)*(theorem|lemma)\s+([^\s:({\[]+)")
TOPLEVEL = re.compile(r"^(?:@\[|theorem\b|lemma\b|def\b|instance\b|abbrev\b|structure\b|inductive\b|class\b|end\b|section\b|namespace\b|open\b|variable\b|private\b|protected\b|noncomputable\b|#|/-|set_option\b|attribute\b|example\b|macro\b|syntax\b|elab\b|notation\b|scoped\b|local\b|universe\b|deriving\b|alias\b|export\b|import\b|mutual\b|termination_by\b|decreasing_by\b|unseal\b|opaque\b|axiom\b)")
CALCSTEP = re.compile(r"^\s*_\s*(=|≤|<|≥|>|≠|≡|∣|⊆|⊂|∈|⟶|→|↔|=ᶠ|≃|∼|≈|≪)")
BULLET = re.compile(r"^\s*(·|\.|\|)\s*")

def strip_comments(text):
    out = []; depth = 0; i = 0; n = len(text)
    while i < n:
        if text.startswith('/-', i):
            depth += 1; i += 2; continue
        if depth and text.startswith('-/', i):
            depth -= 1; i += 2; continue
        if depth:
            if text[i] == '\n': out.append('\n')
            i += 1; continue
        if text.startswith('--', i):
            j = text.find('\n', i); i = n if j < 0 else j; continue
        out.append(text[i]); i += 1
    return ''.join(out)

def head_of(line):
    s = line.strip()
    m = BULLET.match(line)
    if m: s = line[m.end():].strip()
    if CALCSTEP.match(line): return 'calc_step', s
    tok = s.split(None, 1)[0] if s else ''
    tok = tok.rstrip(',;')
    return tok, s

def classify(tok, s):
    if tok == 'calc_step': return 'ASSERT'
    cls = HEAD_CLASS.get(tok)
    if cls is None: return None
    if cls == 'ASSERT':
        return 'OBLIG' if INLINE_OBLIG.search(s) else 'ASSERT'
    if cls in ('REWRITE', 'STRUCT', 'REPR'):
        if CAST_LEMMA.search(s): return 'CAST'
        if INDEX_LEMMA.search(s): return 'INDEX'
        if ANALYSIS_LEMMA.search(s): return 'ANALYSIS'
        if NATSUB_LEMMA.search(s): return 'SIDE'
        return cls
    return cls

def audit_file(path):
    text = strip_comments(open(path, encoding='utf-8', errors='replace').read())
    lines = text.split('\n')
    stats = collections.Counter(); heads = collections.Counter(); inline = collections.Counter()
    bigrams = collections.Counter(); classbigrams = collections.Counter()
    castlemmas = collections.Counter()
    proofs = []
    i = 0; N = len(lines)
    while i < N:
        m = DECL.match(lines[i])
        if not m:
            i += 1; continue
        name = m.group(2); body = []; k = i; started = False
        while k < N:
            ln = lines[k]
            if k > i and ln.strip() and not ln[0].isspace() and TOPLEVEL.match(ln): break
            if not started:
                if ':=' in ln:
                    started = True; body.append(ln.split(':=', 1)[1])
            else:
                body.append(ln)
            k += 1
        first = ' '.join(b for b in body[:2] if b.strip())
        term_mode = not re.search(r"(^|\s)by(\s|$)", first)
        ntac = 0; prev = None; prevcls = None; pstats = collections.Counter()
        for b in body:
            if not b.strip(): continue
            tok, s = head_of(b)
            cls = classify(tok, s)
            if cls is None: continue
            ntac += 1; stats[cls] += 1; heads[tok] += 1; pstats[cls] += 1
            if cls == 'OBLIG':
                mh = INLINE_HEAD.search(s); inline[mh.group(1) if mh else '?'] += 1
            if cls == 'CAST':
                for lm in re.findall(r"[A-Za-z_][A-Za-z0-9_.']*", s):
                    if CAST_LEMMA.search(lm): castlemmas[lm] += 1
            if prev:
                bigrams[(prev, tok)] += 1; classbigrams[(prevcls, cls)] += 1
            prev, prevcls = tok, cls
        nl = sum(1 for b in body if b.strip())
        proofs.append((name, nl, ntac, term_mode, pstats))
        i = max(k, i + 1)
    return stats, heads, inline, bigrams, classbigrams, castlemmas, proofs

RECON = ('OBLIG', 'CAST', 'INDEX', 'REPR', 'NORM', 'SIDE', 'ANALYSIS')

def bucket(nl):
    return '<=3' if nl <= 3 else '4-10' if nl <= 10 else '11-30' if nl <= 30 else '>30'

def summarize(files, label):
    S = collections.Counter(); H = collections.Counter(); I = collections.Counter()
    B = collections.Counter(); CB = collections.Counter(); CL = collections.Counter(); P = []
    perfile = []; bucket_stats = collections.defaultdict(collections.Counter)
    bucket_theorems = collections.Counter()
    for f in files:
        s, h, i, b, cb, cl, p = audit_file(f)
        S += s; H += h; I += i; B += b; CB += cb; CL += cl; P += p
        ft = sum(s.values())
        if ft >= 40:
            perfile.append((os.path.basename(f), ft, round(100 * sum(s[c] for c in RECON) / ft, 1)))
        for (name, nl, ntac, tm, pstats) in p:
            bucket_theorems[bucket(nl)] += 1
            bucket_stats[bucket(nl)] += pstats
    tot = sum(S.values())
    lens = [p[1] for p in P]
    buckets = {}
    for bk, cnt in bucket_stats.items():
        bt = sum(cnt.values())
        buckets[bk] = {'theorems': bucket_theorems[bk], 'invocations': bt,
                       'share_of_invocations_pct': round(100 * bt / tot, 1) if tot else 0,
                       'recon_pct': round(100 * sum(cnt[c] for c in RECON) / bt, 1) if bt else 0,
                       'assert_pct': round(100 * cnt['ASSERT'] / bt, 1) if bt else 0,
                       'rewrite_pct': round(100 * cnt['REWRITE'] / bt, 1) if bt else 0,
                       'struct_pct': round(100 * cnt['STRUCT'] / bt, 1) if bt else 0}
    perfile.sort(key=lambda t: -t[2])
    res = {'label': label, 'files': len(files), 'theorems': len(P), 'tactic_invocations': tot,
           'term_mode_theorems': sum(1 for p in P if p[3]),
           'class_counts': dict(S),
           'class_pct': {k: round(100 * v / tot, 1) for k, v in S.items()} if tot else {},
           'top_heads': H.most_common(40), 'inline_obligation_heads': I.most_common(20),
           'top_cast_lemmas': CL.most_common(25),
           'top_head_bigrams': [[list(k), v] for k, v in B.most_common(30)],
           'top_class_bigrams': [[list(k), v] for k, v in CB.most_common(20)],
           'recon_pct_total': round(100 * sum(S[c] for c in RECON) / tot, 1) if tot else 0,
           'length_buckets': buckets,
           'top_files_by_recon_share': perfile[:15],
           'bottom_files_by_recon_share': perfile[-10:],
           'proof_lines': {'median': statistics.median(lens) if lens else 0,
                           'mean': round(statistics.mean(lens), 1) if lens else 0,
                           'p90': sorted(lens)[int(0.9 * len(lens)) - 1] if lens else 0,
                           'max': max(lens) if lens else 0,
                           'le3': sum(1 for l in lens if l <= 3),
                           'gt30': sum(1 for l in lens if l > 30)}}
    return res

if __name__ == '__main__':
    root = sys.argv[1]; args = sys.argv[2:]
    sample = args[args.index('--sample') + 1:] if '--sample' in args else []
    allfiles = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != '.lake']
        allfiles += [os.path.join(dp, f) for f in fn if f.endswith('.lean')]
    out = {'corpus': summarize(sorted(allfiles), root)}
    if sample:
        out['sample'] = summarize(sample, 'sampled-by-reports')
    json.dump(out, open('audit_results.json', 'w'), indent=1)
    for key in out:
        r = out[key]
        print('==', r['label'], 'files', r['files'], 'theorems', r['theorems'],
              'invocations', r['tactic_invocations'], 'term-mode', r['term_mode_theorems'])
        for k, v in sorted(r['class_pct'].items(), key=lambda kv: -kv[1]):
            print(f"  {k:9s} {v:5.1f}%  ({r['class_counts'][k]})")
        print('  proof lines', r['proof_lines'])
        print('  inline obligations', r['inline_obligation_heads'][:12])
        print('  cast lemmas', r['top_cast_lemmas'][:12])
        print('  class bigrams', r['top_class_bigrams'][:10])
        print('  head bigrams', r['top_head_bigrams'][:12])
