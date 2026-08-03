import os
import numpy as np
from pydantic import computed_field, Field

from laura.models.physical import PhysicalElement, Position  # noqa E402
from laura.models.element import flatten, PhysicalBaseElement
from laura.models.baseModels import IgnoreExtra
from typing import Dict, Any
from warnings import warn

from ..converters import (
    type_conversion_rules,
    type_conversion_rules_Elegant,
    type_conversion_rules_Genesis,
    type_conversion_rules_Opal,
    type_conversion_rules_Madx,
    elements_Elegant,
    elements_Genesis,
    elements_Opal,
    elements_Madx,
    keyword_conversion_rules_elegant,
    keyword_conversion_rules_genesis,
    keyword_conversion_rules_ocelot,
    keyword_conversion_rules_cheetah,
    keyword_conversion_rules_xsuite,
    keyword_conversion_rules_wake_t,
    keyword_conversion_rules_opal,
    keyword_conversion_rules_madx,
)
from ..utils.fields import field
from ..utils.functions import expand_substitution, checkValue, sanitize_string
from ..converters.codes.gpt import gpt_ccs


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

    master_lattice: str = None
    """Location of the directory containing lattice/data/simulation files."""

    directory: str = "./"
    """Directory to which lattice/element files will be written."""

    ccs: gpt_ccs = None
    """Co-ordinate system for GPT elements."""

    def model_post_init(self, __context):
        self.type_conversion_rules = type_conversion_rules
        self.conversion_rules["elegant"] = keyword_conversion_rules_elegant["general"]
        self.conversion_rules["ocelot"] = keyword_conversion_rules_ocelot["general"]
        self.conversion_rules["cheetah"] = keyword_conversion_rules_cheetah["general"]
        self.conversion_rules["xsuite"] = keyword_conversion_rules_xsuite["general"]
        self.conversion_rules["wake_t"] = keyword_conversion_rules_wake_t["general"]
        self.conversion_rules["genesis"] = keyword_conversion_rules_genesis["general"]
        self.conversion_rules["opal"] = keyword_conversion_rules_opal["general"]
        if self.hardware_type.lower() in keyword_conversion_rules_elegant:
            self.conversion_rules["elegant"] = (
                keyword_conversion_rules_elegant[self.hardware_type.lower()]
                | keyword_conversion_rules_elegant["general"]
            )
        if self.hardware_type.lower() in keyword_conversion_rules_ocelot:
            self.conversion_rules["ocelot"] = (
                keyword_conversion_rules_ocelot[self.hardware_type.lower()]
                | keyword_conversion_rules_ocelot["general"]
            )
        if self.hardware_type.lower() in keyword_conversion_rules_cheetah:
            self.conversion_rules["cheetah"] = (
                keyword_conversion_rules_cheetah[self.hardware_type.lower()]
                | keyword_conversion_rules_cheetah["general"]
            )
        if self.hardware_type.lower() in keyword_conversion_rules_xsuite:
            self.conversion_rules["xsuite"] = (
                keyword_conversion_rules_xsuite[self.hardware_type.lower()]
                | keyword_conversion_rules_xsuite["general"]
            )
        if self.hardware_type.lower() in keyword_conversion_rules_wake_t:
            self.conversion_rules["wake_t"] = (
                keyword_conversion_rules_wake_t[self.hardware_type.lower()]
                | keyword_conversion_rules_wake_t["general"]
            )
        if self.hardware_type.lower() in keyword_conversion_rules_genesis:
            self.conversion_rules["genesis"] = (
                keyword_conversion_rules_genesis[self.hardware_type.lower()]
                | keyword_conversion_rules_genesis["general"]
            )
        if self.hardware_type.lower() in keyword_conversion_rules_opal:
            self.conversion_rules["opal"] = (
                keyword_conversion_rules_opal[self.hardware_type.lower()]
                | keyword_conversion_rules_opal["general"]
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
        data = flatten({**self.model_dump()}, parent_key="", separator="_")
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

        ELEGANT and Xsuite require the normalized k-value, whereas the functional
        definition is stored on the multipole as the integrated kl-value, so the
        division by length is folded into the symbolic expression (rpn for
        ELEGANT, an infix string for Xsuite). For zero-length magnets the
        normalized strength equals the integrated value (mirroring the numeric
        ``KnL / length`` fall-back).
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
          ``"angle"``/``"angle/2"``, see :attr:`DipoleTranslator.angle
          <laura.translator.converters.magnet.DipoleTranslator.angle>`) -- if
          the bend angle itself is defined functionally, the token is
          substituted with that functional name, producing a valid expression
          (rpn for ELEGANT, infix for other codes, e.g. ``"bend1 / 2"``);
          otherwise returns None (the bend angle is a plain number, so the
          edge angle should be resolved numerically as usual).
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
            # Any other expression referencing "angle": substitute the token
            # (infix codes only -- ELEGANT rpn doesn't support arbitrary
            # substitution into an infix expression here).
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
                        # Dipole edge angle referencing the reserved "angle"
                        # token: carry a functional bend angle through
                        # symbolically (as an rpn expression); otherwise
                        # resolve numerically as before.
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_edge_angle(
                                "entrance_edge_angle" if key == "e1" else "exit_edge_angle",
                                "elegant",
                            )
                        )
                        value = raw if raw is not None else (
                            self.magnetic.KnL(0) if value == "angle" else self.magnetic.KnL(0) / 2
                        )
                    elif value == "angle":
                        value = self.magnetic.KnL(0)
                    elif value == "angle/2":
                        value = self.magnetic.KnL(0) / 2
                    elif key in ["k1", "k2", "k3", "k4", "k5", "k6"]:
                        # When rendering symbolically, carry a functional strength
                        # through to ELEGANT as the normalized k = KnL/length (an
                        # rpn expression); otherwise use the computed numeric value.
                        expr = (
                            None
                            if self._resolve_functional
                            else self._functional_strength_expr(int(key[1]), "elegant")
                        )
                        value = expr if expr is not None else getattr(self, f"{key}")
                    elif key == "angle":
                        # Dipole bend angle: carry a functional definition through
                        # symbolically (ELEGANT ANGLE is the integrated KnL(0)); it
                        # is quoted by _elegant_value below.
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_multipole_strength(0)
                        )
                        if raw is not None:
                            value = raw
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
        from ocelot.cpbd.elements import Marker, Aperture
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
                    setattr(obj, self._convertKeyword_Ocelot(key), value)
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
        from cheetah.accelerator import Screen as Screen_Cheetah
        from cheetah.accelerator import Drift as Drift_Cheetah
        from ..conversion_rules.codes import cheetah_conversion
        from torch import tensor, float64

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
                    return obj
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
                if key in ["k1", "k2", "k3", "k4", "k5", "k6"]:
                    value = getattr(self, f"{key}l")
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
                    # else:
                    #     from torch import get_default_dtype
                    #     dt = get_default_dtype()
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
                if key in ["k1", "k2", "k3", "k4", "k5", "k6"] and not self._resolve_functional:
                    # Carry a symbolic functional strength through to Xsuite as the
                    # normalized k = KnL/length, referencing the Environment
                    # variable; else use the number.
                    expr = self._functional_strength_expr(int(key[1]), "xsuite")
                    if expr is not None:
                        value = expr
                if key == "angle":
                    if self.length > 0:
                        # Xsuite dipole uses k0 = angle / length; carry a functional
                        # bend angle through symbolically as an Environment expression.
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
                if "edge" in key and isinstance(value, str) and not self.is_functional(value):
                    if value == "angle":
                        value = self.magnetic.KnL(0)
                    elif value == "angle/2":
                        value = self.magnetic.KnL(0) / 2
                properties.update({key: value})
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
                        # Dipole edge angle referencing the reserved "angle"
                        # token: carry a functional bend angle through
                        # symbolically (as a deferred expression); otherwise
                        # resolve numerically as before.
                        raw = (
                            None
                            if self._resolve_functional
                            else self._raw_edge_angle(
                                "entrance_edge_angle" if key == "e1" else "exit_edge_angle",
                                "madx",
                            )
                        )
                        if raw is not None:
                            value = raw
                            deferred = True
                        else:
                            value = self.magnetic.KnL(0) if value == "angle" else self.magnetic.KnL(0) / 2
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
        """
        Converts the element type to the corresponding Elegant type using predefined rules.

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
            type_conversion_rules_Elegant[etype]
            if etype in type_conversion_rules_Elegant
            else etype
        )

    def _convertKeyword_Elegant(self, keyword: str, updated_type: str = "") -> str:
        """
        Converts a keyword to its corresponding Elegant keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for Elegant, or the original keyword if no conversion rule exists.

        """
        if updated_type.lower() in keyword_conversion_rules_elegant:
            conversion_rules = (
                keyword_conversion_rules_elegant[updated_type.lower()]
                | keyword_conversion_rules_elegant["general"]
            )
            element = elements_Elegant.get(self._convertType_Elegant(updated_type).lower(), "drift")
        else:
            conversion_rules = self.conversion_rules["elegant"]
            element = elements_Elegant.get(
                self._convertType_Elegant(self.hardware_type).lower(), "drift"
            )
        for strip in ["", "simulation_", "cavity_", "magnetic_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
            elif stripped in element.keys():
                return stripped
        return keyword

    def _convertType_Genesis(self, etype: str) -> str:
        """
        Converts the element type to the corresponding Genesis type using predefined rules.

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
            type_conversion_rules_Genesis[etype]
            if etype in type_conversion_rules_Genesis
            else etype
        )

    def _convertKeyword_Genesis(self, keyword: str, updated_type: str = "") -> str:
        """
        Converts a keyword to its corresponding Genesis keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for Genesis, or the original keyword if no conversion rule exists.

        """
        if updated_type.lower() in keyword_conversion_rules_genesis:
            conversion_rules = (
                keyword_conversion_rules_genesis[updated_type.lower()]
                | keyword_conversion_rules_genesis["general"]
            )
            element = elements_Genesis.get(self._convertType_Genesis(updated_type), "drift")
        else:
            conversion_rules = self.conversion_rules["genesis"]
            element = elements_Genesis.get(self._convertType_Genesis(self.hardware_type), "drift")
        for strip in ["", "simulation_", "cavity_", "magnetic_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
            elif stripped in element.keys():
                return stripped
        return keyword

    def _convertType_Ocelot(self, etype: str) -> object:
        """
        Converts the element type to the corresponding Ocelot type using predefined rules.

        Parameters
        ----------
        etype: str
            The type of the element to be converted.

        Returns
        -------
        object
            The Ocelot element, or the original type if no conversion rule exists.
        """
        from ..conversion_rules.codes import ocelot_conversion
        from ocelot.cpbd.elements.drift import Drift as Drift_Oce

        return ocelot_conversion.ocelot_conversion_rules.get(etype, Drift_Oce)

    def _convertKeyword_Ocelot(self, keyword: str, updated_type: str = "") -> str:
        """
        Converts a keyword to its corresponding Ocelot keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for Ocelot, or the original keyword if no conversion rule exists.

        """
        conversion_rules = self.conversion_rules["ocelot"]
        for strip in ["", "simulation_", "cavity_", "magnetic_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
        return keyword

    def _convertType_Cheetah(self, etype: str) -> object:
        """
        Converts the element type to the corresponding Cheetah type using predefined rules.

        Parameters
        ----------
        etype: str
            The type of the element to be converted.

        Returns
        -------
        object
            The Cheetah element, or the original type if no conversion rule exists.
        """
        from ..conversion_rules.codes import cheetah_conversion
        from cheetah.accelerator import Drift as Drift_Che

        return cheetah_conversion.cheetah_conversion_rules.get(etype, Drift_Che)

    def _convertKeyword_Cheetah(self, keyword: str) -> str:
        """
        Converts a keyword to its corresponding Cheetah keyword using predefined rules.

        Parameters
        ----------
        keyword: str
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for Cheetah, or the original keyword if no conversion rule exists.
        """
        conversion_rules = self.conversion_rules["cheetah"]
        for strip in ["", "simulation_", "cavity_", "magnetic_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
        return keyword

    def _convertKeyword_Xsuite(self, keyword: str) -> str:
        """
        Converts a keyword to its corresponding Xsuite keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for Xsuite, or the original keyword if no conversion rule exists.

        """
        conversion_rules = self.conversion_rules["xsuite"]
        for strip in ["", "simulation_", "cavity_", "magnetic_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
        return keyword

    def _convertKeyword_WakeT(self, keyword: str) -> str:
        """
        Converts a keyword to its corresponding Wake-T keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for Wake-T, or the original keyword if no conversion rule exists.

        """
        conversion_rules = self.conversion_rules["wake_t"]
        for strip in ["", "simulation_", "cavity_", "magnetic_", "plasma_", "laser_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
        return keyword

    def _convertType_Opal(self, etype: str) -> str:
        """
        Converts the element type to the corresponding Opal type using predefined rules.

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
            type_conversion_rules_Opal[etype]
            if etype in type_conversion_rules_Opal
            else etype
        )

    def _convertKeyword_Opal(self, keyword: str, updated_type: str = "") -> str:
        """
        Converts a keyword to its corresponding Opal keyword using predefined rules.

        Parameters
        ----------
        keyword: str:
            The keyword to be converted.

        Returns
        -------
        str
            The converted keyword for Opal, or the original keyword if no conversion rule exists.

        """
        if updated_type.lower() in keyword_conversion_rules_opal:
            conversion_rules = (
                keyword_conversion_rules_opal[updated_type.lower()]
                | keyword_conversion_rules_opal["general"]
            )
            element = elements_Opal[self._convertType_Opal(updated_type)]
        else:
            conversion_rules = self.conversion_rules["opal"]
            element = elements_Opal[self._convertType_Opal(self.hardware_type)]
        for strip in ["", "simulation_", "cavity_", "magnetic_", "aperture_"]:
            stripped = keyword.replace(strip, "")
            if stripped in conversion_rules:
                return conversion_rules[stripped]
            elif stripped in element.keys():
                return stripped
        return keyword

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
        return self.physical.rotation.theta

    @computed_field
    @property
    def y_rot(self) -> float:
        return self.physical.rotation.phi

    @computed_field
    @property
    def z_rot(self) -> float:
        return self.physical.rotation.psi

    @computed_field
    @property
    def dx_rot(self) -> float:
        return self.physical.error.rotation.theta

    @computed_field
    @property
    def dy_rot(self) -> float:
        return self.physical.error.rotation.phi

    @computed_field
    @property
    def dz_rot(self) -> float:
        return self.physical.error.rotation.psi

    def get_field_reference_position(self) -> np.ndarray:
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
                return np.array(list(getattr(
                    self.physical, self.simulation.field_reference_position.lower()
                ).model_dump().values()))
            except AttributeError:
                warn(
                    "field_reference_position should be (start/middle/end) not"
                    + self.simulation.field_reference_position
                    + "; returning start"
                )
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
                        self, self.simulation.field_definition, self.master_lattice,
                    ),
                    # "field_type": self.field_type,
                }
                if "cavity" in self.hardware_type.lower():
                    field_kwargs.update(
                        {
                            "frequency": self.cavity.frequency,
                            "cavity_type": self.cavity.structure_Type,
                            "n_cells": self.cavity.n_cells,
                        }
                    )
                self.simulation.field_definition = field(**field_kwargs)
            if (
                hasattr(self.simulation, "wakefield_definition")
                and self.simulation.wakefield_definition is not None
                and isinstance(self.simulation.wakefield_definition, str)
            ):
                if hasattr(self, "cavity"):
                    additional = {}
                    if hasattr(self.cavity, "frequency"):
                        additional.update({"frequency": self.cavity.frequency})
                    if hasattr(self.cavity, "structure_Type"):
                        additional.update(
                            {"structure_Type": self.cavity.structure_Type}
                        )
                        cavity_type = (self.cavity.structure_Type,)
                    self.simulation.wakefield_definition = field(
                        filename=expand_substitution(
                            self, self.simulation.wakefield_definition, self.master_lattice,
                        ),
                        # field_type=self.field_type,
                        n_cells=self.cavity.n_cells,
                        **additional,
                    )
                else:
                    self.simulation.wakefield_definition = field(
                        filename=expand_substitution(
                            self, self.simulation.wakefield_definition, self.master_lattice,
                        ),
                    )

    def generate_field_file_name(self, param: field, code: str) -> str | None:
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
            return os.path.basename(
                param.write_field_file(code=code, location=efield_basename)
            )
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
