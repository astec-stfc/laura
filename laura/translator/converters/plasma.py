import os
from math import ceil
from typing import Any
from warnings import warn

import numpy as np
from scipy.constants import c

from laura.models.laser import LaserElement
from laura.models.plasma import PlasmaElement
from laura.models.simulation import PlasmaSimulationElement

from ..utils.hipace import laser_envelope, number, piecewise_linear, write_density_rz
from .base import BaseElementTranslator
from .laser import LaserTranslator

_HIPACE_ELEMENTS = {"electron": "electron", "positron": "positron", "hydrogen": "proton"}
"""LAURA plasma ``species`` against the HiPACE++ ``element`` of that particle."""

_HIPACE_MAX_STEP = 10**9
"""``max_step`` for an adaptive time step; HiPACE++ stops at ``max_time`` long before."""


class PlasmaTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Plasma` instance into a string or
    object that can be understood by various simulation codes.
    """

    plasma: PlasmaElement
    """Plasma element."""

    simulation: PlasmaSimulationElement
    """Plasma simulation element."""

    laser: LaserElement | None
    """Laser element."""

    def to_wake_t(self) -> Any:
        """
        Create a Wake-T plasma element object based on the attributes of this element.

        If a `laser` sub-element is defined, it is also converted to a Wake-T laser object and
        added to the plasma element; if two laser sub-elements are defined, they are summed together
        using the :class:`~wake_t.physics_models.laser.laser_pulse.SummedPulse` class.

        Returns
        -------
        wake_t.PlasmaStage
            Wake-T plasma element object

        Raises
        ------
        ValueError
            If the wakefield model is not supported; note that not all models are implemented yet
        """
        from wake_t.physics_models.laser.laser_pulse import (
            SummedPulse,
        )

        from ..conversion_rules.codes import wake_t_conversion

        type_conversion_rules_wake_t = wake_t_conversion.wake_t_conversion_rules
        if self.simulation.wakefield_model is None and self.verbose:
            warn(
                "No wakefield model defined; no plasma wakefields will be computed."
                f"Supported models are {list(self.simulation.required_attrs.keys())[1:]}."
            )
        elif (
            self.simulation.wakefield_model not in self.simulation.required_attrs.keys()
        ):
            raise ValueError(
                f"Invalid wakefield model {self.simulation.wakefield_model}. "
                f"Supported models are {list(self.simulation.required_attrs.keys())[1:]}."
            )
        commondict = {
            self._convert_keyword_wake_t(param): getattr(self, param)
            for param in self.simulation.required_attrs["common"]
        }
        modeldict = {
            self._convert_keyword_wake_t(param): getattr(self, param)
            for param in self.simulation.required_attrs.get(
                self.simulation.wakefield_model, []
            )
        }
        elemdict = modeldict | commondict | {"density": self._wake_t_density()}
        if self.plasma.ionizable:
            warn(
                f"{self.name} has an ionizable species, which Wake-T does not model; "
                "it is tracked as the pre-ionized plasma alone, with no ionization "
                "injection. Use a PIC code such as FBPIC for that."
            )
        if self.laser is not None and self.driver_laser is None:
            warn(
                f"The laser of {self.name} is an injector, not a wake driver; Wake-T "
                "cannot model the ionization it is there for, so it is left out."
            )
        lasers = []
        if self.driver_laser is not None:
            laser_translator = LaserTranslator.model_validate(self.model_dump())
            lasers.append(laser_translator.to_wake_t())
        if len(lasers) == 1:
            elemdict.update({"laser": lasers[0]})
        elif len(lasers) == 2:
            elemdict.update({"laser": SummedPulse(lasers[0], lasers[1])})
        elif len(lasers) > 2:
            if self.verbose:
                warn(
                    "More than two laser sub-elements found; only the first two will be used."
                )
            elemdict.update({"laser": SummedPulse(lasers[0], lasers[1])})
        obj = type_conversion_rules_wake_t[self.hardware_type](
            wakefield_model=self.simulation.wakefield_model, **elemdict
        )
        return obj

    def to_hipace(self, include_ions: bool = False, directory: str | None = None) -> dict:
        """
        HiPACE++ input parameters this stage defines: box, grid, run length,
        plasma species and laser. The beam, diagnostics and numerics are left to
        the caller; render the result with
        :func:`~laura.translator.utils.hipace.hipace_inputs`.

        HiPACE++ solves for the fields from the charge density itself, so
        neutrality is explicit: the background electrons carry an immobile
        neutralising background unless ``include_ions`` makes the ions mobile,
        and ionizable atoms starting at level *k* come with *k* electrons each,
        mobile, in ``atom_electrons``. Freed electrons go to ``injected``.

        Parameters
        ----------
        include_ions : bool
            Model the background ions as mobile protons, as FBPIC's ``include_ions``
        directory : str or None
            Where to write the openPMD density files of a ``custom`` profile

        Returns
        -------
        dict
            ``{input key: value}``, in SI units

        Raises
        ------
        ValueError
            If the box or grid is unset, a ``custom`` profile has no ``directory``, a laser stage
            asks for an adaptive time step, or :func:`~_hipace_laser` refuses the laser
        """
        sim, plas, laser = self.simulation, self.plasma, self.laser
        params = self._hipace_box()

        names = []

        def add(name: str, **kwargs) -> None:
            names.append(name)
            params.update({f"{name}.{key}": value for key, value in kwargs.items()})

        if plas.species not in _HIPACE_ELEMENTS:
            raise ValueError(
                f"{self.name}: plasma species {plas.species!r} has no HiPACE++ "
                f"element; use one of {list(_HIPACE_ELEMENTS)}."
            )
        ppc = [sim.particles_per_radial_cell] * 2
        column = {"ppc": ppc}
        if sim.r_max_plasma is not None:
            column["radius"] = sim.r_max_plasma
        if sim.p_rmin:
            column["hollow_core_radius"] = sim.p_rmin
        if plas.temperature:
            column["temperature_in_ev"] = plas.temperature
        background = column | {
            "element": _HIPACE_ELEMENTS[plas.species],
            **self._hipace_density(plas.density, directory, "electrons"),
        }
        if include_ions:
            if plas.species != "electron":
                raise ValueError(f"{self.name}: include_ions needs an electron plasma.")
            add("electrons", **background, neutralize_background=0)
            add("ions", **background | {"element": "proton"}, neutralize_background=0)
        else:
            add("electrons", **background)

        if plas.ionizable:
            if not plas.ionization_element:
                raise ValueError(
                    f"{self.name} sets ionizable but no ionization_element. Give "
                    "the atomic symbol of the gas to ionize, e.g. 'N' or 'He'."
                )
            if plas.ionization_max_level is not None and self.verbose:
                warn(f"{self.name}: HiPACE++ has no maximum ionization level; it is ignored.")
            n_atoms = float(plas.ionization_density or plas.density)
            level = plas.ionization_initial_level or 0
            gas = column | {"radius": sim.p_rmax_ionizable}
            add(
                "atoms",
                **gas,
                element=plas.ionization_element,
                **self._hipace_density(n_atoms, directory, "atoms"),
                initial_ion_level=level,
                can_field_ionize=1,
                can_laser_ionize=int(laser is not None),
                ionization_product="injected",
            )
            if level:
                add(
                    "atom_electrons",
                    **gas,
                    element="electron",
                    **self._hipace_density(level * n_atoms, directory, "atom_electrons"),
                    neutralize_background=0,
                )
            add("injected", element="electron", ppc=[0, 0], neutralize_background=0,
                **{"density(x,y,z)": 0})
        params["plasmas.names"] = names

        if laser is not None:
            params |= self._hipace_laser()
        return params

    def _hipace_laser(self) -> dict:
        """
        HiPACE++ laser parameters, as FBPIC would launch the pulse: a Gaussian
        through HiPACE++'s own profile, the others as parser expressions.
        ``focal_position`` is box z at t = 0 (FBPIC's lab ``zf``).
        HiPACE++ keeps the peak of a chirped Gaussian pulse at ``a0``.
        CEP is dropped: HiPACE++'s Gaussian scales the amplitude by ``exp(CEP)``.

        Returns
        -------
        dict
            ``{input key: value}``

        Raises
        ------
        ValueError
            For a counter-propagating laser, a ``file`` profile, or without
            wavelength, waist and pulse_duration_fwhm
        """
        sim, laser = self.simulation, self.laser
        profile = str(laser.profile_type).lower()
        if (
            profile == "file"
            or laser.propagation_direction != 1
            or str(laser.polarization) not in ("linear", "circular")
            or not (laser.wavelength and laser.waist and laser.pulse_duration_fwhm)
        ):
            raise ValueError(
                f"{self.name}: HiPACE++ export handles a co-propagating, linear or "
                "circular laser of an analytic profile, with wavelength, waist and "
                "pulse_duration_fwhm set."
            )
        if self.verbose:
            for attr, why in (
                ("polarization_angle", "an envelope laser has no polarization angle"),
                ("cep_phase", "an envelope laser has no carrier phase"),
            ):
                if getattr(laser, attr):
                    warn(f"{self.name}: {why}; {attr} is ignored.")
            if sim.laser_envelope_n_longitudinal:
                warn(
                    f"{self.name}: HiPACE++ runs the laser on the wakefield's longitudinal "
                    "grid; laser_envelope_n_longitudinal is ignored."
                )
        tau = laser.pulse_duration_1e_field  # HiPACE++'s and FBPIC's tau: exp(-(z/c tau)^2)
        phi2 = laser.temporal_chirp_2nd_order or 0.0
        params = {
            "lasers.names": ["laser"],
            "lasers.lambda0": laser.wavelength,
            "lasers.polarization": str(laser.polarization),
            "lasers.solver_type": "multigrid" if sim.laser_evolution else "off",
            "lasers.use_phase": int(sim.laser_envelope_use_phase),
        }
        if profile == "gaussian":
            params |= {
                "laser.init_type": "gaussian",
                "laser.a0": laser.amplitude * (1 + (2 * phi2 / tau**2) ** 2) ** -0.25,
                "laser.w0": laser.waist,
                "laser.tau": tau,
                "laser.position_mean": [0.0, 0.0, laser.initial_position],
                "laser.focal_distance": laser.focal_position,
                "laser.phi2": phi2,
            }
        else:
            real, imag = laser_envelope(
                profile, laser.amplitude, laser.wavelength, laser.waist, tau,
                laser.initial_position, laser.focal_position, phi2,
                p=laser.laguerre_polynomial_order_p, m=laser.laguerre_polynomial_order_m,
                flatness=laser.flatness,
            )
            params |= {
                "laser.init_type": "parser",
                "laser.laser_real(x,y,z)": real,
                "laser.laser_imag(x,y,z)": imag,
            }
        if sim.laser_envelope_n_radial:
            params["lasers.n_cell"] = [2 * sim.laser_envelope_n_radial] * 2
        return params

    def _hipace_box(self) -> dict:
        """HiPACE++ box, grid, run length, time step and dump period of this stage."""
        sim = self.simulation
        zmin, zmax = sim.min_longitudinal_position, sim.max_longitudinal_position
        if not (sim.r_max > 0 and sim.n_radial > 0 and sim.n_longitudinal > 0 and zmax > zmin):
            raise ValueError(
                f"{self.name}: HiPACE++ needs r_max, n_radial and n_longitudinal set, "
                "and max_longitudinal_position above min_longitudinal_position."
            )
        max_time = self.length / c
        # Cartesian box over the cylindrical one, at the same cell size.
        params = {
            "amr.n_cell": [2 * sim.n_radial, 2 * sim.n_radial, sim.n_longitudinal],
            "geometry.prob_lo": [-sim.r_max, -sim.r_max, zmin],
            "geometry.prob_hi": [sim.r_max, sim.r_max, zmax],
            "hipace.max_time": max_time,
        }
        if str(sim.dt_bunch).lower() == "auto":
            if self.laser is not None:
                raise ValueError(
                    f"{self.name}: HiPACE++ cannot take an adaptive time step with a "
                    "laser; set simulation.dt_bunch to a number of seconds."
                )
            params["hipace.dt"] = "adaptive"
            params["max_step"] = _HIPACE_MAX_STEP
            if sim.n_out > 1 and self.verbose:
                warn(
                    f"{self.name}: with an adaptive time step HiPACE++ cannot space "
                    f"n_out = {sim.n_out} dumps; only the first and last are written."
                )
        else:
            params["hipace.dt"] = float(sim.dt_bunch)
            params["max_step"] = max(1, ceil(max_time / float(sim.dt_bunch)))
        params["diagnostic.output_period"] = max(1, params["max_step"] // max(sim.n_out, 1))
        return params

    def _hipace_density(self, density: float, directory: str | None, species: str) -> dict:
        """
        HiPACE++ density of one species: this plasma scaled to ``density``.
        HiPACE++'s ``z`` is ``c*t`` from the stage entrance -- the axis
        :func:`~PlasmaElement.relative_density_profile` is measured on.
        A ``custom`` profile is Python, so it is sampled onto an (r, z) grid
        and written to ``<directory>/<name>_<species>_density.h5``.

        Parameters
        ----------
        density : float
            Nominal density [m^-3]
        directory : str or None
            Where a ``custom`` profile's file goes
        species : str
            HiPACE++ species name, for the file name

        Returns
        -------
        dict
            ``{"density(x,y,z)": parser expression}``, or
            ``{"read_density_from_path": file}`` for a ``custom`` profile

        Raises
        ------
        ValueError
            For a ``custom`` profile with no ``directory``, or a profile
            :func:`~PlasmaElement.relative_density_profile` rejects
        """
        plas = self.plasma
        kind = str(plas.density_profile_type).lower()
        if plas.density_profile and kind == "custom":
            if directory is None:
                raise ValueError(
                    f"{self.name}: a custom density profile goes to HiPACE++ as an "
                    "openPMD file; pass the directory to write it in."
                )
            sim = self.simulation
            dr = sim.r_max / sim.n_radial
            # Two cells either side: HiPACE++ interpolates with quadratic splines.
            r = dr * np.arange(-2, ceil(np.sqrt(2) * sim.n_radial) + 3)
            # 1001 samples along the stage; a sharper profile needs more.
            z = np.linspace(0.0, self.length, 1001)
            zz, rr = np.meshgrid(z, np.abs(r), indexing="ij")
            values = np.broadcast_to(plas.relative_density_profile(zz, rr), zz.shape)
            # Absolute, as HiPACE++ may run elsewhere than the caller's working directory.
            path = os.path.abspath(os.path.join(directory, f"{self.name}_{species}_density.h5"))
            write_density_rz(path, z, r, density * values)
            return {"read_density_from_path": path}
        plas.relative_density_profile(0.0)  # validates ramps and tables as for every code
        start = plas.density_profile_start
        dz = f"(z-{number(start)})" if start >= 0 else f"(z+{number(-start)})"
        up = plas.ramp_up
        top = up + plas.plateau
        end = top + plas.ramp_down
        terms = [number(density)]
        if not plas.density_profile:
            pass
        elif kind == "linear":
            terms.append(piecewise_linear(dz, [0.0, up, top, end], [0.0, 1.0, 1.0, 0.0]))
        elif kind == "tabulated":
            order = np.argsort(plas.density_profile_positions)
            terms.append(
                piecewise_linear(
                    dz,
                    np.asarray(plas.density_profile_positions)[order],
                    np.asarray(plas.density_profile_values)[order],
                )
            )
        else:  # decaying, as PlasmaElement._decaying_ramp_profile
            # No "<=": ParmParse reads any "=" as the start of a new definition.
            decay = number(plas.ramp_decay_length)
            terms.append(
                f"if({dz}<{number(up)},1/(1+({number(up)}-{dz})/{decay})^2,"
                f"if({number(top)}<{dz},"
                f"if({number(end)}<{dz},1e-06,1/(1+({dz}-{number(top)})/{decay})^2),1))"
            )
        if plas.parabolic_coefficient:
            terms.append(f"(1+{number(plas.parabolic_coefficient)}*(x^2+y^2))")
        return {"density(x,y,z)": "*".join(terms)}

    @property
    def driver_laser(self) -> LaserElement | None:
        """
        The laser driving the wake, or None for a beam-driven stage -- which
        includes one whose only laser is an injector (``role: injector``).
        """
        if isinstance(self.laser, LaserElement) and str(self.laser.role) == "driver":
            return self.laser
        return None

    def _wake_t_density(self) -> float | Any:
        """
        The plasma density in the form Wake-T takes it: a number for a uniform
        plasma, otherwise :func:`~_wake_t_density_profile`, which carries the
        longitudinal profile and any parabolic channel together.

        Returns
        -------
        float or Callable
            Density in m^-3, or a function ``f(z, r)`` returning it
        """
        if self.plasma.is_uniform:
            return float(self.plasma.density)
        return self._wake_t_density_profile

    def _wake_t_density_profile(self, z, r=0.0) -> np.ndarray:
        """
        :func:`~_density_profile`, floored just above zero for Wake-T.

        Wake-T normalises its grid by the local plasma skin depth, which is
        infinite where the density is exactly zero. The floor is the same
        1e-6 of nominal density that the ``decaying`` profile already
        returns past its down-ramp.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Density in m^-3, never less than 1e-6 of :attr:`~plasma.density`
        """
        return np.maximum(
            self._density_profile(z, r), 1e-6 * float(self.plasma.density)
        )

    def laser_to_fbpic(self) -> Any | None:
        """
        Create the FBPIC laser profile for the laser attached to this plasma stage
        via `fbpic.lpa_utils.laser.add_laser_pulse`.

        Returns
        -------
        fbpic.lpa_utils.laser.laser_profiles.LaserProfile or None
            The laser profile, or None if no laser is attached to this stage.
        """
        if not isinstance(self.laser, LaserElement):
            return None
        data = self.model_dump()
        data["hardware_type"] = "Laser"
        data["hardware_class"] = "Laser"
        return LaserTranslator.model_validate(data).to_fbpic()

    def _density_profile(self, z, r=0.0) -> np.ndarray:
        """
        Absolute plasma density as a function of position, in m^-3.

        This is the form Wake-T expects. PIC codes such as FBPIC instead want the
        density *relative* to the nominal density; use
        :func:`~_relative_density_profile` for those.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position along the plasma element in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Density in m^-3
        """
        return self.plasma._density_profile(z, r)

    def _relative_density_profile(self, z, r=0.0) -> np.ndarray:
        """
        Plasma density profile relative to :attr:`~plasma.density`.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position along the plasma element in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Relative density
        """
        return self.plasma.relative_density_profile(z, r)


class PlasmaLensTranslator(PlasmaTranslator):
    """
    Translator for a :class:`~laura.models.element.PlasmaLens` (active plasma lens).

    Wake-T and HiPACE++ model the lens directly. Codes without an equivalent element
    see it as a drift of the same length, with a warning.
    """

    focusing_strength: float = 0.0
    """Focusing gradient [T/m]."""

    wakefields: bool = False
    """Whether the beam-driven plasma wakefields in the lens are modelled."""

    laser: LaserElement | None = None
    """Unused; a plasma lens has no laser driver."""

    def to_hipace(self, include_ions: bool = False, directory: str | None = None) -> dict:
        """
        The lens as a HiPACE++ run: the field ``B = g (y, -x, 0)`` of
        :attr:`~focusing_strength` *g* on every beam -- positive focuses
        electrons -- over the box and run length of a plasma stage.
        The run is the lens, so the field needs no limits. The plasma is
        included only with :attr:`~wakefields`.

        Parameters
        ----------
        include_ions, directory
            As :func:`~PlasmaTranslator.to_hipace`, with :attr:`~wakefields`

        Returns
        -------
        dict
            ``{input key: value}``, in SI units

        Raises
        ------
        ValueError
            Without :attr:`~wakefields` and with an adaptive time step, which
            HiPACE++ takes from the plasma density
        """
        if self.wakefields:
            params = super().to_hipace(include_ions=include_ions, directory=directory)
        else:
            params = self._hipace_box() | {"plasmas.names": "no_plasma"}
            if params["hipace.dt"] == "adaptive":
                raise ValueError(
                    f"{self.name}: HiPACE++ times an adaptive step by the plasma, and a lens "
                    "without wakefields has none; set simulation.dt_bunch to a number of seconds."
                )
        g = self.focusing_strength
        params["beams.external_B(x,y,z,t)"] = [f"{number(g)}*y", f"{number(-g)}*x", 0.0]
        return params

    def to_wake_t(self) -> Any:
        """
        Create a Wake-T ``ActivePlasmaLens``.

        With :attr:`~wakefields` set, the plasma density and the grid
        settings of the ``simulation`` sub-element are passed on, as for a
        :class:`~PlasmaTranslator` stage.

        Returns
        -------
        wake_t.ActivePlasmaLens
            Wake-T plasma-lens object
        """
        from ..conversion_rules.codes import wake_t_conversion

        kwargs = {
            self._convert_keyword_wake_t(param): getattr(self, param)
            for param in self.simulation.required_attrs["common"]
        }
        if self.wakefields:
            model = self.simulation.wakefield_model or "quasistatic_2d"
            kwargs.update(
                {
                    self._convert_keyword_wake_t(param): getattr(self, param)
                    for param in self.simulation.required_attrs.get(model, [])
                    if not param.startswith("laser_")
                }
            )
            kwargs.update(wakefield_model=model, density=self._wake_t_density())
        return wake_t_conversion.wake_t_conversion_rules["PlasmaLens"](
            foc_strength=self.focusing_strength,
            wakefields=self.wakefields,
            **kwargs,
        )
