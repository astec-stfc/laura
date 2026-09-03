import os
from typing import Any, Dict
from warnings import warn

import numpy as np
from pydantic import Field, computed_field

from laura.models.baseModels import IgnoreExtra
from laura.models.element import PhysicalBaseElement
from laura.models.physical import PhysicalElement, Position  # noqa E402
from laura.utils import flatten_dict

from ..converters import (
    elements_Bmad,
    elements_Elegant,
    elements_Genesis,
    elements_Madx,
    elements_Opal,
    keyword_conversion_rules_bmad,
    keyword_conversion_rules_cheetah,
    keyword_conversion_rules_elegant,
    keyword_conversion_rules_genesis,
    keyword_conversion_rules_madx,
    keyword_conversion_rules_ocelot,
    keyword_conversion_rules_opal,
    keyword_conversion_rules_wake_t,
    keyword_conversion_rules_xsuite,
    type_conversion_rules,
    type_conversion_rules_Bmad,
    type_conversion_rules_Elegant,
    type_conversion_rules_Genesis,
    type_conversion_rules_Madx,
    type_conversion_rules_Opal,
)
from ..converters.codes.gpt import gpt_ccs
from ..utils.bmad import bmad_misalignment
from ..utils.fields import field
from ..utils.functions import checkValue, expand_substitution, sanitize_string

_ASTRA_ROTATION_SIGN = {"x": -1.0, "y": -1.0, "z": 1.0}
"""Sign taking a LAURA ``Rotation`` component into ASTRA's ``*_xrot`` family.

ASTRA names these for the plane and then spells out the axis -- "rotation
angle of the quadrupole in the x-z plane, i.e. around the y-axis" -- so the
pairing with LAURA's ``x_rot``/``y_rot``/``z_rot``, which name the plane too,
is name for name.  The signs are not: LAURA's ``Ry`` factor turns the
opposite way to an ordinary right-handed one, so the two transverse angles
are negated and the roll is not.

Measured against ASTRA itself rather than read off the manual, with a 0.5 m
k=2 quadrupole at 1 GeV and a 1 m drift after it: ``Q_xrot = +0.05`` puts the
beam at x = -0.4503 mm, ``Q_yrot = +0.05`` at y = +1.650 mm, and a
``Q_zrot = +0.3`` with the beam entering at x = +1 mm sends it to
y = -0.707 mm.  Bmad reproduces all three to within its differing fringe
model (-0.4464 mm, +1.7105 mm, -0.7071 mm), and Bmad's own pairing with
LAURA is fixed by the floor-angle matrix conversion in
:func:`~laura.translator.utils.bmad.angles.bmad_floor_angles_to_laura`.

This stays here rather than moving to ``utils/bmad`` with the rest: it is
the ASTRA convention, and the only reason it was ever written next to the
Bmad one is that the two were measured in the same sitting.
"""


class BaseElementTranslator(PhysicalBaseElement):
    """
    Translator class for converting a :class:`~laura.models.element.Element` instance into a string or
    object that can be understood by various simulation codes.
    """

    type_conversion_rules: Dict = {}
    """Conversion rules for keywords when exporting to different code formats."""

    conversion_rules: Dict = {}
    """Conversion rules for keywords when exporting to different code formats."""

    counter: int = Field(ge=1, default=1)
    """
    Counter to indicate the number of elements of this type in the lattice/section.
    #TODO was needed for ASTRA/CSRTrack; may be deprecated.
    """

    master_lattice: str | None = None
    """Location of the directory containing lattice/data/simulation files."""

    directory: str = "./"
    """Directory to which lattice/element files will be written."""

    ccs: gpt_ccs | None = None
    """Co-ordinate system for GPT elements."""

    def model_post_init(self, __context):
        self.type_conversion_rules = type_conversion_rules
        hardware_type = self.hardware_type.lower()
        rules_by_code = {
            "elegant": keyword_conversion_rules_elegant,
            "ocelot": keyword_conversion_rules_ocelot,
            "cheetah": keyword_conversion_rules_cheetah,
            "xsuite": keyword_conversion_rules_xsuite,
            "wake_t": keyword_conversion_rules_wake_t,
            "genesis": keyword_conversion_rules_genesis,
            "opal": keyword_conversion_rules_opal,
            "bmad": keyword_conversion_rules_bmad,
        }
        for code, rules in rules_by_code.items():
            self.conversion_rules[code] = (
                rules[hardware_type] | rules["general"]
                if hardware_type in rules
                else rules["general"]
            )
        self.conversion_rules["madx"] = keyword_conversion_rules_madx["general"]
        if self.hardware_type.lower() in keyword_conversion_rules_madx:
            self.conversion_rules["madx"] = (
                keyword_conversion_rules_madx[self.hardware_type.lower()]
                | keyword_conversion_rules_madx["general"]
            )
        self.ccs = gpt_ccs(name="wcs", position=[0, 0, 0], rotation=[0, 0, 0])
        super().model_post_init(__context)

    def full_dump(self, resolve: bool = True) -> Dict[str, Any]:
        """
        Dump the full lattice model as a single-layer dictionary. For attributes within nested models,
        keys will be separated by "_".

        Parameters
        ----------
        resolve: bool
            If True (default), any value that is a string naming a functional
            definition is resolved to its numeric value. Codes that natively
            support symbolic/functional parameters (e.g. Xsuite, ELEGANT) pass
            ``resolve=False`` to keep the symbolic name.

        Returns
        -------
        Dict[str, Any]
            A flattened dictionary containing the attributes of the element.
        """
        data = flatten_dict({**self.model_dump()}, parent_key="", separator="_")
        if resolve:
            defs = IgnoreExtra.functional_definitions
            data = {
                key: (defs[value] if self.is_functional(value) else value)
                for key, value in data.items()
            }
        return data

    @staticmethod
    def is_functional(value: Any) -> bool:
        """
        True if ``value`` is a string naming an entry in the lattice's functional
        definitions (i.e. it should be resolved to a number, or passed through
        symbolically to codes that support it).
        """
        return isinstance(value, str) and value in IgnoreExtra.functional_definitions

    @property
    def _resolve_functional(self) -> bool:
        """The global resolution mode. When True, functional attributes are
        baked in as resolved numbers even for codes that support symbolic
        parameters; when False (default) they are rendered symbolically."""
        return IgnoreExtra.resolve_functional

    def _raw_multipole_strength(self, order: int) -> str | None:
        """
        Return the stored multipole strength for a given order if it is defined
        symbolically (as a functional-parameter name), otherwise None. Used by
        codes that support functional parameters to emit the symbolic reference
        rather than the resolved number.
        """
        magnetic = getattr(self, "magnetic", None)
        multipoles = getattr(magnetic, "multipoles", None) if magnetic else None
        if multipoles is None:
            return None
        multipole = getattr(multipoles, f"K{order}L", None)
        if multipole is None:
            return None
        raw = multipole.skew if getattr(magnetic, "skew", False) else multipole.normal
        return raw if self.is_functional(raw) else None

    def _functional_strength_expr(self, order: int, code: str) -> str | None:
        """
        Build a code-specific expression for the *normalized* magnet strength
        ``k = KnL(order) / length`` when that strength is defined symbolically;
        return None otherwise.

        For zero-length magnets the normalized strength equals the integrated
        value (mirroring the numeric ``KnL / length`` fall-back).
        """
        raw = self._raw_multipole_strength(order)
        if raw is None:
            return None
        length = getattr(self.magnetic, "length", 0)
        if not length:
            return self._rpn(raw) if code == "elegant" else raw
        if code == "elegant":
            return self._rpn(raw, length, "/")
        return f"{raw} / {length}"

    def _raw_edge_angle(self, which: str, code: str) -> str | None:
        """
        Return a symbolic expression for a dipole edge angle (``which`` is
        ``"entrance_edge_angle"`` or ``"exit_edge_angle"``) if it should be
        carried through to the target code symbolically, otherwise None (in
        which case the caller should fall back to the resolved number, e.g.
        via :attr:`DipoleTranslator.e1 <laura.translator.converters.magnet.DipoleTranslator.e1>`).

        The stored value may be:

        * a plain number -- returns None (nothing symbolic to do).
        * an expression referencing the reserved ``angle`` token (e.g.
          ``"angle"``/``"angle/2"``).
        * the name of a functional definition -- returned as a bare reference
          (rpn-quoted for ELEGANT).
        """
        magnetic = getattr(self, "magnetic", None)
        value = getattr(magnetic, which, None) if magnetic else None
        if not isinstance(value, str):
            return None
        if "angle" in value:
            raw = self._raw_multipole_strength(0)
            if raw is None:
                return None
            if value == "angle":
                return self._rpn(raw) if code == "elegant" else raw
            if value == "angle/2":
                return self._rpn(raw, 2, "/") if code == "elegant" else f"{raw} / 2"
            return value.replace("angle", raw) if code != "elegant" else self._rpn(raw)
        if self.is_functional(value):
            return self._rpn(value) if code == "elegant" else value
        return None

    def _elegant_value(self, value: Any) -> Any:
        """
        Render a value for an ELEGANT keyword. A functional parameter is emitted
        as an rpn variable reference (the quoted name, resolved by the matching
        ``% <value> sto <name>`` line at the top of the file); anything else is
        returned unchanged.
        """
        if self.is_functional(value):
            return f'"{value}"'
        return value

    @staticmethod
    def _rpn(*tokens: Any) -> str:
        """
        Build a quoted ELEGANT rpn expression from ``tokens`` (operands and
        operators in postfix order), e.g. ``_rpn(90, "phi", "-")`` -> ``"90 phi -"``.
        """
        return '"' + " ".join(str(token) for token in tokens) + '"'

    def start_write(self) -> None:
        """
        Begin the element writing process; calls :func:`~update_field_definition`.
        """
        self.update_field_definition()

    def to_elegant(self) -> str:
        """
        Generates a string representation of the object's properties in the Elegant format.

        Returns
        -------
        str
            A formatted string representing the object's properties in Elegant format.
        """
        self.start_write()
        wholestring = ""
        etype = self._convertType_Elegant(self.hardware_type)
        if etype == "drift" and self.hardware_type != "Drift":
            warn(
                f"Elegant does not support {self.hardware_type!r}; "
                f"{self.name!r} was exported as a drift."
            )
        string = self.name + ": " + etype
        keys = []
        for key, value in self.full_dump(resolve=self._resolve_functional).items():
            if (
                not key == "name"
                and not key == "type"
                and not key == "commandtype"
                and self._convertKeyword_Elegant(key) in elements_Elegant[etype]
            ):
                if value is not None:
                    key = self._convertKeyword_Elegant(key)
                    if value in ("angle", "angle/2") and key in ("e1", "e2"):
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_edge_angle(
                                (
                                    "entrance_edge_angle"
                                    if key == "e1"
                                    else "exit_edge_angle"
                                ),
                                "elegant",
                            )
                        )
                        value = (
                            raw
                            if raw is not None
                            else (
                                self.magnetic.KnL(0)
                                if value == "angle"
                                else self.magnetic.KnL(0) / 2
                            )
                        )
                    elif value == "angle":
                        value = self.magnetic.KnL(0)
                    elif value == "angle/2":
                        value = self.magnetic.KnL(0) / 2
                    elif key in ["k1", "k2", "k3", "k4", "k5", "k6"]:
                        expr = (
                            None
                            if self._resolve_functional
                            else self._functional_strength_expr(int(key[1]), "elegant")
                        )
                        value = expr if expr is not None else getattr(self, f"{key}")
                    elif key == "angle":
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_multipole_strength(0)
                        )
                        if raw is not None:
                            value = raw
                    elif key == "yaw" and isinstance(value, (int, float)):
                        value = -value
                    value = 1 if value is True else value
                    value = 0 if value is False else value
                    if key not in keys:
                        value = self._elegant_value(value)
                        tmpstring = ", " + key + " = " + str(value)
                        if len(string + tmpstring) > 76:
                            wholestring += string + ",&\n"
                            string = ""
                            string += tmpstring[2::]
                        else:
                            string += tmpstring
                    keys.append(key)
        wholestring += string + ";\n"
        return wholestring

    def to_ocelot(self) -> object:
        """
        Generates an Ocelot object based on the element's properties and type.

        Returns
        -------
        object
            An Ocelot object representing the element, initialized with its properties.
        """
        from ocelot.cpbd.elements import Aperture, Marker

        from ..conversion_rules.codes import ocelot_conversion

        type_conversion_rules_Ocelot = ocelot_conversion.ocelot_conversion_rules
        self.start_write()
        obj = type_conversion_rules_Ocelot[self.hardware_type](eid=self.name)
        for key, value in self.full_dump().items():
            if (key not in ["name", "type", "commandtype"]) and (
                not type(obj) in [Aperture, Marker]
                and self._convertKeyword_Ocelot(key) in obj.__class__().element.__dict__
            ):
                if value is not None:
                    key = self._convertKeyword_Ocelot(key)
                    if value == "angle":
                        value = self.magnetic.KnL(0)
                    if key in ["k1", "k2", "k3", "k4", "k5", "k6"]:
                        value = getattr(self, f"{key}l") / self.magnetic.length
                    if key == "gap":
                        value = 2 * value
                    setattr(obj, self._convertKeyword_Ocelot(key), value)
                    if key == "fint" and hasattr(obj.element, "fintx"):
                        setattr(obj, "fintx", value)
        return obj

    @staticmethod
    def _cheetah_float64(obj: object) -> object:
        """
        Promotes every floating-point buffer on a Cheetah element to float64.
        """
        from torch import float64

        for bufname, buf in obj._buffers.items():
            if buf is not None and buf.is_floating_point() and buf.dtype != float64:
                obj._buffers[bufname] = buf.to(float64)
        return obj

    def to_cheetah(self) -> object:
        """
        Generates a Cheetah object based on the element's properties and type.

        Returns
        -------
        object
            A Cheetah object representing the element, initialized with its properties.
        """
        from cheetah.accelerator import Aperture as Aperture_Cheetah
        from cheetah.accelerator import Drift as Drift_Cheetah
        from cheetah.accelerator import Screen as Screen_Cheetah
        from torch import float64, tensor

        from ..conversion_rules.codes import cheetah_conversion

        type_conversion_rules_Cheetah = cheetah_conversion.cheetah_conversion_rules
        self.start_write()
        try:
            obj = type_conversion_rules_Cheetah[self.hardware_type](
                name=self.name,
                length=tensor(self.physical.length, dtype=float64),
                sanitize_name=True,
            )
        except Exception as e:
            if self.hardware_type in type_conversion_rules_Cheetah:
                if self.physical.length > 0:
                    obj = Drift_Cheetah(
                        name=self.name,
                        length=tensor(self.physical.length, dtype=float64),
                        sanitize_name=True,
                    )
                else:
                    obj = Screen_Cheetah(
                        name=self.name,
                        sanitize_name=True,
                    )
                    obj.is_active = True
                    return self._cheetah_float64(obj)
            else:
                raise NotImplementedError(
                    f"Cheetah element {self.hardware_type} not implemented, {e}"
                )
        buffers = obj.__class__(
            length=tensor(self.physical.length, dtype=float64)
        )._buffers
        for key, value in self.full_dump().items():
            if (key not in ["name", "type", "commandtype"]) and (
                not type(obj) in [Aperture_Cheetah]
                and self._convertKeyword_Cheetah(key) in buffers
            ):
                key = self._convertKeyword_Cheetah(key)
                if key == "gap":
                    value = 2 * value
                if isinstance(value, float):
                    dt = float64
                    setattr(
                        obj, self._convertKeyword_Cheetah(key), tensor(value, dtype=dt)
                    )
                elif isinstance(value, int):
                    from torch import int64

                    dt = int64
                    setattr(
                        obj, self._convertKeyword_Cheetah(key), tensor(value, dtype=dt)
                    )
                if key == "fringe_integral" and "fringe_integral_exit" in buffers:
                    setattr(obj, "fringe_integral_exit", tensor(value, dtype=float64))
                    # else:
                    #     from torch import get_default_dtype
                    #     dt = get_default_dtype()
        self._cheetah_float64(obj)
        if isinstance(obj, Screen_Cheetah):
            obj.is_active = True
        return obj

    def to_xsuite(self, beam_length: int) -> tuple:
        """
        Generates an Xsuite object based on the element's properties and type.

        Parameters
        ----------
        beam_length: int
            Number of macroparticles in the beam

        Returns
        -------
        tuple
            (objectname, Xsuite object, properties[dict])
        """
        from ..conversion_rules.codes import xsuite_conversion

        type_conversion_rules_Xsuite = xsuite_conversion.xsuite_conversion_rules
        self.start_write()
        if self.hardware_type in type_conversion_rules_Xsuite:
            obj = type_conversion_rules_Xsuite[self.hardware_type]
        else:
            warn(
                f"Could not find hardware type {self.hardware_type} in xsuite conversion rules "
                f"for element {self.name}; setting as drift"
            )
            obj = type_conversion_rules_Xsuite["Drift"]
        properties = {}
        from xtrack.monitors import ParticlesMonitor

        if obj == ParticlesMonitor:
            properties = {
                "num_particles": beam_length,
                "start_at_turn": 0,
                "stop_at_turn": 1,
                # "store_particles": True,
            }
            return self.name, obj, properties
        for key, value in self.full_dump(resolve=self._resolve_functional).items():
            if (key not in ["name", "type", "commandtype"]) and (
                self._convertKeyword_Xsuite(key) in list(obj.__dict__.keys())
            ):
                key = self._convertKeyword_Xsuite(key)
                if (
                    key in ["k1", "k2", "k3", "k4", "k5", "k6"]
                    and not self._resolve_functional
                ):
                    expr = self._functional_strength_expr(int(key[1]), "xsuite")
                    if expr is not None:
                        value = expr
                if key == "angle":
                    if self.length > 0:
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_multipole_strength(0)
                        )
                        if raw is not None:
                            properties.update({"k0": f"{raw} / {self.length}"})
                        else:
                            properties.update(
                                {"k0": self.magnetic.KnL(0) / self.length}
                            )
                if self.hardware_type.lower() == "dipole":
                    properties.update({"num_multipole_kicks": 10})
                if (
                    "edge" in key
                    and isinstance(value, str)
                    and not self.is_functional(value)
                ):
                    if value == "angle":
                        value = self.magnetic.KnL(0)
                    elif value == "angle/2":
                        value = self.magnetic.KnL(0) / 2
                properties.update({key: value})
        if self.hardware_type.lower() == "dipole":
            properties.update(
                {
                    "edge_entry_fint": self.magnetic.edge_field_integral,
                    "edge_exit_fint": self.magnetic.edge_field_integral,
                    "edge_entry_hgap": self.magnetic.half_gap,
                    "edge_exit_hgap": self.magnetic.half_gap,
                }
            )
        return self.name, obj, properties

    def to_genesis(self, index: int) -> str:
        """
        Generates a string representation of the object's properties in the Genesis format.

        Returns
        -------
        str
            A formatted string representing the object's properties in Elegant format.
        """
        self.start_write()
        wholestring = ""
        etype = self._convertType_Genesis(self.hardware_type)
        if "mark" in etype.lower():
            fld = ", dumpfield = 1" if "photon" in self.hardware_type.lower() else ""
            return f"{index}{self.name}: {etype} = " + "{dumpbeam = 1" + fld + "};\n"
        string = f"{index}{self.name}: {etype} = " + "{"
        keys = []
        for key, value in self.full_dump().items():
            if (
                not key == "name"
                and not key == "type"
                and not key == "commandtype"
                and self._convertKeyword_Genesis(key) in elements_Genesis[etype]
            ):
                if value is not None:
                    key = self._convertKeyword_Genesis(key)
                    if key in ["k1", "k2", "k3", "k4", "k5", "k6"]:
                        value = getattr(self, f"{key}l")
                    value = 1 if value is True else value
                    value = 0 if value is False else value
                    if key not in keys:
                        string += key + " = " + str(value) + ", "
                    keys.append(key)
        wholestring += string[:-2] + "};\n"
        return wholestring

    def to_csrtrack(self, n: int = 0, **kwargs) -> str:
        """
        Base function for writing to CSRTrack; this is empty since only certain elements are supported.

        #TODO add warnings
        """
        return ""

    def to_astra(self, n: int = 0, **kwargs: dict) -> str:
        """
        Base function for writing to ASTRA; this is empty since only certain elements are supported.

        #TODO add warnings
        """
        return ""

    def to_gpt(self, Brho: float = 0.0, *args, **kwargs) -> str:
        """
        Base function for writing to GPT; this is empty since only certain elements are supported.

        #TODO add warnings
        """
        return ""

    def to_rftrack(self, P_Q: float = float("nan")) -> object:
        """
        Generates an RF-Track element object based on the element's properties and type.

        Dispatches on ``hardware_type`` via
        :data:`~laura.translator.conversion_rules.codes.rftrack_conversion.rftrack_conversion_rules`,
        unlike ``to_ocelot``/``to_cheetah``/``to_xsuite`` this is a single generic
        implementation — no per-element-category override is needed because RF-Track
        builder functions receive the fully-typed translator instance (e.g. a
        ``DipoleTranslator`` has ``e1``/``e2`` available) directly.

        Parameters
        ----------
        P_Q: float
            Beam reference momentum-over-charge [MV/c] at this point in the
            lattice. Only used by dipole (``SBend``) conversion — RF-Track's
            ``SBend``, unlike ``Quadrupole``/``Multipole``, does not support
            deferring this to ``autophase()`` (verified: an unset/NaN value
            silently produces zero transmission). Mirrors how
            ``to_gpt(Brho=...)`` threads the equivalent rigidity value down
            from ``SectionLatticeTranslator.to_gpt(Brho=...)``.

        Returns
        -------
        object or list of object
            An RF-Track element object (e.g. ``RF_Track.Quadrupole``), with its
            name and aperture (if any) applied. A handful of builders (e.g.
            :func:`~laura.translator.conversion_rules.codes.rftrack_conversion.
            build_tw_fieldmap`) instead return a **list** of RF-Track objects
            meant to be flattened as siblings into the caller's own Lattice
            rather than wrapped in a nested sub-Lattice (see that function's
            docstring for why) -- name/aperture are applied to every item in
            that case, and :func:`~laura.translator.converters.section.
            SectionLatticeTranslator.to_rftrack` flattens the list when
            appending.
        """
        from ..conversion_rules.codes.rftrack_conversion import (
            build_drift,
            rftrack_conversion_rules,
        )

        self.start_write()
        builder = rftrack_conversion_rules.get(self.hardware_type, None)
        if builder is None:
            warn(
                f"Element type {self.hardware_type} of {self.name} not supported by "
                f"RF-Track; using a Drift"
            )
            builder = build_drift
        obj = builder(self, P_Q=P_Q)
        for o in obj if isinstance(obj, list) else [obj]:
            o.set_name(self.name)
            self._apply_rftrack_aperture(o)
        return obj

    def to_rftrack_repr(self, varname: str, P_Q: float = float("nan")) -> tuple:
        """
        Generates the Python source lines that (re)construct this element as a
        standalone ``RF_Track`` object, mirroring what :func:`to_rftrack`
        builds in memory. Used by ``SectionLatticeTranslator.to_rftrack(save=
        True)`` to export a self-contained lattice script (RF-Track has no
        built-in equivalent of Ocelot's ``MagneticLattice.save_as_py_file()``).

        Parameters
        ----------
        varname: str
            Python variable name to assign the constructed object to.
        P_Q: float
            Beam reference momentum-over-charge [MV/c]; see :func:`to_rftrack`.

        Returns
        -------
        tuple
            ``(lines, varnames)``. ``lines`` are the Python source lines
            (assumes ``import RF_Track as rft``/``import numpy as np`` at the
            top of the generated file). Most elements produce exactly one
            object (``varnames == [varname]``), but a builder whose
            ``repr_*`` counterpart returns a **list** of ``(ctor_expr,
            post_stmts)`` (e.g. ``repr_tw_fieldmap``, matching
            :func:`to_rftrack`'s list-returning ``build_tw_fieldmap``)
            produces one block per list entry, uniquely suffixed
            (``{varname}_0``, ``{varname}_1``, ...); ``varnames`` lists every
            object actually created, so the caller can append each one into
            its own Lattice individually (see
            ``SectionLatticeTranslator._save_rftrack_py_file``).
        """
        from ..conversion_rules.codes.rftrack_conversion import (
            repr_drift,
            rftrack_repr_rules,
        )

        self.start_write()
        repr_fn = rftrack_repr_rules.get(self.hardware_type, None)
        if repr_fn is None:
            repr_fn = repr_drift
        result = repr_fn(self, P_Q=P_Q)
        entries = result if isinstance(result, list) else [result]
        lines = []
        varnames = []
        for i, (ctor_expr, post_stmts) in enumerate(entries):
            vn = varname if len(entries) == 1 else f"{varname}_{i}"
            varnames.append(vn)
            lines.append(f"{vn} = rft.{ctor_expr}")
            lines.append(f"{vn}.set_name({self.name!r})")
            lines += self._rftrack_aperture_repr(vn)
            lines += [s.format(var=vn) for s in post_stmts]
        return lines, varnames

    def _rftrack_aperture_params(self):
        """
        Resolve this element's aperture (if any) into the ``(Rx, Ry, shape)``
        arguments used by RF-Track's universal ``set_aperture(Rx, Ry, SHAPE)``
        method (RF-Track has no standalone aperture element -- aperture is a
        property of every element instead). Shared by :func:`_apply_rftrack_aperture`
        and :func:`_rftrack_aperture_repr` so both apply the exact same rule.

        Returns
        -------
        tuple or None
            ``(Rx, Ry, shape)`` or ``None`` if there is no aperture to apply.
        """
        aperture = getattr(self, "aperture", None)
        if aperture is None or not getattr(aperture, "shape", None):
            return None
        shape = aperture.shape
        if shape in ("circular", "elliptical"):
            if aperture.radius is not None:
                rx = ry = aperture.radius
            else:
                rx = (aperture.horizontal_size or 0.0) / 2
                ry = (aperture.vertical_size or 0.0) / 2 or rx
            if rx > 0 or ry > 0:
                return (rx, ry, "circular")
        elif shape in ("planar", "rectangular", "scraper"):
            rx = (aperture.horizontal_size or 0.0) / 2
            ry = (aperture.vertical_size or 0.0) / 2
            if rx > 0 or ry > 0:
                return (rx, ry, "rectangular")
        return None

    def _apply_rftrack_aperture(self, obj: object) -> None:
        """
        Apply this element's aperture (if any) to an already-built RF-Track object,
        via the universal ``set_aperture(Rx, Ry, SHAPE)`` method every RF-Track
        element supports (RF-Track has no standalone aperture element — aperture is
        a property of every element instead).

        Parameters
        ----------
        obj: object
            The RF-Track element object to apply the aperture to.
        """
        params = self._rftrack_aperture_params()
        if params is not None:
            obj.set_aperture(*params)

    def _rftrack_aperture_repr(self, varname: str) -> list:
        """Text-rendering counterpart of :func:`_apply_rftrack_aperture`, for
        :func:`to_rftrack_repr`."""
        params = self._rftrack_aperture_params()
        if params is None:
            return []
        rx, ry, shape = params
        return [f"{varname}.set_aperture({rx!r}, {ry!r}, {shape!r})"]

    def to_wake_t(self) -> object:
        """
        Generates a Wake-T object based on the element's properties and type.

        Returns
        -------
        object
            Wake-T object
        """
        from ..conversion_rules.codes import wake_t_conversion

        type_conversion_rules_Wake_T = wake_t_conversion.wake_t_conversion_rules
        if self.hardware_type in type_conversion_rules_Wake_T:
            obj = type_conversion_rules_Wake_T[self.hardware_type]()
        else:
            if "drift" not in self.hardware_type.lower():
                warn(
                    f"Element type {self.hardware_type} not in Wake-T; setting as drift"
                )
            from wake_t.beamline_elements import Drift as Drift_WakeT

            obj = Drift_WakeT()
        obj.element_name = self.name
        for key, value in self.full_dump().items():
            if key not in ["name", "type", "commandtype"]:
                key = self._convertKeyword_WakeT(key)
                setattr(obj, self._convertKeyword_WakeT(key), value)
        return obj

    def to_opal(self, sval: float, designenergy: float | None = None) -> str:
        """
        Generates a string representation of the object's properties in the OPAL format.

        Parameters
        ----------
        sval: float
            S-position of the element
        designenergy: float, optional
            Beam energy at element in MeV

        Returns
        -------
        str
            A formatted string representing the object's properties in OPAL format.
        """
        # wholestring = ""
        self.start_write()
        etype = self._convertType_Opal(self.hardware_type)
        wholestring = self.name.replace("-", "_") + ": " + etype
        if etype.lower() == "drift":
            return ""
        keys = []
        for key, value in self.full_dump().items():
            if (
                not key == "name"
                and not key == "type"
                and not key == "commandtype"
                and self._convertKeyword_Opal(key) in elements_Opal[etype]
            ):
                if value is not None:
                    key = self._convertKeyword_Opal(key)
                    if value == "angle":
                        value = self.magnetic.KnL(0)
                    elif value == "angle/2":
                        value = self.magnetic.KnL(0) / 2
                    # elif key in ["k1", "k2", "k3", "k4", "k5", "k6"]:
                    #     value = getattr(self, f"{key}l")
                    val = 1 if value is True else value
                    val = 0 if value is False else val
                    tmpstring = ", " + key + " = " + str(val)
                    if key not in keys:
                        wholestring += tmpstring
                        keys.append(key)
        if etype == "monitor":
            wholestring += f', OUTFN = "{self.name}_opal"'
        wholestring += f", ELEMEDGE = {sval};\n"
        return wholestring

    _KEYWORD_STRIP_PREFIXES = ["", "simulation_", "cavity_", "magnetic_", "aperture_"]
    _KEYWORD_STRIP_PREFIXES_WAKE_T = _KEYWORD_STRIP_PREFIXES + ["plasma_", "laser_"]

    @staticmethod
    def _convert_type(etype: str, rules: dict, default):
        """Look up `etype` in a type-conversion rules dict, falling back to `default`."""
        return rules[etype] if etype in rules else default

    def _convert_keyword(
        self,
        keyword: str,
        conversion_rules: dict,
        element: dict | None = None,
        strip_prefixes=_KEYWORD_STRIP_PREFIXES,
    ) -> str:
        """
        Strip known field-group prefixes from `keyword` and look up each candidate in
        `conversion_rules`; if `element` is given, also accept a candidate that matches
        one of its keys directly. Falls back to the original keyword.
        """
        for strip in strip_prefixes:
            stripped = keyword.removeprefix(strip)
            if stripped in conversion_rules:
                return conversion_rules[stripped]
            elif element is not None and stripped in element.keys():
                return stripped
        return keyword

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the MAD-X
        format (see the `MAD-X User Guide <https://madx.web.cern.ch/webguide/manual.html>`_),
        suitable for :meth:`cpymad.madx.Madx.input`.

        Symbolic/functional parameters are emitted as deferred expressions
        (``key := name`` or ``key := name / length``), which MAD-X keeps live
        against the ``<name> = <value>;`` declarations produced by
        :func:`~laura.translator.utils.functions.madx_functional_definitions`.

        Parameters
        ----------
        at: float, optional
            S-position (measured from the start of the sequence, to the entry
            edge of the element) at which to place the element inside a MAD-X
            ``SEQUENCE``. If given, an ``at = <at>`` clause is appended to the
            element definition; if omitted, only the bare element definition
            (as used e.g. to pre-declare an element type) is returned.

        Returns
        -------
        str
            A formatted string representing the object's properties in MAD-X format.
        """
        self.start_write()
        etype = self._convertType_Madx(self.hardware_type)
        string = sanitize_string(self.name) + ": " + etype
        keys = []
        for key, value in self.full_dump(resolve=self._resolve_functional).items():
            if (
                not key == "name"
                and not key == "type"
                and not key == "commandtype"
                and self._convertKeyword_Madx(key) in elements_Madx[etype]
            ):
                if value is not None:
                    key = self._convertKeyword_Madx(key)
                    deferred = False
                    if value in ("angle", "angle/2") and key in ("e1", "e2"):
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_edge_angle(
                                (
                                    "entrance_edge_angle"
                                    if key == "e1"
                                    else "exit_edge_angle"
                                ),
                                "madx",
                            )
                        )
                        if raw is not None:
                            value = raw
                            deferred = True
                        else:
                            value = (
                                self.magnetic.KnL(0)
                                if value == "angle"
                                else self.magnetic.KnL(0) / 2
                            )
                    elif value == "angle":
                        value = self.magnetic.KnL(0)
                    elif value == "angle/2":
                        value = self.magnetic.KnL(0) / 2
                    elif key in ["k1", "k2", "k3", "k4", "k5", "k6"]:
                        expr = (
                            None
                            if self._resolve_functional
                            else self._functional_strength_expr(int(key[1]), "madx")
                        )
                        if expr is not None:
                            value = expr
                            deferred = True
                        else:
                            value = getattr(self, key)
                    elif key == "angle":
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_multipole_strength(0)
                        )
                        if raw is not None:
                            value = raw
                            deferred = True
                    elif not self._resolve_functional and self.is_functional(value):
                        deferred = True
                    value = 1 if value is True else value
                    value = 0 if value is False else value
                    if key not in keys:
                        op = ":=" if deferred else "="
                        string += f", {key} {op} {value}"
                    keys.append(key)
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def _convertType_Elegant(self, etype: str) -> str:
        """Converts the element type to the corresponding Elegant type using predefined rules."""
        converted = self._convert_type(etype, type_conversion_rules_Elegant, etype)
        if converted.lower() not in elements_Elegant:
            return "drift"
        return converted

    def _convertKeyword_Elegant(self, keyword: str, updated_type: str = "") -> str:
        """Converts a keyword to its corresponding Elegant keyword using predefined rules."""
        if updated_type.lower() in keyword_conversion_rules_elegant:
            conversion_rules = (
                keyword_conversion_rules_elegant[updated_type.lower()]
                | keyword_conversion_rules_elegant["general"]
            )
            element = elements_Elegant.get(
                self._convertType_Elegant(updated_type).lower(),
                elements_Elegant["drift"],
            )
        else:
            conversion_rules = self.conversion_rules["elegant"]
            element = elements_Elegant.get(
                self._convertType_Elegant(self.hardware_type).lower(),
                elements_Elegant["drift"],
            )
        return self._convert_keyword(keyword, conversion_rules, element)

    def _convertType_Genesis(self, etype: str) -> str:
        """Converts the element type to the corresponding Genesis type using predefined rules."""
        return self._convert_type(etype, type_conversion_rules_Genesis, etype)

    def _convertKeyword_Genesis(self, keyword: str, updated_type: str = "") -> str:
        """Converts a keyword to its corresponding Genesis keyword using predefined rules."""
        if updated_type.lower() in keyword_conversion_rules_genesis:
            conversion_rules = (
                keyword_conversion_rules_genesis[updated_type.lower()]
                | keyword_conversion_rules_genesis["general"]
            )
            element = elements_Genesis.get(
                self._convertType_Genesis(updated_type), elements_Genesis["drift"]
            )
        else:
            conversion_rules = self.conversion_rules["genesis"]
            element = elements_Genesis.get(
                self._convertType_Genesis(self.hardware_type), elements_Genesis["drift"]
            )
        return self._convert_keyword(keyword, conversion_rules, element)

    def _convertType_Ocelot(self, etype: str) -> object:
        """Converts the element type to the corresponding Ocelot type using predefined rules."""
        from ocelot.cpbd.elements.drift import Drift as Drift_Oce

        from ..conversion_rules.codes import ocelot_conversion

        return self._convert_type(
            etype, ocelot_conversion.ocelot_conversion_rules, Drift_Oce
        )

    def _convertKeyword_Ocelot(self, keyword: str, updated_type: str = "") -> str:
        """Converts a keyword to its corresponding Ocelot keyword using predefined rules."""
        return self._convert_keyword(keyword, self.conversion_rules["ocelot"])

    def _convertType_Cheetah(self, etype: str) -> object:
        """Converts the element type to the corresponding Cheetah type using predefined rules."""
        from cheetah.accelerator import Drift as Drift_Che

        from ..conversion_rules.codes import cheetah_conversion

        return self._convert_type(
            etype, cheetah_conversion.cheetah_conversion_rules, Drift_Che
        )

    def _convertKeyword_Cheetah(self, keyword: str) -> str:
        """Converts a keyword to its corresponding Cheetah keyword using predefined rules."""
        return self._convert_keyword(keyword, self.conversion_rules["cheetah"])

    def _convertKeyword_Xsuite(self, keyword: str) -> str:
        """Converts a keyword to its corresponding Xsuite keyword using predefined rules."""
        return self._convert_keyword(keyword, self.conversion_rules["xsuite"])

    def _convertKeyword_WakeT(self, keyword: str) -> str:
        """Converts a keyword to its corresponding Wake-T keyword using predefined rules."""
        return self._convert_keyword(
            keyword,
            self.conversion_rules["wake_t"],
            strip_prefixes=self._KEYWORD_STRIP_PREFIXES_WAKE_T,
        )

    def _convertType_Opal(self, etype: str) -> str:
        """Converts the element type to the corresponding Opal type using predefined rules."""
        return self._convert_type(etype, type_conversion_rules_Opal, etype)

    def _convertKeyword_Opal(self, keyword: str, updated_type: str = "") -> str:
        """Converts a keyword to its corresponding Opal keyword using predefined rules."""
        if updated_type.lower() in keyword_conversion_rules_opal:
            conversion_rules = (
                keyword_conversion_rules_opal[updated_type.lower()]
                | keyword_conversion_rules_opal["general"]
            )
            element = elements_Opal[self._convertType_Opal(updated_type)]
        else:
            conversion_rules = self.conversion_rules["opal"]
            element = elements_Opal[self._convertType_Opal(self.hardware_type)]
        return self._convert_keyword(keyword, conversion_rules, element)

    def _convertType_Madx(self, etype: str) -> str:
        """
        Converts the element type to the corresponding MAD-X type using predefined rules.

        Parameters
        ----------
        etype: str
            The type of the element to be converted.

        Returns
        -------
        str
            The converted type of the element, or the original type if no conversion rule exists.
        """
        return (
            type_conversion_rules_Madx[etype]
            if etype in type_conversion_rules_Madx
            else etype
        )

    def _convertKeyword_Madx(self, keyword: str, updated_type: str = "") -> str:
        """
        Converts a keyword to its corresponding MAD-X keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for MAD-X, or the original keyword if no conversion rule exists.
        """
        if updated_type.lower() in keyword_conversion_rules_madx:
            conversion_rules = (
                keyword_conversion_rules_madx[updated_type.lower()]
                | keyword_conversion_rules_madx["general"]
            )
            element = elements_Madx[self._convertType_Madx(updated_type).lower()]
        else:
            conversion_rules = self.conversion_rules["madx"]
            element = elements_Madx[self._convertType_Madx(self.hardware_type).lower()]
        for strip in ["", "simulation_", "cavity_", "magnetic_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
            elif stripped in element.keys():
                return stripped
        return keyword

    def _convertType_Bmad(self, etype: str) -> str:
        """
        Converts the element type to the corresponding Bmad type using predefined rules.

        Parameters
        ----------
        etype: str
            The type of the element to be converted.

        Returns
        -------
        str
            The converted type of the element, or the original type if no conversion rule exists.
        """
        converted = self._convert_type(etype, type_conversion_rules_Bmad, etype)
        return converted if converted.lower() in elements_Bmad else "drift"

    def _convertKeyword_Bmad(self, keyword: str, updated_type: str = "") -> str:
        """
        Converts a keyword to its corresponding Bmad keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.
        updated_type: str
            Optional override for type name

        Returns
        -------
        str
            The converted keyword for Bmad, or the original keyword if no conversion rule exists.
        """
        hardware_type = updated_type or self.hardware_type
        key = hardware_type.lower()
        conversion_rules = (
            keyword_conversion_rules_bmad[key]
            | keyword_conversion_rules_bmad["general"]
            if key in keyword_conversion_rules_bmad
            else self.conversion_rules["bmad"]
        )
        element = (
            elements_Bmad[self._convertType_Bmad(hardware_type).lower()]
            | elements_Bmad["common"]
        )
        return self._convert_keyword(
            keyword,
            conversion_rules,
            element,
            strip_prefixes=(
                "",
                "simulation_",
                "cavity_",
                "magnetic_",
                "aperture_",
                "physical_",
            ),
        )

    def _bmad_parameters(self, etype: str | None = None) -> Dict[str, Any]:
        """
        Return the native Bmad attributes represented by this element.

        Parameters
        ----------
        etype: str | None
            Element type

        Returns
        -------
        dict
            Dictionary of Bmad parameters associated with the element
        """
        etype = etype or self._convertType_Bmad(self.hardware_type)
        common = elements_Bmad["common"]
        element = elements_Bmad[etype] | common
        explicit = self.simulation.model_fields_set
        parameters = {}
        for source_key, value in self.full_dump(
            resolve=self._resolve_functional
        ).items():
            key = self._convertKeyword_Bmad(source_key)
            if value is None or key not in element:
                continue
            source_field = source_key.removeprefix("simulation_")
            if source_field not in explicit and (
                key in common
                or source_field in {"horizontal_offset", "vertical_offset"}
            ):
                continue
            if value in ("angle", "angle/2") and key in ("e1", "e2"):
                raw = (
                    None
                    if self._resolve_functional
                    else self._raw_edge_angle(
                        "entrance_edge_angle" if key == "e1" else "exit_edge_angle",
                        "bmad",
                    )
                )
                value = (
                    raw
                    if raw is not None
                    else (
                        self.magnetic.KnL(0)
                        if value == "angle"
                        else self.magnetic.KnL(0) / 2
                    )
                )
            elif key in ("k1", "k2", "k3", "k4"):
                expression = (
                    None
                    if self._resolve_functional
                    else self._functional_strength_expr(int(key[1]), "bmad")
                )
                value = expression if expression is not None else getattr(self, key)
            elif key == "angle":
                raw = (
                    None
                    if self._resolve_functional
                    else self._raw_multipole_strength(0)
                )
                value = raw if raw is not None else self.magnetic.KnL(0)
            parameters.setdefault(key, value)
        length = self.length
        cavity = getattr(self, "cavity", None)
        if not length and cavity is not None:
            length = cavity.cell_length * (cavity.n_cells or 1)
        if "l" in element:
            parameters["l"] = length
        if etype in ("sbend", "rbend"):
            parameters["hgap"] = self.magnetic.half_gap
            parameters["fint"] = self.magnetic.edge_field_integral
        return parameters

    def _bmad_common_parameters(self) -> Dict[str, Any]:
        """Return common Bmad attributes represented by this element."""
        return {
            key: value
            for key, value in self._bmad_parameters().items()
            if key in elements_Bmad["common"]
        }

    def _format_bmad(
        self,
        etype: str | None = None,
        parameters: Dict[str, Any] | None = None,
    ) -> str:
        """
        Format one Bmad lattice element definition.

        Parameters
        ----------
        etype: str | None
            Element type
        parameters: Dict[str, Any] | None
            Element parameters

        Returns
        -------
        str
            Formatted string for Bmad output
        """
        self.start_write()
        etype = etype or self._convertType_Bmad(self.hardware_type)
        element = elements_Bmad[etype] | elements_Bmad["common"]
        if parameters is None:
            parameters = self._bmad_parameters(etype)
        else:
            parameters = self._bmad_common_parameters() | parameters
        parameters.update(bmad_misalignment(self, etype, parameters))

        def render(key, value):
            if value is True:
                return "T"
            if value is False:
                return "F"
            if element.get(key) == "integer":
                return str(int(value))
            return str(value)

        attributes = "".join(
            f", {key} = {render(key, value)}" for key, value in parameters.items()
        )
        return f"{sanitize_string(self.name)}: {etype}{attributes}\n"

    def to_bmad(self) -> str:
        """
        Generate a Bmad lattice element string.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        return self._format_bmad()

    def _write_ASTRA_dictionary(self, d: dict, n: int | None = 1) -> str:
        """
        Generates a string representation of the object's properties in the ASTRA format.

        Parameters
        ----------
        d: dict
            A dictionary containing the properties of the object to be formatted.
        n: int, optional
            An optional integer to specify the index for ASTRA objects. Default is 1.

        Returns
        -------
        str
            A formatted string representing the object's properties in ASTRA format.
        """
        output = ""
        for k, v in list(d.items()):
            if checkValue(self, v) is not None:
                if "type" in v and v["type"] == "list":
                    for i, l in enumerate(checkValue(self, v)):
                        if n is not None:
                            param_string = (
                                k
                                + "("
                                + str(i + 1)
                                + ","
                                + str(n)
                                + ") = "
                                + str(l)
                                + ", "
                            )
                        else:
                            param_string = k + " = " + str(l) + "\n"
                        if len((output + param_string).splitlines()[-1]) > 70:
                            output += "\n"
                        output += param_string
                elif "type" in v and v["type"] == "array":
                    if n is not None:
                        param_string = k + "(" + str(n) + ") = ("
                    else:
                        param_string = k + " = ("
                    for i, l in enumerate(checkValue(self, v)):
                        param_string += str(l) + ", "
                        if len((output + param_string).splitlines()[-1]) > 70:
                            output += "\n"
                    output += param_string[:-2] + "),\n"
                elif "type" in v and v["type"] == "not_zero":
                    if abs(checkValue(self, v)) > 0:
                        if n is not None:
                            param_string = (
                                k
                                + "("
                                + str(n)
                                + ") = "
                                + str(checkValue(self, v))
                                + ", "
                            )
                        else:
                            param_string = k + " = " + str(checkValue(self, v)) + ",\n"
                        if len((output + param_string).splitlines()[-1]) > 70:
                            output += "\n"
                        output += param_string
                else:
                    if n is not None:
                        param_string = (
                            k + "(" + str(n) + ") = " + str(checkValue(self, v)) + ", "
                        )
                    else:
                        param_string = k + " = " + str(checkValue(self, v)) + ",\n"
                    if len((output + param_string).splitlines()[-1]) > 70:
                        output += "\n"
                    output += param_string
        return output[:-2] + "\n"

    @computed_field
    @property
    def length(self) -> float:
        leng = self.physical.length
        if leng == 0:
            try:
                return self.magnetic.length
            except Exception:
                return leng
        return leng

    @computed_field
    @property
    def dx(self) -> float:
        return self.physical.error.position.x

    @computed_field
    @property
    def dy(self) -> float:
        return self.physical.error.position.y

    @computed_field
    @property
    def dz(self) -> float:
        return self.physical.error.position.z

    @computed_field
    @property
    def x_rot(self) -> float:
        """Design rotation in the x-plane, i.e. about the **y** axis [rad]."""
        return self.physical.rotation.theta

    @computed_field
    @property
    def y_rot(self) -> float:
        """Design rotation in the y-plane, i.e. about the **x** axis [rad]."""
        return self.physical.rotation.phi

    @computed_field
    @property
    def z_rot(self) -> float:
        """Design roll, about the longitudinal (z) axis [rad]."""
        return self.physical.rotation.psi

    @computed_field
    @property
    def dx_rot(self) -> float:
        """Alignment error in the x-plane, i.e. about the **y** axis [rad]."""
        return self.physical.error.rotation.theta

    @computed_field
    @property
    def dy_rot(self) -> float:
        """Alignment error in the y-plane, i.e. about the **x** axis [rad]."""
        return self.physical.error.rotation.phi

    @computed_field
    @property
    def dz_rot(self) -> float:
        """Roll error, about the longitudinal (z) axis [rad]."""
        return self.physical.error.rotation.psi

    def _astra_rotation(self, plane: str) -> float:
        """The total design-plus-error rotation for one plane, in ASTRA's sense."""
        sign = _ASTRA_ROTATION_SIGN[plane]
        return sign * (getattr(self, f"{plane}_rot") + getattr(self, f"d{plane}_rot"))

    def get_field_reference_position(self, if_none: str = "start") -> np.ndarray:
        """
        Returns the position of the field reference point based on the `field_reference_position` attribute.

        Returns
        -------
        list
            The position of the field reference point, which can be 'start', 'middle', or 'end'.
            If `field_reference_position` is not set, it defaults to the start position.

        Raises
        ------
        ValueError
            If `field_reference_position` is set to an invalid value that is not 'start', 'middle', or 'end'.
        """
        if self.simulation.field_reference_position is not None:
            try:
                return np.array(
                    list(
                        getattr(
                            self.physical,
                            self.simulation.field_reference_position.lower(),
                        )
                        .model_dump()
                        .values()
                    )
                )
            except AttributeError:
                warn(
                    "field_reference_position should be (start/middle/end) not"
                    + self.simulation.field_reference_position
                    + "; returning start"
                )
        else:
            try:
                return np.array(
                    list(getattr(self.physical, if_none.lower()).model_dump().values())
                )
            except AttributeError:
                return np.array(list(self.physical.start.model_dump().values()))
        return np.array(list(self.physical.start.model_dump().values()))

    def update_field_definition(self) -> None:
        """
        Updates the field definitions to allow for the relative sub-directory location
        """
        if hasattr(self, "simulation"):
            if (
                hasattr(self.simulation, "field_definition")
                and self.simulation.field_definition is not None
                and isinstance(self.simulation.field_definition, str)
            ):
                field_kwargs = {
                    "filename": expand_substitution(
                        self,
                        self.simulation.field_definition,
                        self.master_lattice,
                    ),
                    # "field_type": self.field_type,
                }
                if "cavity" in self.hardware_type.lower():
                    field_kwargs.update(
                        {
                            "frequency": self.cavity.frequency,
                            "cavity_type": self.cavity.structure_type,
                            "n_cells": self.cavity.n_cells,
                        }
                    )
                try:
                    self.simulation.field_definition = field(**field_kwargs)
                except Exception as exc:
                    raise Exception(
                        f"Setting field definition on {self.name} failed: {field_kwargs}"
                    )
            if (
                hasattr(self.simulation, "wakefield_definition")
                and self.simulation.wakefield_definition is not None
                and isinstance(self.simulation.wakefield_definition, str)
            ):
                if hasattr(self, "cavity"):
                    additional = {}
                    if hasattr(self.cavity, "frequency"):
                        additional.update({"frequency": self.cavity.frequency})
                    if hasattr(self.cavity, "structure_type"):
                        additional.update(
                            {"structure_Type": self.cavity.structure_type}
                        )
                        cavity_type = (self.cavity.structure_type,)
                    self.simulation.wakefield_definition = field(
                        filename=expand_substitution(
                            self,
                            self.simulation.wakefield_definition,
                            self.master_lattice,
                        ),
                        # field_type=self.field_type,
                        n_cells=self.cavity.n_cells,
                        **additional,
                    )
                else:
                    self.simulation.wakefield_definition = field(
                        filename=expand_substitution(
                            self,
                            self.simulation.wakefield_definition,
                            self.master_lattice,
                        ),
                    )

    def _wakefield_active(self) -> bool:
        """
        Whether this element should be written with its wakefield applied.

        False if wakefields have been switched off for the element, if no
        wakefield definition is set, or if the definition carries no usable
        data.

        Returns
        -------
        bool
            True if a usable wakefield is defined and enabled
        """
        if not getattr(self.simulation, "wakefield_enable", True):
            return False
        wake = getattr(self.simulation, "wakefield_definition", None)
        if wake is None or wake == "":
            return False
        if not isinstance(wake, str):
            # a field object: only usable if it has a longitudinal coordinate
            try:
                wake.z_values
            except Exception:
                return False
        return True

    def _bmad_sr_wake(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add this element's short-range wake to its Bmad parameters, if it has one. Bmad
        takes a tabulated wake by ``call::`` and not inline.

        Parameters
        ----------
        parameters: Dict[str, Any]
            Bmad parameters for the element, modified in place

        Returns
        -------
        Dict[str, Any]
            The same parameters
        """
        if self._wakefield_active():
            wake = self.generate_field_file_name(
                self.simulation.wakefield_definition,
                code="bmad",
                verbose=getattr(self, "verbose", True),
            )
            if wake:
                parameters["sr_wake"] = f"call::{wake}"
        return parameters

    def generate_field_file_name(self, param: field, code: str, **kwargs) -> str | None:
        """
        Generates a field file name based on the provided frameworkElement and tracking code.

        Parameters
        ----------
        param: field
            The :class:`~laura.translator.utils.fields.field` object for which the field file is being generated.
        code: str
            The tracking code for which the field file is being generated (e.g., 'elegant', 'ocelot').

        Returns
        -------
        str | None
            The name of the field file if it exists, otherwise None.
        """
        if hasattr(param, "filename"):
            self.make_directory()
            basename = (
                os.path.basename(param.filename).replace('"', "").replace("'", "")
            )
            efield_basename = os.path.abspath(
                os.path.join(
                    self.directory.replace("\\", "/"), basename.replace("\\", "/")
                )
            )
            filename = param.write_field_file(
                code=code, location=efield_basename, **kwargs
            )
            return os.path.basename(filename) if filename else None
        else:
            if param:
                warn(
                    f"param associated with {self.name} does not have a filename: {param}, it must be a `field` object"
                )
        return None

    @property
    def get_field_amplitude(self) -> float:
        """
        Returns the field amplitude of the element, scaled by `scale_field` if it exists.

        Returns
        -------
        float or None
            The field amplitude of the element, which is either scaled by `scale_field`
            or directly taken from `field_amplitude`.
            Returns None if `field_amplitude` is not defined

        """
        if hasattr(self, "magnetic"):
            if hasattr(self.magnetic, "fields"):
                if hasattr(self.magnetic.fields, "S0L"):
                    # Resolve a functional definition to its number before substitution.
                    s0l = self.resolve(self.magnetic.fields.S0L)
                    if type(self.simulation.scale_field) in [int, float]:
                        return float(self.scale_field) * float(
                            expand_substitution(self, s0l, self.master_lattice)
                        )
                    else:
                        return float(
                            expand_substitution(self, s0l, self.master_lattice)
                        )
                return 0.0
            return 0.0
        return 0.0

    def make_directory(self) -> None:
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory)
