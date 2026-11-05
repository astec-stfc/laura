import math
from typing import Dict
from warnings import warn

from laura.models.element import CrystalElement, TargetElement
from laura.models.simulation import ApertureElement

from ..converters import elements_elegant, elements_madx
from ..utils.functions import sanitize_string
from .base import BaseElementTranslator, bmad_limits, elegant_line

SILICON_LATTICE_CONSTANT = 5.431e-10
"""Silicon's cubic lattice constant [m], the default unit cell of a :class:`CrystalTranslator`."""

OPAL_THIN_APERTURE_LENGTH = 0.01
"""Length [m] OPAL gives an aperture that has none. OPAL removes only the particles it
finds inside a collimator, and stops unless the length is more than ten time steps of
drift (6 mm at ``DT`` = 2 ps)."""


class ApertureTranslator(BaseElementTranslator):
    """Apertures and collimators. Every code gets a local aperture of the
    LAURA shape; a code with only thin apertures gets one at each end of a
    drift, which is exact for a convex aperture."""

    aperture: ApertureElement

    @property
    def _elliptical(self) -> bool:
        shape = getattr(self.aperture.shape, "value", self.aperture.shape)
        return shape in ("elliptical", "circular")

    def _offsets(self) -> tuple:
        return self.aperture.horizontal_offset, self.aperture.vertical_offset

    def _warn_dropped_offset(self, code: str) -> None:
        if any(self._offsets()):
            warn(
                f"{code} apertures are centred; the offset of {self.name!r} was dropped."
            )

    def _convert_type_madx(self, etype: str) -> str:
        return "ecollimator" if self._elliptical else "rcollimator"

    def _convert_type_elegant(self, etype: str) -> str:
        return "ecol" if self._elliptical else "rcol"

    def _convert_type_opal(self, etype: str) -> str:
        return "ecollimator" if self._elliptical else "rcollimator"

    def to_bmad(self) -> str:
        """
        Generate a native Bmad collimator.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        etype = "ecollimator" if self._elliptical else "rcollimator"
        horizontal, vertical = self._half_sizes()
        return self._format_bmad(
            etype,
            {"l": self.length}
            | bmad_limits(self.name, self.aperture, horizontal, vertical),
        )

    def xsuite_limit(self) -> tuple | None:
        """
        The aperture as an Xsuite black absorber: a thin ``LimitEllipse`` (circular,
        elliptical) or ``LimitRect`` (rectangular, planar, scraper; a plane without a
        size is open), which
        :meth:`~laura.translator.converters.section.SectionLattice.to_xsuite` places at
        the element's entrance and exit. Sizes are half widths.

        Returns
        -------
        tuple or None
            ``(xtrack class, properties)``, or None if the aperture has no size.
        """
        import xtrack as xt

        shape = getattr(self.aperture.shape, "value", self.aperture.shape)
        half_x = self.aperture.horizontal_size or 0.0
        half_y = self.aperture.vertical_size or 0.0
        if shape in ("circular", "elliptical"):
            a = self.aperture.radius or half_x or half_y
            b = self.aperture.radius or half_y or a
            return (xt.LimitEllipse, {"a": a, "b": b}) if a else None
        limits = {}
        if half_x:
            limits.update(min_x=-half_x, max_x=half_x)
        if half_y:
            limits.update(min_y=-half_y, max_y=half_y)
        return (xt.LimitRect, limits) if limits else None

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the MAD-X
        format.

        An elliptical or circular aperture (``aperture.shape in ["elliptical",
        "circular"]``) is written as a MAD-X ``ECOLLIMATOR`` rather than the
        default ``RCOLLIMATOR``.

        Parameters
        ----------
        at: float, optional
            S-position at which to place the element inside a MAD-X ``SEQUENCE``;
            see :meth:`~laura.translator.converters.base.BaseElementTranslator.to_madx`.

        Returns
        -------
        str
            String representation of the element for MAD-X
        """
        self.start_write()
        etype = self._convert_type_madx(self.hardware_type)
        string = sanitize_string(self.name) + ": " + etype
        for key, value in self._dump_items(
            self._convert_keyword_madx,
            elements_madx[etype],
            resolve=self._resolve_functional,
        ):
            deferred = not self._resolve_functional and self.is_functional(value)
            string += f", {key} {':=' if deferred else '='} {self._flag(value)}"
        horizontal, vertical = self._half_sizes()
        if horizontal:
            apertype = "ellipse" if etype == "ecollimator" else "rectangle"
            string += (
                f", apertype = {apertype}, aperture = {{{horizontal}, {vertical}}}"
            )
        if any(self._offsets()):
            ox, oy = self._offsets()
            string += f", aper_offset = {{{ox}, {oy}}}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def _half_sizes(self) -> tuple:
        """Horizontal and vertical half apertures; a missing vertical copies the horizontal."""
        horizontal = self.aperture.radius or self.aperture.horizontal_size or 0.0
        vertical = self.aperture.radius or self.aperture.vertical_size or horizontal
        return horizontal, vertical

    def _write_astra_common(self, dic: dict) -> dict:
        """
        Creates the part of the ASTRA element dictionary common to all apertures in ASTRA

        Parameters
        ----------
        dic: dict
            Dictionary containing the parameters for the aperture

        Returns
        -------
        dict
            ASTRA dictionary with parameters and values
        """
        if self.aperture.negative_extent is not None:
            dic["Ap_Z1"] = {"value": self.aperture.negative_extent, "default": 0}
            dic["a_pos"] = {"value": self.physical.start.z}
        else:
            dic["Ap_Z1"] = {"value": self.physical.start.z + self.dz, "default": 0}
        if self.aperture.positive_extent is not None:
            dic["Ap_Z2"] = {"value": self.aperture.positive_extent, "default": 0}
            dic["a_pos"] = {"value": self.physical.start.z}
        else:
            end = (
                self.physical.end.z + self.dz
                if self.physical.end.z >= (self.physical.start.z + 1e-3)
                else self.physical.start.z + self.dz + 1e-3
            )
            dic["Ap_Z2"] = {"value": end, "default": 0}
        ox, oy = self._offsets()
        dic["A_xoff"] = {"value": self.dx + ox, "default": 0, "type": "not_zero"}
        dic["A_yoff"] = {"value": self.dy + oy, "default": 0, "type": "not_zero"}
        dic["A_xrot"] = {
            "value": self._astra_rotation("x"),
            "default": 0,
            "type": "not_zero",
        }
        dic["A_yrot"] = {
            "value": self._astra_rotation("y"),
            "default": 0,
            "type": "not_zero",
        }
        dic["A_zrot"] = {
            "value": self._astra_rotation("z"),
            "default": 0,
            "type": "not_zero",
        }
        return dic

    def _write_astra_circular(self) -> dict:
        """
        Creates the part of the ASTRA element dictionary relevant to circular apertures in ASTRA

        Returns
        -------
        dict
            ASTRA dictionary with parameters and values
        """
        dic = dict()
        dic["File_Aperture"] = {"value": "RAD"}
        if self.aperture.radius is not None:
            radius = self.aperture.radius
        elif self.aperture.horizontal_size > 0 and self.aperture.vertical_size > 0:
            radius = min([self.aperture.horizontal_size, self.aperture.vertical_size])
        elif self.aperture.horizontal_size > 0:
            radius = self.aperture.horizontal_size
        elif self.aperture.vertical_size > 0:
            radius = self.aperture.vertical_size
        else:
            radius = 1
        if (
            self.aperture.radius is None
            and self.aperture.horizontal_size > 0
            and self.aperture.vertical_size > 0
            and self.aperture.horizontal_size != self.aperture.vertical_size
        ):
            warn(
                f"ASTRA has no elliptical aperture (its aperture file is a radius "
                f"against z): {self.name!r} is written as a circle of the smaller "
                f"half axis, {radius} m."
            )
        dic["Ap_R"] = {"value": 1e3 * radius}
        return self._write_astra_common(dic)

    def _write_astra_planar(self, plane, width) -> dict:
        """
        Creates the ASTRA element dictionary for one plane of a planar aperture.

        Parameters
        ----------
        plane: str
            ASTRA ``File_Aperture`` value, ``"Col_X"`` or ``"Col_Y"``
        width: float
            Aperture half-width written as ``Ap_R`` [mm]

        Returns
        -------
        dict
            ASTRA dictionary with parameters and values
        """
        dic = dict()
        dic["File_Aperture"] = {"value": plane}
        dic["Ap_R"] = {"value": width}
        return self._write_astra_common(dic)

    def to_astra(self, n: int = 0, **kwargs: dict) -> str:
        """
        Writes the aperture element string for ASTRA

        Parameters
        ----------
        n: int
            Element index number
        **kwargs: dict
            Keyword args

        Returns
        -------
        str
            String representation of the element for ASTRA

        Raises
        ------
        ValueError
            If `shape` is not in the list of allowed values.
        """
        self.start_write()
        self.aperture.number_of_elements = 0
        if self.aperture.shape in ["elliptical", "circular"]:
            self.aperture.number_of_elements += 1
            dic = self._write_astra_circular()
            return self._write_astra_dictionary(dic, n)
        elif self.aperture.shape in ["planar", "rectangular"]:
            text = ""
            if (
                self.aperture.horizontal_size is not None
                and self.aperture.horizontal_size > 0
            ):
                dic = self._write_astra_planar(
                    "Col_X", 1e3 * self.aperture.horizontal_size
                )
                text += self._write_astra_dictionary(dic, n)
                self.aperture.number_of_elements += 1
            if (
                self.aperture.vertical_size is not None
                and self.aperture.vertical_size > 0
            ):
                dic = self._write_astra_planar(
                    "Col_Y", 1e3 * self.aperture.vertical_size
                )
                if self.aperture.number_of_elements > 0:
                    self.aperture.number_of_elements += 1
                    n = n + 1
                    text += "\n"
                text += self._write_astra_dictionary(dic, n)
            return text
        elif self.aperture.shape == "scraper":
            text = ""
            if (
                self.aperture.horizontal_size is not None
                and self.aperture.horizontal_size > 0
            ):
                dic = self._write_astra_planar(
                    "Scr_X", 1e3 * self.aperture.horizontal_size
                )
                text += self._write_astra_dictionary(dic, n)
                self.aperture.number_of_elements += 1
            if (
                self.aperture.vertical_size is not None
                and self.aperture.vertical_size > 0
            ):
                dic = self._write_astra_planar(
                    "Scr_Y", 1e3 * self.aperture.vertical_size
                )
                if self.aperture.number_of_elements > 0:
                    self.aperture.number_of_elements += 1
                    n = n + 1
                    text += "\n"
                text += self._write_astra_dictionary(dic, n)
            return text
        else:
            raise ValueError(
                "shape must be in ['elliptical', 'planar', 'circular', 'rectangular', 'scraper']"
            )

    def to_elegant(self) -> str:
        """
        Generates a string representation of the object's properties in the Elegant format.

        Returns
        -------
        str
            A formatted string representing the object's properties in Elegant format.
        """
        self.start_write()
        etype = self._convert_type_elegant(self.hardware_type)
        horizontal, vertical = self._half_sizes()
        ox, oy = self._offsets()
        # elegant's DX/DY move the collimator, which is the aperture offset too
        overrides = {
            "x_max": horizontal,
            "y_max": vertical,
            "dx": self.dx + ox,
            "dy": self.dy + oy,
        }
        terms = [
            f"{key} = {self._flag(value)}"
            for key, value in self._dump_items(
                self._convert_keyword_elegant,
                elements_elegant[etype],
                overrides=overrides,
            )
        ]
        return elegant_line(self.name + ": " + etype, terms)

    def _opal_alignment(self) -> Dict[str, float]:
        """The OPAL alignment with the aperture offset added, plus the sizes and
        the length: OPAL removes only the particles it finds inside a
        collimator's length, so a zero-length aperture gets a thin one."""
        alignment = super()._opal_alignment()
        horizontal, vertical = self._half_sizes()
        ox, oy = self._offsets()
        return alignment | {
            "dx": alignment["dx"] + ox,
            "dy": alignment["dy"] + oy,
            "xsize": horizontal,
            "ysize": vertical,
            "l": self.length or OPAL_THIN_APERTURE_LENGTH,
        }

    def to_ocelot(self) -> object:
        """An OCELOT ``Aperture``, or a drift between two for a thick element."""
        from ocelot.cpbd.elements import Aperture, Drift

        self.start_write()
        horizontal, vertical = self._half_sizes()
        ox, oy = self._offsets()

        def aperture(eid):
            # OCELOT's dx/dy place the aperture centre: offset plus misalignment
            return Aperture(
                xmax=horizontal or math.inf,
                ymax=vertical or math.inf,
                dx=self.dx + ox,
                dy=self.dy + oy,
                type="ellipt" if self._elliptical else "rect",
                eid=eid,
            )

        if not self.length:
            return aperture(self.name)
        return [
            aperture(f"{self.name}_entry"),
            Drift(l=self.length, eid=self.name),
            aperture(f"{self.name}_exit"),
        ]

    def to_cheetah(self) -> object:
        """A Cheetah ``Aperture``, or a drift between two for a thick element."""
        from cheetah.accelerator import Aperture, Drift, Segment
        from torch import float64, tensor

        self.start_write()
        self._warn_dropped_offset("Cheetah")
        horizontal, vertical = self._half_sizes()

        def aperture(name):
            return Aperture(
                x_max=tensor(horizontal or math.inf, dtype=float64),
                y_max=tensor(vertical or math.inf, dtype=float64),
                shape="elliptical" if self._elliptical else "rectangular",
                name=name,
                sanitize_name=True,
                dtype=float64,
            )

        if not self.length:
            return aperture(self.name)
        drift = Drift(
            length=tensor(self.length, dtype=float64),
            name=f"{self.name}_drift",
            sanitize_name=True,
            dtype=float64,
        )
        return Segment(
            elements=[
                aperture(f"{self.name}_entry"),
                drift,
                aperture(f"{self.name}_exit"),
            ],
            name=self.name,
            sanitize_name=True,
        )

    def to_xsuite(self, beam_length: int) -> tuple | list:
        """An Xtrack limit, or a drift between two for a thick element."""
        import xtrack as xt

        self.start_write()
        horizontal, vertical = self._half_sizes()
        if self.aperture.shape == "planar":
            # a slit: the unsized plane stays open rather than copying the other
            vertical = self.aperture.vertical_size
        ox, oy = self._offsets()
        # an unset plane is open; 1e10 is xtrack's own "unlimited"
        horizontal, vertical = horizontal or 1e10, vertical or 1e10
        if self._elliptical:
            component = xt.LimitEllipse
            properties = {"a": horizontal, "b": vertical, "shift_x": ox, "shift_y": oy}
        else:
            component = xt.LimitRect
            properties = {
                "min_x": ox - horizontal,
                "max_x": ox + horizontal,
                "min_y": oy - vertical,
                "max_y": oy + vertical,
            }
        if not self.length:
            return self.name, component, properties
        return [
            (f"{self.name}_entry", component, dict(properties)),
            (self.name, xt.Drift, {"length": self.length}),
            (f"{self.name}_exit", component, dict(properties)),
        ]

    def to_bdsim(
        self,
        section_aperture: Dict | None = None,
        charge_sign: int | float = 1,
        integrator_set: str = "bdsimmatrix",
    ) -> object:
        """
        Generates a BDSIM object based on the element's properties and type.

        Parameters
        ----------
        section_aperture: dict, optional
                Dictionary containing aperture information for the section,
                which may be used to set the aperture of the BDSIM element.
        charge_sign: int or float, optional
                Beam particle charge sign; unused here.
        integrator_set: str, optional
                BDSIM ``integratorSet`` option; unused here.

        Returns
        -------
        object
            BDSIM object
        """
        from ..conversion_rules.codes import bdsim_conversion

        def get_bdsim_drift(name) -> object:
            if self.verbose:
                warn(
                    f"Aperture type not defined for {name} or not provided for BDSIM; setting as drift"
                )
            from pybdsim.Builder import Drift as Drift_BDSIM

            return Drift_BDSIM

        type_conversion_rules_bdsim = bdsim_conversion.bdsim_conversion_rules
        if self.hardware_type in type_conversion_rules_bdsim:
            if hasattr(self, "aperture"):
                if self.aperture.shape in ["elliptical", "circular"]:
                    from pybdsim.Builder import ECol

                    obj = ECol
                elif self.aperture.shape in ["planar", "rectangular"]:
                    from pybdsim.Builder import RCol

                    obj = RCol
                elif self.aperture.shape == "scraper":
                    from pybdsim.Builder import JCol

                    obj = JCol
                else:
                    obj = get_bdsim_drift(self.name)
            else:
                obj = get_bdsim_drift(self.name)
        else:
            obj = get_bdsim_drift(self.name)
        material = self.material or getattr(
            getattr(self, "aperture", None), "material", None
        )
        if obj.__name__ in ("ECol", "RCol", "JCol") and not material:
            warn(
                f"{self.name} has no material, which a BDSIM collimator needs; writing a drift with its aperture"
            )
            from pybdsim.Builder import Drift

            obj = Drift
        keywords = self._bdsim_keywords(obj, section_aperture)
        if obj.__name__ in ("ECol", "RCol", "JCol"):
            keywords["material"] = material
            keywords["xsize"] = (
                self.aperture.radius or self.aperture.horizontal_size or 0.0
            )
            keywords["ysize"] = (
                self.aperture.radius or self.aperture.vertical_size or 0.0
            )
            if obj.__name__ != "JCol" and not keywords["ysize"]:
                keywords["ysize"] = keywords["xsize"]  # round, or square
        return obj(
            **self._bdsim_charge_sign(obj, keywords, charge_sign, integrator_set)
        )


class TargetTranslator(BaseElementTranslator):
    """A block of material in the beam: BDSIM's ``target``; a drift elsewhere."""

    target: TargetElement | None = None

    def to_bdsim(
        self,
        section_aperture: Dict | None = None,
        charge_sign: int | float = 1,
        integrator_set: str = "bdsimmatrix",
    ) -> object:
        """
        BDSIM ``target``: ``l`` and ``material``, its full transverse size as
        ``horizontalWidth`` and, for a round block, ``apertureType="circular"``
        (which is all that keyword means for a target: its outer shape).

        Parameters
        ----------
        section_aperture: dict, optional
            Unused: the beam pipe's aperture is not the block's shape.
        charge_sign: int or float, optional
            Unused.
        integrator_set: str, optional
            Unused.

        Returns
        -------
        object
            BDSIM object
        """
        from ..conversion_rules.codes.bdsim_conversion import Target as TargetBDSIM

        if not self.material:
            raise ValueError(f"Target {self.name} has no material, which BDSIM needs")
        keywords = self._bdsim_keywords(TargetBDSIM, None)
        for key in [
            k for k in keywords if k.startswith("aper") or k == "beampipeMaterial"
        ]:
            del keywords[key]
        keywords.pop("apertureType", None)
        target = self.target or TargetElement()
        if target.transverse_size:
            keywords["horizontalWidth"] = target.transverse_size
        if target.circular:
            keywords["apertureType"] = "circular"
        return TargetBDSIM(**keywords)


class CrystalTranslator(BaseElementTranslator):
    """A bent crystal centred on the beam: BDSIM's ``crystalcol``; a drift elsewhere."""

    crystal: CrystalElement | None = None

    def to_bdsim(
        self,
        section_aperture: Dict | None = None,
        charge_sign: int | float = 1,
        integrator_set: str = "bdsimmatrix",
    ) -> list:
        """
        A gmad ``crystal`` definition and the ``crystalcol`` holding it.

        The crystal is centred on the beam axis (the collimator's half gap is minus half
        its width) and turned by half its bending angle, which aligns its planes with
        the beam at its entrance, plus :attr:`entrance_angle`.

        Parameters
        ----------
        section_aperture: dict, optional
            Unused: the container is sized to the crystal.
        charge_sign: int or float, optional
            Unused.
        integrator_set: str, optional
            Unused.

        Returns
        -------
        list
            ``[pybdsim.Builder.Crystal, pybdsim.Builder.CrystalCol]``; the section adds
            the first as an object and the second to the line.
        """
        import math
        import os

        from pybdsim.Builder import Crystal as CrystalBDSIM
        from pybdsim.Builder import CrystalCol

        from ..utils.functions import expand_substitution

        crystal = self.crystal or CrystalElement()
        if not self.material:
            raise ValueError(f"Crystal {self.name} has no material, which BDSIM needs")
        if not crystal.data_file:
            raise ValueError(
                f"Crystal {self.name} has no channelling data_file, which BDSIM needs"
            )
        data = expand_substitution(self, crystal.data_file, self.master_lattice or "./")
        if not os.path.isabs(data) and self.master_lattice:
            data = os.path.join(self.master_lattice, data)
        angle = crystal.bending_angle / 2 + crystal.entrance_angle
        thickness = (self.length - 2e-9 - 1e-8) / (1 + abs(math.tan(angle)))
        if thickness <= 0:
            raise ValueError(
                f"Crystal {self.name} is too short ({self.length} m) to model"
            )
        a, b, c = crystal.lattice_constants or [SILICON_LATTICE_CONSTANT] * 3
        alpha, beta, gamma = crystal.lattice_angles or [math.pi / 2] * 3
        name = sanitize_string(self.name)
        definition = CrystalBDSIM(
            f"{name}_crystal",
            material=self.material,
            data=os.path.abspath(data),
            shape="box",
            lengthX=crystal.horizontal_size,
            lengthY=crystal.vertical_size,
            lengthZ=thickness,
            sizeA=a,
            sizeB=b,
            sizeC=c,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            spaceGroup=crystal.space_group,
            bendingAngleYAxis=crystal.bending_angle,
            bendingAngleZAxis=0,
        )
        keywords = self._bdsim_keywords(CrystalCol, None)
        for key in [
            k for k in keywords if k.startswith("aper") or k == "beampipeMaterial"
        ]:
            del keywords[key]
        keywords.update(
            xsize=-crystal.horizontal_size / 2,
            material=self.material,
            crystalLeft=f"{name}_crystal",
            crystalAngleYAxisLeft=angle,
            apertureType="rectangular",
            aper1=crystal.horizontal_size,
            aper2=crystal.vertical_size,
        )
        return [definition, CrystalCol(**keywords)]
