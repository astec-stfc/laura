# RF-Track API Notes (distilled from RF-Track Reference Manual v2.5)

Install: `pip install RF_Track` (Python bindings exist; Octave bindings also exist via a
compiled `.oct` file — this manual gives most examples in Octave but states the
conversion to Python is straightforward). Licensing/citation boilerplate omitted.

## 1. Overview

RF-Track is a CERN-developed (A. Latina, BE-ABP) particle tracking / beam-dynamics code
written in optimized parallel C++ with Octave and Python as user-facing scripting
interfaces. It can track beams of particles of arbitrary energy, mass and charge (even
mixed species), solving fully relativistic equations of motion, including space-charge,
collective effects, and complex/real 1D-3D static or oscillating RF field maps.

Architecture concept:
- Two beam representations: **Bunch6d** (tracking "in space", using the longitudinal
  coordinate S as the independent/integration variable — the classical matrix-optics
  model where all particles share a common longitudinal plane) and **Bunch6dT**
  (tracking "in time", using time t as the independent variable — needed when particles
  can be created/emitted at arbitrary times/locations, e.g. cathodes, and needed for
  accurate 3D space-charge).
- Two tracking environments, each paired with one beam type: **Lattice** (works with
  Bunch6d; represents the accelerator as a strictly sequential — MAD-X-like — list of
  elements, transported element-by-element from entrance to exit plane) and **Volume**
  (works with Bunch6dT; elements can be placed at arbitrary 3D position/orientation and
  may overlap; supports fully time-integrated tracking, backward propagation, particle
  creation, realistic fringe fields, and is the natural place for space-charge-dominated
  regions such as injectors). A Volume can itself be inserted into a Lattice as a single
  element (and vice versa — see section 6).
- A **Beam** object is a set of individual Bunch6d/Bunch6dT bunches at arbitrary
  spacing, for multi-bunch simulations (bunch trains).

## 2. Beam/Bunch definition API

### Units (internal, always used regardless of Octave/Python)

| Quantity | Symbol | Unit |
|---|---|---|
| Bunch population | N | number (real particles) |
| Particle mass | m | MeV/c² |
| Particle charge | Q | e |
| Particle positions | x, y, z / X, Y, Z | mm |
| Particle angles | x', y' | mrad |
| Particle momenta | Px, Py, Pz, P | MeV/c |
| Particle energy | E | MeV |
| Time (particle arrival/creation) | t | **mm/c** (not seconds!) |
| Element offsets/positions | Xo, Yo, Zo | m |
| Element pitch/yaw/roll | — | rad |

Predefined constants (via `RF_Track.<name>` in Octave, same in Python):
`clight` [m/s], `electronmass`, `protonmass`, `muonmass` [MeV/c²], `muonlifetime`
[mm/c], time-unit helpers `s, ms, us, ns, ps, fs` (all expressed in mm/c, e.g.
`RF_Track.ps` converts picoseconds to mm/c), charge-unit helpers `C, mC, uC, nC, pC`
(in e). `RF_Track.electron_anomalous_magnetic_moment` (0.00115), `proton_...` (1.792),
`muon_...` (0.00116) for spin tracking. `RF_Track.version`,
`RF_Track.max_number_of_threads` / `RF_Track.number_of_threads` (or in Python,
`RF_Track.cvar.number_of_threads`).

### Bunch6d ("tracking in space")

State vector per macro-particle: `(x, x', y, y', t, P, m, Q, N)`. Also stores the
current longitudinal coordinate `B.S` [m] along the Lattice.

Constructors:
```
B = Bunch6d(mass, population, charge, Pref, Twiss, nParticles, sigmaCut=0)
B = Bunch6d(mass, population, charge, [X XP Y YP T P ID])
B = Bunch6d(mass, population, charge, [X XP Y YP T P])
B = Bunch6d([X XP Y YP T P MASS Q N ID])
B = Bunch6d([X XP Y YP T P MASS Q N])
B = Bunch6d([X XP Y YP T P MASS Q])
B = Bunch6d()   # empty bunch
```
Arguments: `mass` [MeV/c²], `population` [#], `charge` [e], `Pref` reference momentum
[MeV/c], `Twiss` an instance of `Bunch6d_twiss`, `nParticles` number of macro-particles
[#], `sigmaCut` truncate distribution at N sigma if >0. Column-vector inputs:
`X,Y` [mm], `T` [mm/c], `P` [MeV/c], `XP,YP` [mrad], `MASS` [MeV/c²], `Q` [e], `N` [#],
`ID` [integer].

`get_phase_space(format='%x %xp %y %yp %t %Pc', which='good')` returns a matrix; `which`
is `'all'|'good'` (default good = excludes lost particles). Identifiers accepted (Table
2.1, partial): `%x %y` [mm], `%t` [mm/c], `%dt` [mm/c], `%z` [mm, w.r.t. reference
particle], `%deg@MHz` (e.g. `%deg@750`) [deg], `%K %E` [MeV], `%P` [MeV/c], `%d`
relative momentum [permille], `%xp %yp` [mrad], `%tp` [mrad/c], `%Px %Py %Pz` [MeV/c],
`%px %py %pz` normalized momenta [mrad], `%pt` normalized energy diff [permille],
`%Vx %Vy %Vz` [c], `%m` [MeV/c²], `%Q` [e+], `%N` [#], `%id` [#].

`set_phase_space([X XP Y YP T P])` — only accepts the full 6-column matrix in this
column order.

Other conventions available through `get_phase_space` format strings (from Ch.9 example):
- MAD-X convention: `"%x %px %y %py %Z %pt"`
- TRANSPORT convention: `"%x %xp %y %yp %dt %d"`
- PLACET convention: `"%E %x %y %dt %xp %yp"`

### Bunch6dT ("tracking in time")

State vector per macro-particle: `(X, Px, Y, Py, Z, Pz, m, Q, N, t0)`. `t0` = creation
time of each particle (enables cathode/emission simulation). `B.t` [mm/c] = the common
clock/time at which the bunch is taken (read/write).

Constructors: same pattern as Bunch6d but with `[X Px Y Py Z Pz ID]`,
`[X Px Y Py Z Pz MASS Q N T0 ID]` etc., and phase-space columns `X,Y,Z` [mm],
`Px,Py,Pz` [MeV/c], `T0` creation time [mm/c].

`get_phase_space()` identifiers (Table 2.2) mirror Bunch6d's but with absolute
`%X %Y %Z` [mm], `%Px %Py %Pz` [MeV/c] instead of transverse-angle-based columns; also
has `%t0` [mm/c] (creation time).

### Conversion Bunch6d <-> Bunch6dT

`B0T = Bunch6dT(B0)` converts Bunch6d -> Bunch6dT: all particles set to the same
longitudinal coordinate `B0.S`; the original arrival-time distribution becomes the
distribution of creation times. **The reverse conversion (Bunch6dT -> Bunch6d) is not
supported** because a Bunch6dT's particles are not all at the same longitudinal plane.

### Coasting beams / lifetime / offsetting

- `B.set_coasting(L)` — L = period length [mm]; both Bunch6d/Bunch6dT.
- `B.set_lifetime(T)` — T = lifetime [mm/c]; particles reaching end-of-life are flagged
  lost. `RF_Track.muonlifetime` predefined.
- `B_offset = B.displaced(dx, dy, dz, roll, pitch, yaw)` — dx,dy,dz [mm]; roll/pitch/yaw
  (rotation around Z/X/Y) [mrad].

### Multi-bunch beams (`Beam`)

`Beam` is a set of individual bunches at arbitrary spacing (bunch train). Enables
per-bunch single-bunch effects (space charge) plus dedicated long-range algorithms
(wakefields) between bunches; bunches can have different charges/species, and some
bunches can be multi-particle while others are single macro-particle for speed.
```
Beam0 = Beam()                       # or Beam(n_bunches, spacing)
Beam0.append(bunch)                  # first bunch added "as is"
Beam0.append(bunch, spacing)         # spacing in mm/c (Bunch6d) or mm (Bunch6dT)
Beam0.append(n_bunches, bunch, spacing)
```
Tracking: `B1 = Line.track(B0)`, then in Octave `B1{1}`, `B1{2}`, ...; in Python
`B1[0]`, `B1[1]`, ... (0-indexed).

### Spin polarization tracking (since v2.5.0)

Each particle carries an anomalous magnetic moment G and a unit 3D spin vector S,
evolving per the Thomas-BMT equation using lab-frame E and B fields (T, V/m).
```
B0.set_polarization(anomalous_magnetic_moment, P)              # P: scalar 0..1 (vertical) or Nx3 matrix
B0.set_polarization(anomalous_magnetic_moment, P, Sx, Sy, Sz)   # arbitrary direction
```
v2.4.1 auto-normalized the spin vector to 1; v2.4.2+ allows magnitude <1 (average
polarization of real particles in the macro-particle); inputs >1 are clamped to 1.
Query per-particle: `get_phase_space("%Sx %Sy %Sz")`. Average along a lattice via
transport table identifiers `%mean_Sx %mean_Sy %mean_Sz`.

## 3. Lattice construction API

`Lattice` represents the accelerator as a **strictly sequential list of elements**
(MAD-X-sequence style), transported element-by-element, entrance to exit.
```
L = Lattice()
L.append(element)          # or L.append(lattice) — nested lattice treated as 1 element ("girder")
L.insert(lattice)          # flattens: sub-elements appended one by one, container identity lost
```
Elements/lattices are added **by value** (a copy) by default — modifying the original
afterward does not affect the copy in `L`. To add **by reference** (so later
modifications propagate, and to avoid duplicating memory for e.g. large field maps),
use `L.append_ref(element)` / `L.insert_ref(lattice)`.

Adding with misalignment:
```
L.append(element, dX, dY, dZ, reference="entrance")
L.append(element, dX, dY, dZ, roll, pitch, yaw, reference="entrance")
L.append_ref(...)   # same signatures
```
`dX,dY,dZ` [m]; `roll` = rotation about Z, `pitch` about X, `yaw` about Y, all [rad]
(Tait-Bryan convention, no small-angle approximation). `reference` in
`{"entrance","center","exit"}`.

Random misalignment: `L.scatter_elements(type, dX, dY, dZ, roll, pitch, yaw,
reference="entrance")` (rms values, dX/dY/dZ [mm], angles [mrad]) — `type` one of
`bpm, sbend, lattice, absorber, solenoid, sextupole, multipole, corrector, rf_elememt`
[sic]; omitting `type` scatters all elements (including inside nested lattices).

Accessing/modifying elements by index or name (wildcards accepted):
- Octave: `L{1}`, `L{'NAME'}`
- Python: `L[0]`, `L['NAME']`
Element attributes can be changed dynamically after being added, e.g.
`L{1}.set_strength(2)`.

Tracking: `B1 = L.track(B0)` — single argument (the beam), returns beam at lattice exit.

### Importing a MAD-X lattice

```
L = Lattice("twiss_file.tws")
```
Converts an entire MAD-X Twiss output file into an RF-Track Lattice. The Twiss file
must be produced in MAD-X with:
```
select, flag=twiss, full;
twiss, file=twiss_file.tws;
```
If the lattice is a transfer line (non-periodic — no periodic Twiss solution), initial
Twiss parameters must be given explicitly in MAD-X, e.g.:
```
call, file="linac4.seq";
use, sequence=linac4;
select, flag=twiss, full;
twiss, betx=0.451, alfx=-3.599, bety=2.236, alfy=-10.419, file=linac4.twiss;
```

### Volume construction & element placement

```
V = Volume()   # no input options
V.add(element, Xpos, Ypos, Zpos, reference="entrance")
V.add(element, Xpos, Ypos, Zpos, roll, pitch, yaw, reference="entrance")
V.add(lattice, ...)   # same signatures
V.add(volume, ...)
V.add_ref(...)         # add by reference instead of copy
```
`Xpos,Ypos,Zpos` [m]; roll/pitch/yaw [rad]. Access by index/name as with Lattice
(`V{1}`/`V[0]`, `V{'NAME'}`/`V['NAME']`).

Track: `B1 = V.track(B0)` or `B1 = V.track(B0, options)` where `B0` is a Bunch6dT and
`options` is a `TrackingOptions` set (a `Volume` object *is itself* an instance of
`TrackingOptions`, so options are commonly set directly as `V.<option> = value`).
Tracking continues until the slowest particle leaves the Volume, or the tracking-time
limits below are hit.

Key TrackingOptions fields (settable directly on a `Volume` or `Lattice` element, or
passed as an options struct): `odeint_algorithm` (string, default `'rk2'`; others:
`'analytic'`, `'leapfrog'`, `'rk4'`, `'rkf45'`, `'rkck'`, `'k8pd'`, `'msadams'`),
`odeint_epsabs` (default 0.001), `odeint_epsrel` (default 0.0), `dt_mm` (integration
step, mm/c), `t_max_mm`/`t_min_mm` (tracking time bounds, default ±inf; `t_min_mm` used
for backtracking), `sc_dt_mm` (space-charge kick period), `cfx_dt_mm` (other collective
effects period), `tt_dt_mm` (transport-table sampling period), `tt_select`
(`'all'|'active'|'all_in_volume'|'active_in_volume'`, default `'all'`),
`emission_nsteps` (default 10), `emission_range` (default 2.0), `wp_dt_mm`/
`wp_basename`/`wp_gzip` (watch-point beam snapshots to disk), `verbosity` (0/1/2).

A `Volume` has two boundary planes `s0`/`s1` orthogonal to its local Z axis, defining
its longitudinal extent (auto-updated as elements are added, unless already fixed).
Set with `V.set_s0(z)` / `V.set_s0(P0, t)` / `V.set_s0(x, y, z, roll=0, pitch=0, yaw=0)`
(and matching `set_s1`), or relative to each other with `V.set_s0_from_s1(P0, l)` /
`V.set_s1_from_s0(P0, l)` (`l` a distance in m, `P0` a reference Bunch6dT particle).

### Volume as a Lattice element

Once a `Volume` has s0/s1 set, it can be appended into a `Lattice` like any element.
Bunch6d particles entering it are converted/distributed onto s0, tracked through the
Volume by time integration, and collected at s1 back into a Bunch6d for continued
Lattice tracking (e.g. sandwiching a field-map dipole Volume between two Lattices).
`V.set_tt_nsteps(N)` slices the transport table into N screens between s0 and s1, same
as any Lattice element.

## 4. Beamline element catalog

Methods available to **all** elements: `E.set_name(STRING)` / `E.get_name()`;
`E.set_aperture_x(Rx)` / `set_aperture_y(Ry)` / `set_aperture_shape(SHAPE)` /
`set_aperture(Rx,Ry,SHAPE)` (`Rx,Ry` [m]; `SHAPE` in `{'none','rectangular',
'circular'}`, circular becomes elliptical if Rx≠Ry, checked every integration step);
`E.set_static_Bfield(Bx,By,Bz)` [T] / `E.set_static_Efield(Ex,Ey,Ez)` [V/m] (embed the
element in a uniform field of arbitrary orientation); `E.add_collective_effect(CFX)`;
`E.get_field(x,y,z,t)` -> `[E,B]` (scalars or vectors for multiple points at once, E in
V/m, B in T — also works on compound elements Lattice/Volume); `E.set_tt_nsteps(N)`
(Lattice) — number of transport-table sampling points across the element.

### 4.1 Matrix-based elements (all symplectic by construction)

**Drift** — empty space. `D = Drift(L=0)` [m]. Plus the common set_static field methods
and `add_collective_effect` (e.g. simulate air/material region combined with
MultipleCoulombScattering).

**Quadrupole** — `Q = Quadrupole(L=0, strength=0)` or `Q = Quadrupole(L, P_Q, k1)`.
`L` [m]; `strength` = integrated focusing strength S [MV/c/m]; `P_Q` = beam magnetic
rigidity P/q [MV/c] (if `NaN`, RF-Track computes it at `autophase()` time — enables
thin-lens/normalized-strength definition independent of beam energy); `k1` focusing
strength [1/m²]. Relations: `S = (P/q)·k1·L`; `k1 = G/(Bρ)` (G = gradient [T/m]). If
`L=0`, `k1` is interpreted as the integrated strength `k1·L` [1/m] (thin quad).
Get: `get_K1(P_Q)`, `get_K1L(P_Q)`, `get_gradient()` [T/m], `get_strength()` [MV/c/m].
Set: `set_K1(P_Q,k1)`, `set_K1L(P_Q,k1L)`, `set_length(L)`, `set_gradient(G)`,
`set_strength(strength)`.

**SBend** (sector bend) — curved reference system; MAD-X sign convention (positive
angle = bend right, toward -x).
```
S = SBend(L, P_Q, angle, E1=0, E2=0)
S = SBend(L=0)
```
`L` [m], `angle` [rad], `P_Q` [MV/c], `E1,E2` entrance/exit pole-face angles [rad].
Get: `get_E1()/get_E2()` [rad], `get_E1d()/get_E2d()` [deg], `get_angle()` [rad],
`get_angled()` [deg], `get_h()` [1/m] curvature, `get_K0()` [1/m], `get_K1()` [1/m²],
`get_Bfield()` [T]. Set (in addition to obvious ones): `set_h(H)`, `set_hgap(HGAP)`
[m, half gap], `set_fint(FINT)` (fringe-field integral; default 0 = hard-edge;
precomputed values: linear drop-off 1/6, clamped Rogowski 0.4, unclamped Rogowski 0.7,
square-edged non-saturating 0.45), same definition as MAD-X FINT.

**RBend** (rectangular bend) — parallel entrance/exit faces; curved reference system
internally; length = straight-line distance entry-to-exit.
```
R = RBend(L, P_Q, angle, E1=0, E2=0)
```
Same args as SBend (internally an SBend with adjusted edge angles); same Get/Set API.

**Corrector** — magnetic steerer.
```
C = Corrector(L)
C = Corrector(L, Kx, Ky)
```
`L` [m]; `Kx,Ky` integrated H/V corrector strengths [T·mm].

### 4.2 Special elements (numerical integration in non-linear fields)

**Coil** — `C = Coil(L, B0, R)`. `L` element length [m], `B0` peak on-axis field [T],
`R` coil radius [m]. Placed at the middle of `L`. In `Volume`, field permeates the
whole 3D space; in `Lattice`, field exists only within the element's length.

**Solenoid** — inserted into Lattice (treated as matrix-based) or Volume (analytic 3D
field with realistic fringe, permeates whole space, overlaps with other fields).
```
S = Solenoid(L=0, B0=0, R=0)
S = Solenoid(L, B0, Rmin, Rmax, nsheets)
```
`L` [m], `B0` peak on-axis field [T], `R`/aperture radius [m] (also sets aperture in
both environments); `Rmin,Rmax` [m], `nsheets` [integer] current sheets.

**Undulator** — planar undulator; analytic 3D field + numerical integration in Lattice
or Volume.
```
U = Undulator(lperiod, K, nperiods, kx2=0)
```
`lperiod` [m], `K` undulator parameter (x-direction) [-], `nperiods` [integer],
`kx2` pole-surface curvature [1/m²] (default 0; >0 poles bent inward, <0 outward).

**TransferLine** — transports a beam through an entire beamline using only pairs of
Twiss parameters (no per-element definition); transverse plane uses a Twiss-form
transfer matrix with phase advance μ (adjusted for chromaticity if given);
longitudinal plane applies a drift of length `L = L0(1+αc·δ)`. **Works in Lattice
only.** Three modes: (1) two Twiss sets -> single Twiss matrix; (2) a full Twiss
table/MAD-X Twiss file -> tracks through each consecutive pair; (3) a single Twiss set
-> matches any tracked bunch to that target.
```
T = TransferLine("twiss_file.dat", Pref)
T = TransferLine(twiss_matrix, Pref, DQx, DQy, momentum_compaction)
T = TransferLine(twiss_matrix, Pref)
```
`twiss_matrix`: 7-column `[S, βx, αx, μx, βy, αy, μy]` or 11-column adding
`[Dx, Dpx, Dy, Dpy]`; S/β/D in [m], μ in [2π] (turns), `Pref` [MeV/c], `DQx,DQy`
chromaticities [2π], `momentum_compaction` per MAD-X definition. Can be segmented into
steps and have collective effects applied like any Lattice element.

**TW_Structure** (travelling-wave) — analytic TM01n mode description of a metallic
travelling-wave structure via Fourier-series field expansion.
```
T = TW_Structure([an, ...], n, freq, ph_advance, number_of_cells)
T = TW_Structure()
```
`[an,...]` Fourier coefficients [V/m]; `n` index of first coefficient [integer];
`freq` [Hz]; `ph_advance` phase advance per cell [rad]; `number_of_cells` [real]
(positive = structure starts mid-cell; negative = starts at cell beginning).

**SW_Structure** (standing-wave) — connects a beam pipe to a TW structure (input/output
couplers), TM01p Fourier expansion.
```
S = SW_Structure([a1,...], frequency, cell_length, number_of_cells)
S = SW_Structure()
```
`[a1,...]` [V/m], `frequency` [Hz], `cell_length` [m], `number_of_cells` [real]
(positive = starts at cell start; negative = starts at cell centre). A full realistic
structure is built by concatenating a half-SW input coupler + TW body + half-SW output
coupler as three `Lattice.append()`s (see worked example in section 11 below); use
`set_t0(0.0)` and `set_phid(phase_deg)` on each sub-element.

**Pillbox_Cavity** — standing-wave pillbox, TM01p modes, flat ends at z=0 and z=L.
```
S = Pillbox_Cavity([a0,...,ap], frequency, cell_length, n_cells)
S = Pillbox_Cavity()
```
`[a0..ap]` Fourier coefficients [V/m]; `frequency` [Hz]; `cell_length` [m]; `n_cells`
[real].

**Multipole** — normal/skew coefficient definitions identical to MAD-X; numerical
integration.
```
M = Multipole(L, P_Q, [K0L K1L K2L ...])
M = Multipole(L, [S0 S1 S2 ...])
M = Multipole(L=0)
```
`L` [m]; `P_Q` beam rigidity P/q [MV/c]; `S0,S1,...,Sn` (complex) multipole strengths
[MV/c/m^n]; `K0L,K1L,...,KnL` (complex) integrated multipole coefficients [1/m^n].
Complex numbers encode normal+skew: `B̃ = By + iBx`, `k̃n = k(normal) + i·k(skew)`.
Get: `get_Bn()` [T/m^n], `get_KnL(P_over_Q)` [1/m^n], `get_strengths()` [MV/c/m^n].
Set: `set_Bn([...])`, `set_KnL(P_over_Q,[...])`, `set_strengths([...])`,
`set_nsteps(N)` (default 10), `set_odeint_algorithm(name)`.

**Absorber** — block of matter applying MultipleCoulombScattering, EnergyStraggling,
StoppingPower simultaneously (see Collective Effects chapter for the physics).
```
A = Absorber(L, material_name)
A = Absorber(L, X0, Z, A, density, I=-1)
```
`L` [m]; `material_name` in `{'air','water','beryllium','lithium',
'liquid_hydrogen'}`; `X0` radiation length [cm]; `Z` atomic number [int]; `A` atomic
mass [g/mol]; `density` [g/cm³]; `I` mean excitation energy [eV] (empirical if -1).
Enable/disable methods: `enable_/disable_log_term()`, `_fruehwirth_model()` (default
on), `_wentzel_model()` (default on), `_stopping_power()` (default on),
`_energy_straggling()` (default on), `_multiple_coulomb_scattering()` (default on).

**ElectronCooler** — hybrid kinetic model: beam macro-particles interact with a cold,
magnetized electron plasma modeled on 3D meshes.
```
EC = ElectronCooler(L, rx, ry, density, Vz)
EC.set_temperature(Tr, Tl)
EC.set_electron_mesh(Nx, Ny, Nz, density, Vx, Vy, Vz)      # uniform plasma
EC.set_electron_mesh(Nz, DENSITY2D, VX2D, VY2D, VZ2D)       # 2D profile
EC.set_electron_mesh(DENSITY3D, VX3D, VY3D, VZ3D)           # full 3D mesh
EC.set_static_Bfield(Bx, By, Bz)
EC.set_Q(Q=-1)
EC.set_mass(mass=electronmass)
```
`L` [m], `rx,ry` plasma radius [m], `Tr,Tl` radial/longitudinal temperature [eV],
`density` [m⁻³], `Bx,By,Bz` [T], `Vx,Vy,Vz`/`VX*D,VY*D,VZ*D` plasma velocity [c].

**AdiabaticMatchingDevice** (AMD / "Flux Concentrator") — strong tapered solenoid used
in positron sources to capture positrons right after creation; analytic 3D field,
on-axis `Bz(z) = B0/(1+αz)`.
```
AMD = AdiabaticMatchingDevice(L, B0, ALPHA)
```
`L` [m], `B0` peak on-axis field [T], `ALPHA` [m⁻¹]. Aperture is a truncated cone:
`A.set_entrance_aperture(R1)`, `A.set_exit_aperture(R2)` [m].

**SpaceCharge_Field** — exposes the E/B field generated by an arbitrary particle
distribution at any point via `get_field()`; usable for weak-strong interactions in
Volume only (creates a field permeating all space).
```
SC = SpaceCharge_Field(B0T, Nx, Ny, Nz, Vz_slices=1)
```
`B0T` a Bunch6dT [distribution]; `Nx,Ny,Nz` 3D PIC mesh points [int]; `Vz_slices`
relativistic velocity slices [int]. Field computed via 3D PIC/FFT retarded Green's
functions inside the bounding box, and a 5th-order Cartesian multipole expansion
outside it.

**TW_Field** — inserts a travelling-wave structure directly from shunt impedance,
group velocity and quality factor (no explicit field maps needed).
```
TW = TW_Field(P_in, r_Q, Q, VG, freq, ph_adv, n_cells, z0_L=0)          # constant power
TW = TW_Field(P_in, dt, t_inj, r_Q, Q, VG, freq, ph_adv, n_cells)       # dynamic power
```
`P_in` input power [W] (scalar = infinitely long fill pulse, steady state after
filling; or a 1D time-array with time step `dt` [mm/c] and injection time `t_inj`
[mm/c]); `Q` quality factor array; `r_Q` shunt impedance per length array [Ω/m]; `VG`
group-velocity array [c]; `ph_adv` [rad]; `n_cells` [int]; `z0_L` input/output coupler
length as a fraction of cell length (0 = auto-add a standing-wave coupler of length
`z0_L·Lcell` before/after the TW body). `Q, r_Q, VG` arrays must have matching length.

**LaserBeam** — simulates inverse Compton scattering (ICS) between a charged particle
and a laser beam, in Lattice (see manual chapter 5/6 on Collective Effects / ICS for
detail — not elaborated further here).

**Volume as a Lattice element** — see section 3 above.

### 4.3 Diagnostics elements

**Bpm** (beam position monitor, Lattice only):
```
B = Bpm(L, resolution)
```
`L` [m] (reading occurs mid-element); `resolution` [mm]. `[X,Y] = B.get_reading()` [mm]
(repeated reads differ due to resolution noise); `get_resolution()`/`set_resolution()`;
`set_scaling_factor(X_scaling, Y_scaling=X_scaling)`. `Lattice.get_bpm_readings()`
retrieves all BPM readings at once after tracking.

**Screen** (Lattice or Volume) — thin element capturing a phase-space snapshot when a
Beam/Bunch6d(T) traverses it.
```
S = Screen()
S.set_width(W)          # mm, hit if |x| <= W/2
S.set_height(H)         # mm, hit if |y| <= H/2
S.set_time_window(T)    # mm/c, stored if |t - t0| <= T/2
S.set_t0(t0) / S.unset_t0()
```
Default: infinite extension, unbounded time window; auto-synced to the first bunch
traversing it unless `t0` set manually. Get: `S.get_bunch()` -> Bunch6d,
`S.get_beam()` -> Beam, `S.get_t0()`. After tracking, retrieve one Bunch6d/Beam per
screen via `Lattice`/`Volume` methods `get_bunch_at_screens()` /
`get_beam_at_screens()`.

## 5. Field maps

RF-Track accepts real or complex 1D/2D/3D field maps on regular Cartesian meshes, for
static fields, forward/backward travelling fields, or standing-wave RF fields.
1D/2D maps assume cylindrical symmetry around the structure axis and RF-Track
reconstructs off-axis components from Maxwell's equations; 3D maps are fully generic.

Interpolation: default **LINT** (linear, 8 nearest mesh points, fast) or **CINT**
(cubic, 64 nearest points / a 3x3x3 cube, smoother but slower) — selected via a
`_CINT` element-name suffix, e.g. `RF_FieldMap_1d_CINT`. Loss detection granularity =
1 mesh cell (LINT) or ~3 mesh cells (CINT). A `NaN` value anywhere in a 3D field map is
interpreted as a "wall" — a particle that hits a NaN is flagged lost, enabling precise
loss detection in complex 3D geometries.

**RF_FieldMap_1d** (and `_CINT` variant):
```
RF = RF_FieldMap_1d(Ez, hz, length, frequency, direction, P_max=1, P_actual=1)
```
`Ez` on-axis E-field [V/m] (complex = travelling, real = standing); `hz` mesh cell size
[m]; `length` element length (-1 = use map length) [m]; `frequency` [Hz] (0 = static);
`direction`: 0 static, +1 forward-travelling, -1 backward-travelling (standing waves
may use ±1 interchangeably). `P_max`(`P_map`) = input power the map was generated at
[W, default 1]; `P_actual` = actual operating power [W, default 1] — actual field is
scaled as `E_actual = E_map · sqrt(P_actual/P_map)`.

**RF_FieldMap_2d** (and `_CINT`):
```
RF = RF_FieldMap_2d(Er, Ez, Bt, Bz, hr, hz, length, frequency, direction, P_max=1, P_actual=1)
```
`Er,Ez` [V/m] or 0 if absent; `Bt,Bz` [T] or 0; each a 2D mesh indexed `[i,j]`
(i = longitudinal, j = radial); `hr,hz` mesh cell sizes [m].

**RF_FieldMap** (3D, and `_CINT`):
```
RF = RF_FieldMap(Ex,Ey,Ez, Bx,By,Bz, x0,y0, hx,hy,hz, length, frequency, direction, P_max=1, P_actual=1)
```
`Ex,Ey,Ez` [V/m] or 0; `Bx,By,Bz` [T] or 0; 3D meshes indexed `[i,j,k]` = x,y,z;
`x0,y0` bottom-left origin of the map in the x-y plane [m]; `hx,hy,hz` mesh cell sizes
[m]; other args as above.

Common RF field-map methods: `set_t0(T0)` [mm/c] / `unset_t0()` (reference time —
by default auto-set via `autophase()`); `set_phid(PHID)` [deg]; `set_P_actual(P)` [W];
`set_smooth(N)` (Gaussian-filter smoothing, N = kernel radius in mesh points).

**Static_Magnetic_FieldMap_1d** (and `_CINT`):
```
M = Static_Magnetic_FieldMap_1d(Bz, hz, length=-1)
```
`Bz` on-axis field [T]; `hz` mesh cell size [m]; `length` [m] (-1 = map length).

**Static_Magnetic_FieldMap_2d** (and `_CINT`):
```
S = Static_Magnetic_FieldMap_2d(Br, Bz, hr, hz, length=-1)
```
`Br,Bz` [T], 2D mesh `[i,j]` = longitudinal, radial; `hr,hz` [m].

**Static_Magnetic_FieldMap** (3D):
```
S = Static_Magnetic_FieldMap(Bx,By,Bz, x0,y0, hx,hy,hz, length)
S = Static_Magnetic_FieldMap(Ax,Ay,Az, PhiM, x0,y0, hx,hy,hz, length)   # via potentials
```
`Bx,By,Bz` [T]; or `Ax,Ay,Az` vector potential [T·m] + `PhiM` scalar potential [T·m];
`x0,y0` [m]; `hx,hy,hz` [m]; `length` [m].

## 6. Tracking API

- **Lattice**: `B1 = L.track(B0)` — single positional arg, `B0` a Bunch6d, returns the
  beam at the lattice exit.
- **Volume**: `B1 = V.track(B0)` or `B1 = V.track(B0, options)` — `B0` a Bunch6dT;
  tracking continues until the slowest particle leaves the region between planes
  `s0`/`s1`, or `t_max_mm`/`t_min_mm` is reached (see section 3 for TrackingOptions).
- **Beam (multi-bunch)**: `B1 = Line.track(B0)`, then index per-bunch results
  (`B1{1}`/`B1[0]`, ...).

**Particle losses**: `M = L.get_lost_particles()` / `M = V.get_lost_particles()` return
an 11-column matrix (positions/momenta/mass/charge/macro-charge/ID at the point/time of
loss, in the element's own reference frame). Lattice columns: `X[mm] XP[mrad] Y[mm]
YP[mrad] T[mm/c] P[MeV/c] S[mm] MASS[MeV/c²] Q[e] N ID`. Volume columns: `X[mm]
Px[MeV/c] Y[mm] Py[MeV/c] Z[mm] Pz[MeV/c] T[mm/c] MASS[MeV/c²] Q[e] N ID`.

**Autophasing** (`autophase()`, available on both Lattice and Volume) — propagates a
single reference particle (or the average particle of a full bunch) through the
structure, recording its arrival time at every time-dependent element (RF field maps,
TW/SW structures, Screens, LaserBeam) and synchronizing them automatically; for RF
elements it also sets the synchronous phase so that user phase `phid=0` (default)
means on-crest acceleration.
```
P0 = Bunch6d(electronmass, 100*pC, -1, [0 0 0 0 0 Pref])
Pfinal = L.autophase(P0)
```
Remarks: (1) must be called before any tracking — it is called **automatically** on the
first `track()` call if the user hasn't called it explicitly; (2) elements whose
`set_t0()` was called *before* being added to the Lattice/Volume are excluded from
autophasing and keep their manually set reference time.

Deferred/automatic magnet strength setting: define a magnet with `P_Q = NaN` and a
normalized strength (`k1` etc.); RF-Track computes the actual gradient during
`autophase()`, once the beam energy is known at that point in the lattice — useful when
building FODO cells interleaved with RF cavities where momentum varies along the linac.

**Backtracking** (`btrack()`, on both Lattice and Volume) — fully accounts for element
misalignments and deterministic collective effects (space charge, wakefields) but
excludes stochastic effects (multiple Coulomb scattering, quantum synchrotron
radiation).
```
B0 = L.btrack(B1)   # find B0 that evolves into the desired final B1
```

## 7. Twiss parameters API

Two dedicated structures gather the info needed to generate a matched beam from Twiss
parameters: `Bunch6d_twiss` (paired with Bunch6d) and `Bunch6dT_twiss` (paired with
Bunch6dT). Longitudinal phase space can be specified 3 alternative ways: (1)
`emitt_z` + Twiss `α_z`; (2) `emitt_z` + either `sigma_t`/`sigma_z` or `sigma_pt`/
`sigma_pz`; (3) both sigma_t/sigma_z and sigma_pt/sigma_pz directly.

`Bunch6d_twiss` fields: `emitt_x, emitt_y` [mm·mrad, normalized], `emitt_z`
[mm·permille], `sigma_t` [mm/c, rms bunch duration], `sigma_pt` [permille, energy
spread], `alpha_x, alpha_y, alpha_z`, `beta_x, beta_y, beta_z` [m], `disp_x, disp_y,
disp_z` [m], `disp_px, disp_py` [rad] (dispersion prime).

`Bunch6dT_twiss` is analogous with `sigma_z` [mm, rms bunch length] and `sigma_pz`
[permille, normalized long. momentum spread] replacing `sigma_t`/`sigma_pt`.

Creating a matched bunch:
```
Twiss = Bunch6d_twiss()
Twiss.beta_x = ...; Twiss.alpha_x = 0.0; Twiss.emitt_x = 1   # etc.
B0 = Bunch6d(mass, population, Q, Pref, Twiss, nParticles)
```

Retrieving statistical/Twiss quantities from an actual bunch (not the design values):
`I = B.get_info()` (`Bunch6d_info` or `Bunch6dT_info` depending on bunch type) exposes
`I.S`/`I.t` [m]/[mm/c], `I.mean_x, I.mean_y, ...` [mm], `I.mean_xp, I.mean_yp` [mrad],
`I.mean_Px/Py/Pz/P` [MeV/c], `I.mean_K, I.mean_E` [MeV], `I.sigma_x, I.sigma_y,
I.sigma_t` [mm]/[mm/c], `I.sigma_xp, I.sigma_yp` [mrad], `I.sigma_xpx, I.sigma_ypy`
[mm·mrad], `I.sigma_tpt` [mm/c·permille], `I.sigma_E` [MeV], `I.sigma_P` [MeV/c],
`I.emitt_x, I.emitt_y` [mm·mrad], `I.emitt_z` [mm·permille], `I.emitt_4d, I.emitt_6d`,
`I.alpha_x/y/z`, `I.beta_x/y/z` [m], `I.rmax` [mm, max transverse offset], `I.transmission`
(number of real particles remaining). Bunch6dT's `get_info()` uses X/Y/Z/Px/Py/Pz naming
instead but is otherwise analogous.

Along a Lattice/Volume, the transport table (section 8) exposes the running values of
essentially the same set (`%beta_x`, `%disp_x`, `%emitt_x`, `%sigma_x`, `%rmax`, etc.)
at every sampled point, not just at bunch endpoints.

## 8. Output/diagnostics

**Transport table** — both `Lattice` and `Volume` can accumulate average beam
quantities (size, emittance, energy spread, dispersion, Twiss, polarization, etc.)
during tracking. In `Lattice`, sampling density is set per-element via
`element.set_tt_nsteps(N)`; in `Volume`, via the `tt_dt_mm` tracking option (interval
in mm/c). Retrieve with `T = L.get_transport_table('%S %beta_x %beta_y ...')` (Lattice
identifiers, Table 4.1: `%S` [m], `%mean_x/y/t` [mm]/[mm/c], `%mean_xp/yp` [mrad],
`%mean_Px/Py/Pz/P` [MeV/c], `%mean_K/E` [MeV], `%emitt_x/y/4d/6d` [mm·mrad], `%emitt_z`
[mm·permille], `%disp_x/y/z` [m], `%disp_px/py` [rad], `%beta_x/y/z` [m], `%alpha_x/y/z`
[-], `%sigma_x/y` [mm], `%sigma_t` [mm/c], `%sigma_px/py` [mrad], `%sigma_pt`
[permille], `%sigma_P` [MeV/c], `%rmax`/`%rmax99.9`/`%rmax99`/`%rmax90` [mm], `%N`
transmission [#]). Volume identifiers (Table 4.2) are analogous but keyed on absolute
`%X/Y/Z` [mm] and `%t` [mm/c] rather than a curvilinear `%S`.

**BPM / Screen** — see section 4.3. `Lattice.get_bpm_readings()` for all BPMs at once;
`get_bunch_at_screens()` / `get_beam_at_screens()` for phase space at every `Screen`.

**Bunch persistency**:
```
B.save(filename)          # binary, bit-wise reload with B.load(filename); architecture-dependent
B.save_as_dst_file(filename, frequency_in_MHz)     # DST binary format, RF frequency required
B.save_as_sdds_file(filename, description)         # SDDS binary, description string optional
```
Alternatively extract the phase space via `get_phase_space()` and save it with plain
Octave/Python I/O (e.g. `save -text file.txt T0` in Octave).

## 9. MAD-X import

Covered fully in section 3 ("Importing a MAD-X lattice"): `Lattice("twiss_file.tws")`
converts an entire MAD-X-produced Twiss file (via `select, flag=twiss, full; twiss,
file=...;`) into a Lattice of corresponding elements. For non-periodic lines (transfer
lines), MAD-X's `twiss` command must be given explicit initial Twiss parameters
(`betx, alfx, bety, alfy`) since there is no periodic solution to fall back on.
Additionally, `TransferLine` (section 4.2) can directly load a MAD-X Twiss **file**
(not just a lattice) as `TransferLine("twiss_file.dat", Pref)`, tracking a bunch through
each consecutive pair of Twiss parameters via Twiss-matrix transport rather than
converting to individual elements — useful for representing sections of an external
line without re-deriving hardware from MAD-X element types. `Multipole` normal/skew
coefficient conventions and `SBend`'s `FINT`/sign convention explicitly follow MAD-X
definitions too, easing correspondence with MAD-X-derived lattices.

## 10. Units/conventions gotchas

- **Time is stored in mm/c, not seconds.** `t` (Bunch6d arrival time / Bunch6dT
  creation time / clock) and all "time step" tracking options (`dt_mm`, `t_max_mm`,
  `sc_dt_mm`, `tt_dt_mm`, etc.) are in mm/c. Use the predefined unit constants
  (`RF_Track.ps`, `.ns`, etc.) to convert from real time units, e.g.
  `dt = 5 * RF_Track.ps` -> mm/c.
- **Particle-level lengths/angles vs. element/machine-level lengths/angles use
  different units**: particle positions in **mm**, particle angles in **mrad**,
  but element lengths/offsets in **m** and element pitch/roll/yaw in **rad** (note:
  the random-scatter method `scatter_elements` uses **mrad** for its angle arguments,
  an exception worth double-checking against the specific method signature).
  `TransferLine`/Twiss-object betas/dispersions are in **m**, emittances in
  **mm·mrad** (normalized), energy/momentum spread quantities frequently in
  **permille**.
- **Momentum is always in MeV/c**, mass in MeV/c², energy in MeV — there is no
  separate "kinetic energy in GeV" convention; everything is MeV-based internally
  regardless of Octave/Python front end.
- **Charge sign convention**: `charge`/`Q` is in units of the elementary charge e,
  signed (e.g. electrons: `Q = -1`). Bending angle sign follows the MAD-X convention:
  a **positive** bend angle bends **to the right** (toward negative x).
- **Bunch6d vs Bunch6dT phase-space column order differs** and is easy to transpose by
  mistake: Bunch6d matrices use `[X XP Y YP T P ...]` (transverse coordinate + angle
  pairs, then time, then momentum), while Bunch6dT matrices use `[X Px Y Py Z Pz ...]`
  (transverse coordinate + momentum pairs, then longitudinal position and momentum) —
  Bunch6dT has no "angle" columns, only Cartesian momentum components.
- **Bunch6d -> Bunch6dT conversion is one-directional.** `Bunch6dT(B0)` works;
  the reverse has no defined operation because Bunch6dT does not keep all particles on
  a common longitudinal plane.
- **Python positional-only arguments**: RF-Track constructors/methods take strictly
  positional arguments — there are no Python keyword arguments, even though the manual
  sometimes writes `function(arg1=var1, arg2=var2)` purely to document meaning/defaults
  (this is illustrative notation only, not literal keyword-call syntax).
- **NumPy arrays required for vector/matrix inputs in Python.** Octave's native
  `[a, b, c]` row vectors must become explicit `numpy.array([...])` in Python, e.g.
  `Quad = rft.Multipole(length, np.array([0, k1L]))` (see verbatim example below).
  `numpy.inf` is the Python equivalent of Octave's `Inf` for unbounded tracking-time
  options.
- **Elements are added to Lattice/Volume by value (copied), not by reference**, unless
  `append_ref`/`add_ref`/`insert_ref` is used explicitly. Post-hoc edits to the
  original Python/Octave object will silently not propagate unless the `_ref` variant
  was used — a likely source of "my parameter change had no effect" bugs when writing
  a converter.
- **Quadrupole/Multipole `P_Q` = NaN convention**: leaving the reference rigidity as
  `NaN` at construction time (with normalized strength `k1`/`KnL` given instead of an
  absolute strength/gradient) defers gradient computation to `autophase()` time, once
  the local beam momentum is known — relevant if a converter needs to preserve
  MAD-X-style normalized `K1`/`K1L` definitions without knowing local energy up front.
- **`get_phase_space()` supports MAD-X/TRANSPORT/PLACET column-order conventions
  directly via format strings** (e.g. `"%x %px %y %py %Z %pt"` for MAD-X,
  `"%x %xp %y %yp %dt %d"` for TRANSPORT, `"%E %x %y %dt %xp %yp"` for PLACET) — useful
  for a converter that needs to hand off phase space in a specific external tool's
  native ordering.

## 11. Example workflows (verbatim, de-mangled)

### FODO cell: build, Twiss-match a bunch, track, retrieve/plot (Octave, from Ch.1)

```octave
%% Load RF-Track
RF_Track;

%% Beam parameters
mass = RF_Track.electronmass;  % particle mass in MeV/c^2
population = 1e10;             % number of particles per bunch
Q = -1;                        % particle charge in units of e
Pref = 5;                      % reference momentum in MeV/c
B_rho = Pref / Q;              % beam magnetic rigidity in MV/c

%% FODO cell parameters
Lcell = 2;                     % cell length in m
Lquad = 0.0;                   % m, zero-length quadrupole (thin quadrupole)
Ldrift = Lcell/2 - Lquad;      % drift space between the two quadrupoles

mu = 90;                                % phase advance per cell in deg
k1L = sind(mu/2) / (Lcell/4);           % 1/m, quadrupole focusing strength
strength = k1L * B_rho;                 % MeV/m, quadrupole strength

%% Create the elements
Qf = Quadrupole(Lquad/2, strength/2);   % half focusing quadrupole
Qd = Quadrupole(Lquad, -strength);      % defocusing quadrupole
Dr = Drift(Ldrift);                     % drift space
Dr.set_tt_nsteps(100);                  % number of steps for the transport table

%% Create the lattice
FODO = Lattice();          % Create a new object Lattice() called FODO
FODO.append(Qf);           % 1/2 F
FODO.append(Dr);           % O
FODO.append(Qd);           % D
FODO.append(Dr);           % O
FODO.append(Qf);           % 1/2 F

%% Define Twiss parameters
Twiss = Bunch6d_twiss();
Twiss.beta_x = Lcell * (1 + sind(mu/2)) / sind(mu);  % m
Twiss.beta_y = Lcell * (1 - sind(mu/2)) / sind(mu);  % m
Twiss.alpha_x = 0.0;
Twiss.alpha_y = 0.0;
Twiss.emitt_x = 1;   % mm.mrad, normalized emittances
Twiss.emitt_y = 1;   % mm.mrad

%% Create the bunch
B0 = Bunch6d(mass, population, Q, Pref, Twiss, 10000);

%% Perform tracking
B1 = FODO.track(B0);

%% Retrieve the Twiss plot and the phase space
T = FODO.get_transport_table('%S %beta_x %beta_y');
M = B1.get_phase_space('%x %xp %y %yp');

%% Make plots
figure(1)
hold on
plot(T(:,1), T(:,2), 'b-')
plot(T(:,1), T(:,3), 'r-')
legend({'\beta_x', '\beta_y'})
xlabel('S [m]')
ylabel('\beta [m]')

figure(2)
scatter(M(:,1), M(:,2), '*')
xlabel('x [mm]')
ylabel('x'' [mrad]')
```
The manual notes that a thin quadrupole is split in half (`Qf` appears at both ends of
the cell) to make the FODO cell symmetric; `Dr.set_tt_nsteps(100)` requests 100
transport-table sampling points across the drift purely for producing a smooth Twiss
plot (it doesn't affect the physical tracking result). Lattice elements are stored **by
value**: subsequent edits to `Qf`/`Qd`/`Dr` after `append()` do not affect `FODO`.

### Python vector-argument translation note (from Ch.1.5)

Octave:
```octave
Quad = Multipole(length, [0, k1L]);
Sext = Multipole(length, [0, 0, k2L]);
```
must be written in Python as:
```python
import RF_Track as rft
import numpy as np
Quad = rft.Multipole(length, np.array([0, k1L]))
Sext = rft.Multipole(length, np.array([0, 0, k2L]))
```

### Volume sandwiched inside a Lattice (dipole field map, from Ch.3.3.3)

```octave
% A reference particle placed in (0, 0, 0) with Pz = 100 MeV/c
P0 = Bunch6dT(mass, 0.0, +1, [0 0 0 0 0 100]);

% A Volume containing the field map in the figure
Dipole = Volume();
Dipole.dt_mm = 1.0;
Dipole.odeint_algorithm = 'rk2';
Dipole.add(DIPOLE_MAP, 0, 0, 0, 'center');
Dipole.set_s0(P0, -150);   % track backward P0 by 150 mm/c to set s0
Dipole.set_s1(P0, +150);   % track forward P0 by 150 mm/c to set s1
Dipole.set_tt_nsteps(20);

% A Lattice
L = Lattice();
L.append(Lattice1);
L.append(Dipole);
L.append(Lattice2);
```
When tracking through `L`, particles from `Lattice1` are distributed over the planes of
`Dipole`, tracked through the `Volume`, and collected at `s1` to form a `Bunch6d`
suitable for continuing through `Lattice2`.

### Bunch6d from an arbitrary user-defined distribution matrix (Ch.9.1.1)

```octave
% create a bunch of 1e12 100 MeV/c electrons, using 1000 macroparticles
P = 100;                 % MeV/c total momentum
O = zeros(1000,1);       % define a column vector of zeros
I = ones(1000,1);        % define a column vector of ones
X = randn(1000,1);       % mm, column vector of Gaussian-distributed positions
Y = randn(1000,1);       % mm, column vector of Gaussian-distributed positions
% create the beam matrix
M = [X O Y O O P*I];     % Bunch6d %x %xp %y %yp %t %P
% create a bunch
B0 = Bunch6d(RF_Track.electronmass, 1e12, -1, M);

% retrieve the phase space following the MAD-X convention
T0 = B0.get_phase_space("%x %px %y %py %Z %pt");
% retrieve the phase space following the TRANSPORT convention
T0 = B0.get_phase_space("%x %xp %y %yp %dt %d");
% retrieve the phase space following the PLACET convention
T0 = B0.get_phase_space("%E %x %y %dt %xp %yp");

% save on disk
B0.save('my_bunch.rft');                             % RF-Track binary format
B0.save_as_dst_file('my_bunch.dst', 750.0);           % DST, 750 MHz RF
B0.save_as_sdds_file('my_bunch.sdds', 'my useful comment');   % SDDS
% save as an Octave matrix
save -text my_bunch.txt T0;
```
