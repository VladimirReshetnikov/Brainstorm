-- Experiment: kernel-checked polynomial certificate (reflective, `decide`) versus
-- native evaluation (`native_decide`) on the toolchain ProveIt pins (v4.32.0).
-- Dense integer polynomials, lowest degree first. No Mathlib import.
def padd : List Int -> List Int -> List Int
  | [], q => q
  | p, [] => p
  | a :: p, b :: q => (a + b) :: padd p q
def pscale (c : Int) (p : List Int) : List Int := p.map (fun x => c * x)
def pmul : List Int -> List Int -> List Int
  | [], _ => []
  | a :: p, q => padd (pscale a q) (0 :: pmul p q)
def pneg (p : List Int) : List Int := p.map (fun x => -x)
def psub (p q : List Int) : List Int := padd p (pneg q)
def isZero (p : List Int) : Bool := p.all (fun x => x == 0)
/-- Ideal-membership certificate: p = sum_i q_i * f_i, checked by exact arithmetic. -/
def check (p : List Int) (fs qs : List (List Int)) : Bool :=
  isZero (psub p (List.foldl padd [] (List.zipWith pmul qs fs)))
/-- p_n = X^n - 1 -/
def xn1 (n : Nat) : List Int := (-1) :: (List.replicate (n - 1) 0 ++ [1])
/-- q_n = 1 + X + ... + X^(n-1), so that p_n = q_n * (X - 1). -/
def geom (n : Nat) : List Int := List.replicate n 1
/-- A corrupted certificate: one coefficient altered. -/
def geomBad (n : Nat) : List Int := List.replicate (n - 1) 1 ++ [2]

set_option maxRecDepth 100000
set_option maxHeartbeats 40000000
set_option profiler true
set_option profiler.threshold 0
theorem kernel_10 : check (xn1 10) [[-1, 1]] [geom 10] = true := by decide
theorem kernel_40 : check (xn1 40) [[-1, 1]] [geom 40] = true := by decide
theorem kernel_160 : check (xn1 160) [[-1, 1]] [geom 160] = true := by decide
theorem kernel_640 : check (xn1 640) [[-1, 1]] [geom 640] = true := by decide
theorem kernel_1280 : check (xn1 1280) [[-1, 1]] [geom 1280] = true := by decide
theorem native_10 : check (xn1 10) [[-1, 1]] [geom 10] = true := by native_decide
theorem native_40 : check (xn1 40) [[-1, 1]] [geom 40] = true := by native_decide
theorem native_160 : check (xn1 160) [[-1, 1]] [geom 160] = true := by native_decide
theorem native_640 : check (xn1 640) [[-1, 1]] [geom 640] = true := by native_decide
theorem native_1280 : check (xn1 1280) [[-1, 1]] [geom 1280] = true := by native_decide

/-! Residual certificate for a finite jet (the certificate three reports derive independently):
the Catalan series C = 1 + X C^2 in Z[[X]]. The jet c = 1 + X + 2X^2 + 5X^3 + 14X^4 + 42X^5
has residual c - 1 - X c^2 vanishing below degree 6, while its degree-6 coefficient is -132,
so c is a jet of C modulo X^6 and not an exact solution. -/
def catalanJet : List Int := [1, 1, 2, 5, 14, 42]
def catalanResidual : List Int := psub catalanJet (padd [1] (0 :: pmul catalanJet catalanJet))
theorem catalan_jet_ok : (catalanResidual.take 6).all (fun x => x == 0) = true := by decide
theorem catalan_not_exact : catalanResidual[6]? = some (-132) := by decide
/-- Precision loss under differentiation: X^N and 0 agree below N, their derivatives do not. -/
def pderiv (p : List Int) : List Int := List.zipWith (fun (c : Int) (k : Nat) => c * ((k : Int) + 1)) (p.drop 1) (List.range (p.length - 1))
theorem deriv_loses_order : (pderiv [0,0,0,0,0,1]).take 5 ≠ (pderiv [0,0,0,0,0,0]).take 5 := by decide
#print axioms catalan_jet_ok
#print axioms kernel_1280
#print axioms native_1280
