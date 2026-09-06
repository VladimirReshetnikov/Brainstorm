# Exact-arithmetic companion reruns

These are fresh reruns of the unchanged Accord, Cadence and Concord Python companions, made during synthesis review on 2026-09-06 UTC. They are finite Python evidence, not Lean proofs or implementations of the proposed languages.

The interpreter was Python 3.14.4. Each command used `PYTHONDONTWRITEBYTECODE=1` and exited 0; every generated file was routed into this evidence directory.

Run from the Brainstorm repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B docs/round-2/ideas/accord/certificate_lab.py --report docs/round-2/synthesis/evidence/accord-cadence-concord/accord-rerun.json *> docs/round-2/synthesis/evidence/accord-cadence-concord/accord-stdout.txt
python -B docs/round-2/ideas/cadence/certificate_exhibits.py docs/round-2/synthesis/evidence/accord-cadence-concord/cadence-rerun.json *> docs/round-2/synthesis/evidence/accord-cadence-concord/cadence-stdout.txt
python -B docs/round-2/ideas/concord/checks.py --output docs/round-2/synthesis/evidence/accord-cadence-concord/concord-rerun.json *> docs/round-2/synthesis/evidence/accord-cadence-concord/concord-stdout.txt
```

Results use different counting units:

- Accord: 25 unittest methods, 0 failures and 0 errors. Some methods contain many finite samples. Its separate 26-case proposed adversarial language suite was not executed.
- Cadence: 267 recorded Boolean checks, including 190 degree/parameter comparisons (10 degrees for 19 parameter pairs, three in the dual-number algebra).
- Concord: 459 recorded checks: 441 binomial instances, 5 implicit residual coefficients, 4 symbolic Abel coefficient polynomial identities, 7 negative neighbors, and 2 rational root-bound inequalities.

The report outputs and stdout logs are retained independently of the originals. `crosswalk.json` contains 24 source-cited design commitments, not implementation results. The comparative memo explains test limitations and the distinction between symbolic polynomial identities at finitely many degrees and sampled parameter checks.

SHA256 of the unchanged scripts executed:

| Script | SHA256 |
|---|---|
| Accord certificate_lab.py | DCC456F4EE97C3CD35E9A9BFA5CE0C53711B8FAB3F556C58806F50124BF0EEF7 |
| Cadence certificate_exhibits.py | 4ABFEE1B12BB673CB759DF5724C8B0E588FDB0F22335D2F874CA9830B419BAE3 |
| Concord checks.py | 676BDEC73AE0CA6CE205C3A812A9035985C0D2E3E7C88FA8A5DDA8C80B99C7B1 |

