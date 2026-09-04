import logging
import os
import numpy as np
from typing import List, Dict, Any, Union, Literal, Optional
from pydantic import field_validator, BaseModel, ValidationInfo, Field, PositiveInt
from warnings import warn
from yaml import safe_load
from ._functions import read_yaml
from .element import baseElement, Drift, PhysicalBaseElement, Diagnostic
from .physical import PhysicalElement, Position, Rotation
from .trajectory import Trajectory
from ..utils.rotation_matrix import euler_angles_to_rotation_matrix, rotation_matrix_to_euler
from .baseModels import (
    ModelBase,
    set_functional_definitions,
    set_resolve_functional,
    validate_functional_references,
)
from .exceptions import LatticeError
import warnings

from .simulation import DriftSimulationElement

_log = logging.getLogger("laura.model")

LatticeType = Literal["beam", "rf", "laser"]
ALLOWED_LATTICE_TYPES = {"beam", "rf", "laser"}


def normalise_lattice_type(
    lattice_type: str | None,
    *,
    context: str,
    default: LatticeType = "beam",
) -> LatticeType:
    """Validate and normalise lattice type labels across model layers."""
    if lattice_type is None:
        return default
    if not isinstance(lattice_type, str):
        raise TypeError(f"{context} type must be a string")

    value = lattice_type.strip().lower()
    if value not in ALLOWED_LATTICE_TYPES:
        allowed = ", ".join(sorted(ALLOWED_LATTICE_TYPES))
        raise ValueError(f"{context} type must be one of: {allowed}")

    return value


def load_functional_definitions(
    value: Union[str, Dict, None], master_lattice: str | None = None
) -> Dict[str, Union[int, float]]:
    """
    Resolve a ``functional_definitions`` specification into a plain dict.

    The specification may be given directly as a mapping of names to numbers
    (e.g. ``{"quad1_k1l": -2, "cav1_phase": 90}``), or as a path to a YAML file
    holding such a mapping. The YAML may either be a flat mapping or nest the
    mapping under a top-level ``functional_definitions`` key. Paths are resolved
    relative to the working directory, then ``master_lattice``, then the package
    directory (mirroring how :class:`MachineModel` resolves its layout/section
    files).

    Parameters
    ----------
    value: str | dict | None
        The specification to resolve.
    master_lattice: str | None
        Optional base directory used to resolve a relative path.

    Returns
    -------
    Dict[str, Union[int, float]]
        The resolved functional definitions (empty if ``value`` is None/empty).
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        path = value
        if not os.path.exists(path) and master_lattice:
            candidate = os.path.join(master_lattice, value)
            if os.path.exists(candidate):
                path = candidate
        if not os.path.exists(path):
            candidate = os.path.abspath(os.path.dirname(__file__) + "/../" + value)
            if os.path.exists(candidate):
                path = candidate
        if not os.path.exists(path):
            raise ValueError(f"functional_definitions file {value} does not exist")
        with open(path, "r") as f:
            data = safe_load(f)
        if isinstance(data, dict) and "functional_definitions" in data:
            data = data["functional_definitions"]
        return data or {}
    raise ValueError("functional_definitions must be a path, dict, or None")


def dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def chunks(li, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(li), n):
        yield li[i: i + n]


class BaseLatticeModel(ModelBase):
    """
    Base-level description for defining lattices. Allows dynamic extensibility via `append`, `remove` functions.

    This class should not be used for creating lattices from scratch; rather, use
    `laura.models.elementList.SectionLattice`, `laura.models.elementList.MachineLayout`.
    """

    name: str
    """Name of lattice model."""

    _basename: str

    master_lattice: str | None = None
    """Top-level directory containing lattice files."""

    functional_definitions: Union[str, Dict[str, Union[int, float]]] = {}
    """Functional definitions for the lattice, e.g.
    ``{"quad1_k1l": -2, "cav1_phase": 90}``, or a path to a YAML file holding
    such a mapping. Registered into the shared registry so that string-valued
    element parameters can be resolved to numbers on demand."""

    resolve_functional: bool = False
    """Global resolution mode. When False (default), functional attributes are
    rendered as their definition name (a string); when True they are presented as
    resolved numbers. See :func:`~laura.models.baseModels.set_resolve_functional`."""

    revolution_frequency: float | None = None
    """The ring's revolution frequency [Hz], if this lattice is (part of) a closed ring."""

    _functional_source: str | None = None

    def model_post_init(self, __context) -> None:
        self._functional_source = (
            self.functional_definitions
            if isinstance(self.functional_definitions, str)
            else None
        )
        self.functional_definitions = load_functional_definitions(
            self.functional_definitions, self.master_lattice
        )
        set_functional_definitions(self.functional_definitions)
        set_resolve_functional(self.resolve_functional)
        elements = getattr(self, "elements", None)
        if isinstance(elements, ElementList):
            validate_functional_references(
                [e for e in elements.list() if isinstance(e, baseElement)],
                self.functional_definitions,
                self._functional_source,
            )

    # def __add__(self, other: dict) -> dict:
    #     copy = getattr(self, self._basename).copy()
    #     copy.extend(other)
    #     return copy

    # def __radd__(self, other: dict) -> dict:
    #     copy = other.copy()
    #     copy.extend(getattr(self, self._basename))
    #     return copy

    # def __sub__(self, other):
    #     copy = getattr(self, self._basename).copy()
    #     if other in copy:
    #         del copy[other]
    #     return copy

    # def append(self, other: Any) -> None:
    #     if not isinstance(other, list):
    #         other = [other]
    #     super().__init__(name=self.name, elements=self + other)
    #     setattr(self, self._basename, self + other)

    # def remove(self, other: Any) -> None:
    #     if other in getattr(self, self._basename):
    #         copy = getattr(self, self._basename).copy()
    #         copy.remove(other)
    #         super().__init__(name=self.name, elements=copy)
    #         getattr(self, self._basename).remove(other)

    def __str__(self):
        return str({k: v.names() for k, v in getattr(self, self._basename).items()})

    def __repr__(self):
        return self.__str__()


class ElementList(ModelBase):
    """
    A container for an unordered dictionary of :class:`~laura.models.element.baseElement`.
    """

    elements: Dict[str, Union[baseElement, dict, None]]

    def __str__(self):
        return str([e["name"] if isinstance(e, dict) else e.name for e in self.elements.values()])

    def __getitem__(self, item: str) -> int:
        return self.elements[item]

    @property
    def names(self) -> list:
        return [e["name"] if isinstance(e, dict) else e.name for e in self.elements.values()]

    def index(self, element: Union[str, baseElement]):
        if isinstance(element, str):
            return list(self.elements.keys()).index(element)
        return list(self.elements.values()).index(element)

    def _get_attributes_or_none(self, a):
        data = {}
        for k, v in self.elements.items():
            if v is not None and hasattr(v, a):
                data.update({k: getattr(v, a)})
            else:
                data.update({k: None})
        return data

    def __getattr__(self, a):
        try:
            return super().__getattr__(a)
        except Exception:
            data = self._get_attributes_or_none(a)
            if all([isinstance(d, (Union[baseElement, None])) for d in data.values()]):
                return ElementList(elements=data)
            return data

    def list(self):
        return list(self.elements.values())


class SectionLattice(BaseLatticeModel):
    """
    A section of a lattice, consisting of a list of elements and their order along the beam path.
    """

    order: List[str]
    """Ordered list of element names."""

    elements: ElementList = Field(default_factory=ElementList)
    """Container for elements."""

    section_type: LatticeType = "beam"
    """Logical lattice type of this section (beam/rf/laser)."""

    # other_elements: ElementList = ElementList(elements={})
    # TODO should we put this back in?

    _basename: str = "elements"

    @field_validator("section_type", mode="before")
    @classmethod
    def validate_section_type(cls, value: str | None) -> LatticeType:
        return normalise_lattice_type(value, context="section")

    @field_validator("elements", mode="before")
    @classmethod
    def validate_elements(
        cls, elements: Union[List[Union[baseElement, dict]], ElementList], info: ValidationInfo
    ) -> ElementList:
        if isinstance(elements, list):
            elemdict = {}
            for e in elements:
                if isinstance(e, dict):
                    nm = e.get("name")
                else:
                    nm = e.name
                if nm:
                    elemdict[nm] = e

            # print([e for e in info.data['order'] if e not in elemdict.keys()])
            return ElementList(
                elements={
                    e: elemdict[e] for e in info.data["order"] if e in elemdict.keys()
                }
            )
        return elements

    #
    # @model_serializer(mode="plain")
    # def serialize(self) -> dict:
    #     data = self.__dict__.copy()
    #     data['elements'] = {"elements": {}}
    #     data['elements']["elements"] = {
    #         k: v.model_dump() for k, v in self.elements.elements.items()
    #     }
    #     return data

    @property
    def names(self) -> List:
        """List of element names.

        Returns
        -------
        List
            List of element names.
        """
        return self.elements.names

    def __str__(self):
        # return str(getattr(self, self._basename).__str__())
        return str(self.names)

    def __getitem__(self, item: Union[str, int]) -> BaseModel:
        if isinstance(item, int):
            return self.elements[self.names[item]]
        return self.elements[item]

    def __getattr__(self, a):
        try:
            return super().__getattr__(a)
        except Exception:
            return getattr(self.elements, a)

    def _get_all_elements(self) -> List:
        """
        Get a list of all the elements in order.

        Returns
        -------
        List
            Ordered list of elements.
        """
        return [self.elements[e] for e in self.order if e in self.elements.names]

    def createDrifts(
        self,
        csr_enable: bool = True,
        lsc_enable: bool = True,
        lsc_bins: PositiveInt = 20,
    ):
        """Insert drifts into a sequence of 'elements'"""
        positions = []
        originalelements = dict()
        elementno = 0
        newelements = dict()

        elements = self._get_all_elements()

        # if any([x != y for x, y in zip(elements[0].physical.start.model_dump(), [0, 0, 0])]):
        #     machine_area = elements[0].machine_area
        #     self.order.insert(0, "initial_marker")
        #     self.elements.elements.update(
        #         {
        #             "initial_marker": PhysicalBaseElement(
        #                 name="initial_marker",
        #                 hardware_class="Marker",
        #                 hardware_type="Marker",
        #                 machine_area=machine_area,
        #             )
        #         }
        #     )
        #     elements = self._get_all_elements()

        for elem in elements:
            if not elem.subelement:
                originalelements[elem.name] = elem
                if isinstance(elem, Diagnostic):
                    elem.physical.length = 0
                start = elem.physical.start.array
                end = elem.physical.end.array
                try:
                    start += elem.cavity.coupling_cell_length
                except Exception:
                    pass
                positions.append(start)
                positions.append(end)
        positions = positions[1:]
        positions.append(positions[-1])
        driftdata = list(
            zip(iter(list(originalelements.items())), list(chunks(positions, 2)))
        )

        for e, d in driftdata:
            newelements[e[0]] = e[1]
            if len(d) > 1:
                x1, y1, z1 = d[0]
                x2, y2, z2 = d[1]
                try:
                    length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
                    vector = dot((d[1] - d[0]), [0, 0, 1])
                except Exception as exc:
                    _log.error("Drift calculation error near element '%s': %s", e[0], exc)
                    _log.debug("Position data: %s", d)
                    raise exc
                if round(length, 16) > 0:
                    elementno += 1
                    name = self.name + "_drift_" + str(elementno)
                    x, y, z = [(a + b) / 2.0 for a, b in zip(d[0], d[1])]
                    newdrift = Drift(
                        name=name,
                        hardware_class="Drift",
                        machine_area=newelements[e[0]].machine_area,
                        physical=PhysicalElement(
                            length=abs(round(np.copysign(length, vector), 16)),
                            middle=Position(x=x, y=y, z=z),
                            datum=Position(x=x, y=y, z=z),
                        ),
                        simulation=DriftSimulationElement(
                            csr_enable=csr_enable,
                            lsc_enable=lsc_enable,
                            lsc_bins=lsc_bins,
                        ),
                    )
                    newelements[name] = newdrift
        return newelements

    def get_s_values(
        self, as_dict: bool = False, at_entrance: bool = False, starting_s: float = 0
    ) -> list | dict:
        """
        Get the S values for the elements in the lattice.
        This method calculates the cumulative length of the elements in the lattice,
        starting from the entrance or the first element, depending on the `at_entrance` parameter.
        It returns a list or dict of S values, which represent the positions of the elements along the lattice.

        Parameters
        ----------
        as_dict: bool, optional
            If True, returns a dictionary with element names as keys and their S values as values.
        at_entrance: bool, optional
            If True, calculates S values starting from the entrance of the lattice.
            If False, calculates S values starting from the first element.
        starting_s: float, optional
            Initial s position

        Returns
        -------
        list | dict
            A list or dictionary of S values for the elements in the lattice.
            If `as_dict` is True, returns a dictionary with element names as keys and their S values as values.
            If `as_dict` is False, returns a list of S values.
        """
        elems = self.createDrifts()
        s = [starting_s]
        for e in list(elems.values()):
            s.append(s[-1] + e.physical.length)
        s = s[:-1] if at_entrance else s[1:]
        if as_dict:
            return dict(zip([e.name for e in elems.values()], s))
        return list(s)

    def get_resolved_s_values(
        self, as_dict: bool = False, at_entrance: bool = False
    ) -> list | dict:
        """
        Get true arc-length S values for the elements in the lattice, sourced
        from the resolved :class:`~laura.models.trajectory.Trajectory` built by
        :meth:`resolve_positions` (bend-aware, ``reference_placement``-aware).

        Unlike :meth:`get_s_values` (a naive cumulative sum of element lengths),
        this reads each element's already-resolved ``physical.s`` directly, and
        projects synthetic drift elements (created by :meth:`createDrifts`,
        which never get ``physical.s`` set) onto the nearest sibling's
        trajectory via :meth:`~laura.models.trajectory.Trajectory.s_at_xyz`.

        Falls back to :meth:`get_s_values` if no element in the section carries
        a resolved trajectory (i.e. ``resolve_positions`` was never run).

        Parameters
        ----------
        as_dict: bool, optional
            If True, returns a dictionary with element names as keys and their
            S values as values.
        at_entrance: bool, optional
            If True, returns each element's S value at its start rather than
            its middle.

        Returns
        -------
        list | dict
            A list or dictionary of resolved S values for the elements in the
            lattice, in the same order as :meth:`createDrifts`.
        """
        elems = self.createDrifts()

        traj = None
        for e in elems.values():
            phys = getattr(e, "physical", None)
            t = getattr(phys, "_trajectory", None) if phys is not None else None
            if t is not None:
                traj = t
                break
        if traj is None:
            return self.get_s_values(as_dict=as_dict, at_entrance=at_entrance)

        svals = []
        for e in elems.values():
            phys = e.physical
            if phys.s is not None:
                s_mid = phys.s
            else:
                s_mid = traj.s_at_xyz(phys.middle)
            svals.append(s_mid - phys.length / 2.0 if at_entrance else s_mid)

        if as_dict:
            return dict(zip([e.name for e in elems.values()], svals))
        return svals

    # ── s-coordinate support ───────────────────────────────────────────────────

    def _detect_coordinate_system(self, element_registry: dict) -> str:
        """Return ``'s'``, ``'global'``, or ``'reference'`` for this section.

        An element is treated as *pending-s* only when ``s`` is set but
        ``middle`` is still ``None`` (i.e., not yet resolved).  Elements that
        already have both ``s`` and ``middle`` (e.g. after a round-trip) are
        treated as global.  This avoids false positives when a pre-resolved
        model is reconstructed alongside elements using explicit xyz.

        Raises :exc:`ValueError` if pending-s and explicit-xyz elements are
        mixed (``reference_placement``-only elements are always allowed).
        """
        has_global = False
        has_s_pending = False
        for name in self.order:
            elem = element_registry.get(name)
            if elem is None or not hasattr(elem, "physical") or elem.physical is None:
                continue
            phys = elem.physical
            if phys.reference_placement is not None:
                continue
            if phys.s is not None and phys.middle is None:
                has_s_pending = True
            elif phys.middle is not None:
                has_global = True
        if has_s_pending and has_global:
            raise ValueError(
                f"Section '{self.name}': cannot mix s-coordinate and global-coordinate "
                "positioning.  All positioned elements must use the same system."
            )
        return "s" if has_s_pending else ("global" if has_global else "reference")

    def _resolve_s_coordinates(self, element_registry: dict) -> Optional[Trajectory]:
        """Integrate the design orbit and place all s-specified elements.

        Elements are sorted by their s_start value and placed sequentially.
        Straight-line drifts fill any gaps between elements.  For bent elements
        the arc geometry from ``_physical_angle`` is used.

        Returns the :class:`~laura.models.trajectory.Trajectory` built during
        integration, or ``None`` if there are no s-specified elements.
        """
        s_elems = [
            element_registry[n]
            for n in self.order
            if element_registry.get(n) is not None
            and hasattr(element_registry[n], "physical")
            and element_registry[n].physical is not None
            and element_registry[n].physical.s is not None
            and element_registry[n].physical.middle is None
        ]
        if not s_elems:
            return None

        def _s_start(elem: object) -> float:
            phys = elem.physical
            s, L, pt = phys.s, phys.length, phys.s_point
            if pt == "middle":
                return s - L / 2.0
            if pt == "end":
                return s - L
            return s  # 'start'

        s_elems_sorted = sorted(s_elems, key=_s_start)

        current_s = 0.0
        current_pos = np.zeros(3)
        current_R = np.eye(3)

        s_list: list[float] = [0.0]
        pos_list: list[np.ndarray] = [np.zeros(3)]
        rot_list: list[np.ndarray] = [np.eye(3)]

        for elem in s_elems_sorted:
            phys = elem.physical
            L = phys.length
            angle = phys._physical_angle
            s_elem_start = _s_start(elem)
            s_elem_end = s_elem_start + L

            # Drift to element entry
            if s_elem_start > current_s + 1e-12:
                drift = s_elem_start - current_s
                current_pos = current_pos + current_R @ np.array([0.0, 0.0, drift])
                current_s = s_elem_start
                s_list.append(current_s)
                pos_list.append(current_pos.copy())
                rot_list.append(current_R.copy())

            # Compute middle and end positions
            if abs(angle) < 1e-9:
                mid_pos = current_pos + current_R @ np.array([0.0, 0.0, L / 2.0])
                end_pos = current_pos + current_R @ np.array([0.0, 0.0, L])
                exit_R = current_R.copy()
            else:
                # Arc in the bend plane using LAURA's Ry(-angle) convention.
                rho = L / angle
                half = angle / 2.0
                local_mid = np.array([rho * (1.0 - np.cos(half)), 0.0, rho * np.sin(half)])
                local_end = np.array([rho * (1.0 - np.cos(angle)), 0.0, rho * np.sin(angle)])
                mid_pos = current_pos + current_R @ local_mid
                end_pos = current_pos + current_R @ local_end
                ct, st = np.cos(angle), np.sin(angle)
                ry_neg = np.array([[ct, 0.0, st], [0.0, 1.0, 0.0], [-st, 0.0, ct]])
                exit_R = current_R @ ry_neg

            # Set world-frame middle on the element
            phys.middle = Position.from_list(mid_pos.tolist())

            # Inherit trajectory orientation when no explicit rotation given
            if "rotation" not in phys.model_fields_set:
                yaw, pitch, roll = rotation_matrix_to_euler(current_R)
                phys.rotation = Rotation(theta=yaw, phi=pitch, psi=roll)
                phys.global_rotation = Rotation(theta=0.0, phi=0.0, psi=0.0)
                phys._rotation_matrix_cache = None

            s_list.extend([s_elem_start + L / 2.0, s_elem_end])
            pos_list.extend([mid_pos, end_pos])
            rot_list.extend([current_R.copy(), exit_R])

            current_pos = end_pos
            current_R = exit_R
            current_s = s_elem_end

        return Trajectory(np.array(s_list), np.array(pos_list), np.array(rot_list))

    def _build_trajectory_and_assign_s(self, element_registry: dict) -> Optional[Trajectory]:
        """Build a :class:`~laura.models.trajectory.Trajectory` from all resolved elements.

        Walks elements in section order, traces the arc-length through start /
        middle / end of each element, assigns the arc-length ``s`` value (at
        middle) back onto each element's physical block, and attaches the
        trajectory as ``phys._trajectory`` for bidirectional sync.
        """
        s_list: list[float] = [0.0]
        pos_list: list[np.ndarray] = [np.zeros(3)]
        rot_list: list[np.ndarray] = [np.eye(3)]

        current_s = 0.0
        prev_end: Optional[np.ndarray] = None

        elements_to_wire: list[PhysicalElement] = []

        for name in self.order:
            elem = element_registry.get(name)
            if elem is None or not hasattr(elem, "physical") or elem.physical is None:
                continue
            phys = elem.physical
            if phys.middle is None:
                continue
            try:
                start = phys.start
                start_arr = np.array([start.x, start.y, start.z])
            except RuntimeError:
                continue

            gap = float(np.linalg.norm(start_arr - prev_end)) if prev_end is not None else float(np.linalg.norm(start_arr))
            s_elem_start = current_s + gap

            mid_arr = np.array([phys.middle.x, phys.middle.y, phys.middle.z])
            s_elem_mid = s_elem_start + phys.length / 2.0

            try:
                end = phys.end
                end_arr = np.array([end.x, end.y, end.z])
            except RuntimeError:
                end_arr = mid_arr
            s_elem_end = s_elem_start + phys.length

            s_list.extend([s_elem_start, s_elem_mid, s_elem_end])
            pos_list.extend([start_arr, mid_arr, end_arr])
            rot_list.extend([phys.rotation_matrix, phys.rotation_matrix, phys.end_rotation_matrix])

            # Assign s (bypasses sync since _trajectory not yet set)
            phys.s = s_elem_mid

            current_s = s_elem_end
            prev_end = end_arr
            elements_to_wire.append(phys)

        traj = Trajectory(np.array(s_list), np.array(pos_list), np.array(rot_list))
        for phys in elements_to_wire:
            phys._trajectory = traj
        return traj

    def resolve_positions(self, element_registry: dict) -> Optional[Trajectory]:
        """Resolve all positioning modes and build the section trajectory.

        Handles three positioning modes in order:

        1. ``reference_placement`` — resolved first (same as the original
           :meth:`resolve_reference_placements` method).
        2. ``s``-coordinate — the design orbit is integrated from s=0 at
           the global origin to place each element.
        3. Global xyz (``middle``) — already resolved; s-values and trajectory
           attachment are computed from the existing positions.

        Mixing s and explicit-xyz positioning raises :exc:`ValueError`.

        Returns the :class:`~laura.models.trajectory.Trajectory` for this
        section, or ``None`` if no physical elements are present.
        """
        coord_sys = self._detect_coordinate_system(element_registry)

        # Step 1: resolve reference_placements (unchanged logic)
        self.resolve_reference_placements(element_registry)

        # Step 2: resolve s-coordinates (integrates trajectory)
        traj: Optional[Trajectory] = None
        if coord_sys == "s":
            traj = self._resolve_s_coordinates(element_registry)

        # Step 3: build trajectory and assign s to all elements
        traj = self._build_trajectory_and_assign_s(element_registry)
        return traj

    # ── end s-coordinate support ───────────────────────────────────────────────

    def resolve_reference_placements(self, element_registry: dict) -> None:
        """Resolve any ``reference_placement`` specs in this section.

        Iterates elements in order and, for each one whose physical block
        carries a ``reference_placement``, computes the world-frame ``middle``
        position (and orientation) from the named reference element's frame.

        Parameters
        ----------
        element_registry:
            Mapping of element name → element object covering at minimum all
            elements that might be referenced.  Typically ``MachineModel.elements``.
        """
        for name in self.order:
            # Always operate on the registry object so mutations are visible
            # to the caller — section.elements may hold Pydantic-copied instances.
            elem = element_registry.get(name)
            if elem is None or not hasattr(elem, "physical"):
                continue
            phys = elem.physical
            if phys.reference_placement is None:
                continue

            rp = phys.reference_placement
            ref_name = rp.element
            if ref_name not in element_registry:
                raise ValueError(
                    f"reference_placement on '{name}' names element '{ref_name}' "
                    f"which does not exist in the element registry."
                )
            ref_elem = element_registry[ref_name]
            if not hasattr(ref_elem, "physical"):
                raise ValueError(
                    f"reference_placement on '{name}' names element '{ref_name}' "
                    f"which has no physical data."
                )
            ref_phys = ref_elem.physical

            # Reference point position and rotation matrix in world frame
            if rp.point == "end":
                ref_pos = ref_phys.end
                ref_R = ref_phys.end_rotation_matrix
            elif rp.point == "start":
                ref_pos = ref_phys.start
                ref_R = ref_phys.rotation_matrix   # entry frame = element rotation
            else:  # "middle"
                ref_pos = ref_phys.middle
                ref_R = ref_phys.rotation_matrix

            # Compute new world-frame middle position
            if rp.offset is not None:
                off = np.array([rp.offset.x, rp.offset.y, rp.offset.z])
                delta = ref_R @ off
            elif rp.world_offset is not None:
                delta = np.array([rp.world_offset.x, rp.world_offset.y, rp.world_offset.z])
            elif rp.s_offset is not None:
                # s_offset is a scalar along the local beam direction (z-axis of ref frame)
                delta = ref_R @ np.array([0.0, 0.0, rp.s_offset])
            else:
                delta = np.zeros(3)

            new_mid = np.array([ref_pos.x, ref_pos.y, ref_pos.z]) + delta

            # Clear reference_placement before writing middle — the model validator
            # (validate_assignment=True) re-runs on every field write, so both
            # fields must not be set at the same time.
            phys.reference_placement = None
            phys.middle = Position.from_list(new_mid)

            # Determine resolved rotation matrix
            if "rotation" not in phys.model_fields_set:
                # No user-specified rotation: inherit reference frame orientation
                resolved_R = ref_R
            else:
                # User-specified rotation is treated as an additional LOCAL rotation
                # on top of the reference frame: R_world = ref_R @ R_user_local
                ur = phys.rotation
                R_user = euler_angles_to_rotation_matrix(ur.theta, ur.phi, ur.psi)
                resolved_R = ref_R @ R_user

            yaw, pitch, roll = rotation_matrix_to_euler(resolved_R)
            phys.rotation = Rotation(theta=yaw, phi=pitch, psi=roll)
            phys.global_rotation = Rotation(theta=0.0, phi=0.0, psi=0.0)
            phys._rotation_matrix_cache = None


class MachineLayout(BaseLatticeModel):
    """
    A machine layout, consisting of a dictionary of lattice sections.
    This class could represent a full beam path, for example.
    """

    sections: Dict[str, SectionLattice]  # = Field(frozen=True)
    """Dictionary of :class:`~laura.models.elementList.SectionLattice`, keyed by name."""

    master_lattice: str | None = None
    """Directory containing lattice files. """

    layout_type: LatticeType = "beam"
    """Logical lattice type of this path (beam/rf/laser)."""

    _basename: str = "sections"

    @field_validator("layout_type", mode="before")
    @classmethod
    def validate_layout_type(cls, value: str | None) -> LatticeType:
        return normalise_lattice_type(value, context="layout")

    @staticmethod
    def _normalise_type_filter(
        lattice_type: Union[str, list, None],
        *,
        context: str,
    ) -> set[LatticeType] | None:
        if lattice_type is None:
            return None

        if isinstance(lattice_type, str):
            return {normalise_lattice_type(lattice_type, context=context)}

        if isinstance(lattice_type, list):
            return {
                normalise_lattice_type(value, context=context)
                for value in lattice_type
            }

        raise TypeError(f"{context} filter must be a str or list[str]")

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self.functional_definitions = load_functional_definitions(
            self.functional_definitions, self.master_lattice
        )
        set_functional_definitions(self.functional_definitions)
        set_resolve_functional(self.resolve_functional)
        matrix = [v.elements.elements.values() for v in self.sections.values()]
        all_elems = [item for row in matrix for item in row]
        if len(all_elems) > 0:
            all_elems_reversed = reversed(all_elems)
            last_elem = all_elems[-1]
            if isinstance(last_elem, dict):
                superelem = last_elem.get("name")
                # Skip geometry correction for stub dicts
                return

            superelem = last_elem.name
            start_pos = last_elem.physical.start
            all_elem_corrected = []
            for elem in all_elems_reversed:
                if isinstance(elem, PhysicalBaseElement):
                    if not elem.is_subelement():
                        superelem = elem.name
                    all_elem_corrected += [elem]
                    start_pos = elem.physical.start
            self._all_elements = list(reversed(all_elem_corrected))
        else:
            self._all_elements = {}

    @property
    def names(self) -> List:
        """
        Names of lattice sections

        Returns
        -------
        List
            Names of :attr:`~sections`
        """
        return list(self.sections.keys())

    def __str__(self):
        return str([k for k, v in self.sections.items()])

    def __getattr__(self, item: str):
        return getattr(self.sections, item)

    def __getitem__(self, item: str) -> int:
        return self.sections[item]

    def _get_all_elements(self) -> List[baseElement]:
        """
        List of all elements defined in the layout

        Returns
        -------
        List[baseElement]
            List of all elements.
        """
        return self._all_elements

    def _get_all_element_names(self) -> List[str]:
        """
        List of all element names defined in the layout.

        Returns
        -------
        List[str]
            Names of all elements.
        """
        return [e.name for e in self._get_all_elements() if isinstance(e, PhysicalBaseElement)]

    def get_element(self, name: str) -> baseElement:
        """
        Return the LatticeElement object corresponding to a given machine element

        :param str name: Name of the element to look up
        :returns: :class:`~laura.models.element.baseElement` instance for that element
        """
        if name in self._get_all_element_names():
            index = self._get_all_element_names().index(name)
            return self._get_all_elements()[index]
        else:
            message = "Element %s does not exist along the beam path" % name
            raise LatticeError(message)

    def _get_element_names(self, lattice: list) -> list:
        """
        Return the name for each LatticeElement object in a list defining a lattice

        :param str lattice: List of LatticeElement objects representing machine hardware
        :returns: List of strings defining the names of the machine elements
        """
        return [ele.name for ele in lattice]

    def _lookup_index(self, name: str) -> int:
        """
        Look up the index of an element in a given lattice

        :param str name: Name of the element to search for
        :returns: List index of the item within that beam path
        """
        try:
            # fetch the index of the element
            return self._get_all_element_names().index(name)
        except ValueError:
            message = "Element %s does not exist along the beam path" % name
            raise LatticeError(message)

    @property
    def elements(self) -> List[str]:
        """
        List of all element names.

        Returns
        -------
        List[str]
            List of all element names.
        """
        return self._get_all_element_names()

    def _filter_element_list(self, result, filt, attrib):
        if isinstance(filt, (str, list)):
            # make list of valid types
            if isinstance(filt, str):
                filter_list = [filt.lower()]
            elif isinstance(filt, list):
                filter_list = [_type.lower() for _type in filt]
            # apply search criteria
            return [
                ele
                for ele in result
                if (
                    hasattr(ele, attrib)
                    and self._match_field_or_alias(ele, attrib, filter_list)
                )
            ]
        return result

    @staticmethod
    def _match_field_or_alias(ele, attrib, filter_list):
        """Check if a field's value or its alias matches the filter list."""
        value = getattr(ele, attrib, None)
        if value is not None and value.lower() in filter_list:
            return True
        # Also check field alias for the attribute
        field_info = type(ele).model_fields.get(attrib)
        if field_info is not None and field_info.alias is not None:
            if field_info.alias.lower() in filter_list:
                return True
        return False

    def get_all_elements(
        self,
        element_type: Union[str, list, None] = None,
        element_model: Union[str, list, None] = None,
        element_class: Union[str, list, None] = None,
        section_type: Union[str, list, None] = None,
    ) -> List[str]:
        """
        Get all elements in the lattice, or filter them by type/model/class
        # TODO function name implies this returns elements rather than names; rename?

        Parameters
        ----------
        element_type: str | list | None
            Filter by element type; if list, gather multiple types; if None, gather all.
        element_model: str | list | None
            Filter by element model; if list, gather multiple models; if None, gather all.
        element_class
            Filter by element hardware class; if list, gather multiple classes; if None, gather all.

        Returns
        -------
        List[str]
            Filtered names of elements.
        """
        return self.elements_between(
            end=None,
            start=None,
            element_type=element_type,
            element_class=element_class,
            element_model=element_model,
            section_type=section_type,
        )

    def elements_between(
        self,
        end: str = None,
        start: str = None,
        element_type: Union[str, list, None] = None,
        element_model: Union[str, list, None] = None,
        element_class: Union[str, list, None] = None,
        section_type: Union[str, list, None] = None,
    ) -> List[str]:
        """
        Returns a list of all lattice elements (of a specified type) between
        any two points along the accelerator (inclusive). Elements are ordered according
        to their longitudinal position along the beam path.

        Parameters
        ----------
        end: str
            Name of the element defining the end of the search region
        start: str
            Name of the element defining the start of the search region
        element_type: str | list | None
            Filter by element type; if list, gather multiple types; if None, gather all.
        element_model: str | list | None
            Filter by element model; if list, gather multiple models; if None, gather all.
        element_class
            Filter by element hardware class; if list, gather multiple classes; if None, gather all.

        Returns
        -------
        List[str]
            Filtered names of elements.
        """
        # replace blank start and/or end point
        element_names = self._get_all_element_names()
        if start is None:
            start = element_names[0]
        if end is None:
            end = element_names[-1]

        # truncate the list between the start and end elements
        first = self._lookup_index(start)
        last = self._lookup_index(end) + 1
        result = self._get_all_elements()[first:last]

        filtered_section_types = self._normalise_type_filter(
            section_type,
            context="section",
        )
        if filtered_section_types is not None:
            element_to_section = {
                element_name: section_name
                for section_name, section in self.sections.items()
                for element_name in section.names
            }
            allowed_sections = {
                name
                for name, section in self.sections.items()
                if section.section_type in filtered_section_types
            }
            result = [
                ele
                for ele in result
                if element_to_section.get(ele.name) in allowed_sections
            ]

        result = self._filter_element_list(result, element_type, "hardware_type")
        result = self._filter_element_list(result, element_model, "hardware_model")
        result = self._filter_element_list(result, element_class, "hardware_class")

        return self._get_element_names(result)


class MachineModel(ModelBase):
    """
    The full model of the accelerator. It describes all :class:`~laura.models.elementList.MachineLayout` and
    :class:`~laura.models.elementList.SectionLattice` that particles can follow.
    These layouts and sections are also defined as Dict[str, list] and Dict[str, list], and the full dictionary
    containing all elements is also accessible.
    """

    layout: str | Dict | None = None
    """Dictionary containing layout names and the names of the sections of which they are composed."""

    section: str | Dict[str, Dict] | None = None
    """Dictionary containing section names and the elements that compose it."""

    elements: Dict[str, baseElement] = {}
    """Dictionary containing all elements defined in the machine model."""

    sections: Dict[str, SectionLattice] = {}
    """Dictionary containing :class:`~laura.models.elementList.SectionLattice`, keyed by name."""

    lattices: Dict[str, MachineLayout] = {}
    """Dictionary containing :class:`~laura.models.elementList.MachineLayout`, keyed by name.
    #TODO rationalise either this name `lattices` or the class name `MachineLayout`.
    """

    master_lattice: str | None = None
    """Directory containing lattice YAML files."""

    functional_definitions: Union[str, Dict[str, Union[int, float]]] = {}
    """Mapping of functional-parameter names to their numeric values, or a path
    to a YAML file holding such a mapping. Resolved at construction and shared
    with every section, layout and element in the machine."""

    resolve_functional: bool = False
    """Whether functional parameters are rendered as resolved numbers rather
    than as their definition names."""

    _functional_source: str | None = None

    revolution_frequency: float | None = None
    """The ring's revolution frequency [Hz], if this machine is (part of) a closed ring."""

    _layouts: List[str] = None

    _layout_metadata: Dict[str, Dict[str, LatticeType]] = {}

    _section_definitions: Dict[str, Dict[str, Any]] = {}

    _default_path: str = None

    @staticmethod
    def _normalise_type_filter(
        lattice_type: Union[str, list, None],
        *,
        context: str,
    ) -> set[LatticeType] | None:
        if lattice_type is None:
            return None

        if isinstance(lattice_type, str):
            return {normalise_lattice_type(lattice_type, context=context)}

        if isinstance(lattice_type, list):
            return {
                normalise_lattice_type(value, context=context)
                for value in lattice_type
            }

        raise TypeError(f"{context} filter must be a str or list[str]")

    @staticmethod
    def _normalise_section_definitions(sections: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        normalised_sections = {}

        for section_name, section_data in sections.items():
            if isinstance(section_data, list):
                elements = section_data
                section_type = "beam"
            elif isinstance(section_data, dict):
                if "elements" not in section_data:
                    raise KeyError(
                        f"Section '{section_name}' must define an 'elements' list"
                    )
                elements = section_data["elements"]
                section_type = normalise_lattice_type(
                    section_data.get("type", section_data.get("section_type")),
                    context=f"section '{section_name}'",
                )
            else:
                raise TypeError(
                    f"Section '{section_name}' must be a list or dict"
                )

            if not isinstance(elements, list):
                raise TypeError(f"Section '{section_name}' elements must be a list")

            normalised_sections[section_name] = {
                "elements": elements,
                "type": section_type,
            }

        return normalised_sections

    @staticmethod
    def _normalise_layout_metadata(
        layout_metadata: Dict[str, Any] | None,
    ) -> Dict[str, Dict[str, LatticeType]]:
        if not layout_metadata:
            return {}

        normalised = {}
        for layout_name, metadata in layout_metadata.items():
            if isinstance(metadata, str):
                layout_type = metadata
            elif isinstance(metadata, dict):
                layout_type = metadata.get("type")
            else:
                raise TypeError(
                    f"layout_metadata['{layout_name}'] must be a string or dict"
                )

            normalised[layout_name] = {
                "type": normalise_lattice_type(
                    layout_type,
                    context=f"layout '{layout_name}'",
                )
            }

        return normalised

    @staticmethod
    def _section_elements_and_type(
        section_name: str,
        section_definition: Dict[str, Any],
    ) -> tuple[list[str], LatticeType]:
        if "elements" not in section_definition:
            raise KeyError(f"Section '{section_name}' is missing 'elements'")

        elements = section_definition["elements"]
        if not isinstance(elements, list):
            raise TypeError(f"Section '{section_name}' elements must be a list")

        section_type = normalise_lattice_type(
            section_definition.get("type"),
            context=f"section '{section_name}'",
        )
        return elements, section_type

    @field_validator("layout", mode="before")
    @classmethod
    def validate_layout(cls, v: str | dict) -> str | dict:
        if isinstance(v, str):
            if os.path.isfile(v):
                return v
            elif os.path.isfile(
                os.path.abspath(os.path.dirname(__file__) + "/../" + v)
            ):
                return os.path.abspath(os.path.dirname(__file__) + "/../" + v)
            else:
                # Not resolvable relative to the cwd or the laura package;
                # defer to model_post_init, which resolves the path relative
                # to master_lattice (the environment-independent anchor the
                # framework always supplies). Raising here would break any
                # environment where laura is not installed beside the lattice
                # files (e.g. laura in site-packages during testing).
                return v
        elif isinstance(v, dict):
            if "layouts" not in v:
                raise KeyError("layout must specify lines each with a list of sections")
            return v
        else:
            raise ValueError("layout must be a str or dict")

    @field_validator("section", mode="before")
    @classmethod
    def validate_section(cls, v: str | dict) -> str | dict:
        if isinstance(v, str):
            if os.path.isfile(v):
                return v
            elif os.path.isfile(
                os.path.abspath(os.path.dirname(__file__) + "/../" + v)
            ):
                return os.path.abspath(os.path.dirname(__file__) + "/../" + v)
            else:
                # Not resolvable relative to the cwd or the laura package;
                # defer to model_post_init, which resolves the path relative
                # to master_lattice (the environment-independent anchor the
                # framework always supplies). Raising here would break any
                # environment where laura is not installed beside the lattice
                # files (e.g. laura in site-packages during testing).
                return v
        elif isinstance(v, dict):
            if "sections" not in v:
                raise KeyError(
                    "section must specify sections each with lists of elements"
                )
            return v
        else:
            warnings.warn(
                "No sections specified. Sections will be generated from elements."
            )

    def model_post_init(self, __context):
        self._functional_source = (
            self.functional_definitions
            if isinstance(self.functional_definitions, str)
            else None
        )
        self.functional_definitions = load_functional_definitions(
            self.functional_definitions, self.master_lattice
        )
        set_functional_definitions(self.functional_definitions)
        set_resolve_functional(self.resolve_functional)
        if isinstance(self.layout, str):
            layout_file = self.layout
            if not os.path.exists(layout_file) and self.master_lattice:
                candidate = os.path.join(self.master_lattice, layout_file)
                if os.path.exists(candidate):
                    layout_file = candidate
            config = read_yaml(layout_file)
            self._layouts = config.layouts
            self._layout_metadata = self._normalise_layout_metadata(
                getattr(config, "layout_metadata", {})
            )
            try:
                self._default_path = config.default_layout
            except AttributeError:
                message = 'Missing "default_layout" in %s ' % layout_file
                warn(message)
        elif self.layout is None:
            self._layouts = {}
            self._layout_metadata = {}
            self._default_path = None
            warnings.warn("No layouts specified. Lattices will be empty.")
        else:
            for key in ["layouts"]:
                if key not in self.layout:
                    raise KeyError("layout must specify layouts")
            self._layouts = self.layout["layouts"]
            self._layout_metadata = self._normalise_layout_metadata(
                self.layout.get("layout_metadata", {})
            )
            if "default_layout" in self.layout:
                self._default_path = self.layout["default_layout"]
        if isinstance(self.section, str):
            section_file = self.section
            if not os.path.exists(section_file) and self.master_lattice:
                candidate = os.path.join(self.master_lattice, section_file)
                if os.path.exists(candidate):
                    section_file = candidate
            config = read_yaml(section_file)
            self._section_definitions = self._normalise_section_definitions(
                config.sections
            )
        elif self.section is None:
            self._section_definitions = {}
        else:
            if "sections" not in self.section:
                raise KeyError("section must specify sections with a list of sections")
            self._section_definitions = self._normalise_section_definitions(
                self.section["sections"]
            )
        if len(self.elements) > 0:
            # Validate functional references up-front (so the error names the
            # source file), skipping lazy element stores to avoid forcing a load.
            if not hasattr(self.elements, "get_metadata"):
                validate_functional_references(
                    [e for e in self.elements.values() if isinstance(e, baseElement)],
                    self.functional_definitions,
                    self._functional_source,
                )
            if self.section:
                self._build_layouts(self.elements)   # creates SectionLattice only
            else:
                self._build_sections_from_elements(self.elements)
            self._resolve_all_positions()             # resolve before MachineLayout
            if self.section:
                self._build_layout_objects()          # MachineLayout after positions ready

    def __add__(self, other) -> dict:
        copy = self.elements.copy()
        copy.update(other)
        return copy

    def __radd__(self, other) -> dict:
        copy = other.copy()
        copy.update(self.elements)
        return copy

    def __iter__(self) -> iter:
        return iter(self.elements)

    def __str__(self):
        return str(list(self.elements.keys()))

    def _index_elements(self, elements):
        by_area = {}
        by_name = {}

        # Optimized metadata lookup if it's a lazy dict
        if hasattr(elements, "get_metadata"):
            for name in elements.keys():
                is_loaded = getattr(elements, "is_loaded", lambda n: True)(name)
                if is_loaded:
                    elem = elements[name]
                    if elem is None:
                        continue
                    area = getattr(elem, "machine_area", None)
                    item_name = elem.name
                else:
                    meta = elements.get_metadata(name)
                    if meta is None:
                        continue
                    elem = meta
                    area = meta.get("machine_area")
                    item_name = meta.get("name")

                if item_name:
                    by_name[item_name] = elem
                if area:
                    by_area.setdefault(area, []).append(elem)
            return by_area, by_name

        # Standard indexing for other collections
        for elem in elements.values():
            if elem is None:
                continue
            if isinstance(elem, dict):
                area = elem.get("machine_area")
                name = elem.get("name")
            else:
                area = getattr(elem, "machine_area", None)
                name = elem.name

            if name:
                by_name[name] = elem

            if area:
                by_area.setdefault(area, []).append(elem)

        return by_area, by_name

    def append(self, values: dict) -> None:
        self.elements = values | self.elements
        self._build_sections_from_elements(self.elements)
        self._build_layouts(self.elements)

    def update(self, values: dict) -> None:
        return self.append(values)

    def __getitem__(
        self, item: str | list[str] | tuple[str]
    ) -> BaseModel | List[BaseModel]:
        if isinstance(item, (list, tuple)):
            return [self.elements[subitem] for subitem in item]
        return self.elements[item]

    def __setitem__(self, item: str, value: Any) -> None:
        super().__init__(elements=self + {item: value})

    @property
    def default_path(self) -> str:
        return self._default_path

    @default_path.setter
    def default_path(self, path: str):
        self._default_path = path

    def _build_sections_from_elements(self, elements):
        by_area, by_name = self._index_elements(elements)

        for area, new_elements in by_area.items():
            if area in self.sections:
                continue

            order = [
                e["name"] if isinstance(e, dict) else e.name
                for e in new_elements
            ]

            self.sections[area] = SectionLattice(
                name=area,
                elements=new_elements,
                order=order,
                section_type="beam",
                master_lattice=self.master_lattice,
                functional_definitions=self.functional_definitions,
                resolve_functional=self.resolve_functional,
            )

            if not self._section_definitions or area not in self._section_definitions:
                self._section_definitions[area] = {
                    "elements": order,
                    "type": "beam",
                }

        self.lattices = {}

    def _build_layouts(self, elements):
        """Build sections (and layout objects when no full-layout definitions exist)."""
        self._build_sections_phase(elements)
        # Layout objects (MachineLayout) require resolved positions so they are
        # deferred to _build_layout_objects(), called after _resolve_all_positions().

    def _build_sections_phase(self, elements):
        """Create all SectionLattice objects without yet creating MachineLayout objects."""
        by_area, by_name = self._index_elements(elements)

        if self._section_definitions and not self._layouts:
            # Sections only — no layout wrapper needed
            for area, section_definition in self._section_definitions.items():
                if area in self.sections:
                    continue
                elem_names, section_type = self._section_elements_and_type(
                    area,
                    section_definition,
                )
                new_elements = [
                    by_name[name]
                    for name in elem_names
                    if name in by_name
                ]
                _log.debug("Section %s elements=(%s)", area, [elem.name for elem in new_elements])
                self.sections[area] = SectionLattice(
                    name=area,
                    elements=new_elements,
                    order=elem_names,
                    section_type=section_type,
                    master_lattice=self.master_lattice,
                    functional_definitions=self.functional_definitions,
                    resolve_functional=self.resolve_functional,
                )
            return

        if self._layouts:
            for path, areas in self._layouts.items():
                for area in areas:
                    if area in self._section_definitions:
                        elem_names, section_type = self._section_elements_and_type(
                            area,
                            self._section_definitions[area],
                        )
                        new_elements = [
                            by_name[name]
                            for name in elem_names
                            if name in by_name
                        ]
                        _log.debug("Section %s elements=(%s)", area, [elem.name for elem in new_elements])
                        self.sections[area] = SectionLattice(
                            name=area,
                            elements=new_elements,
                            order=elem_names,
                            section_type=section_type,
                            master_lattice=self.master_lattice,
                            functional_definitions=self.functional_definitions,
                            resolve_functional=self.resolve_functional,
                        )

    def _build_layout_objects(self):
        """Create MachineLayout objects from already-resolved sections.

        Called after :meth:`_resolve_all_positions` so that element positions
        are available when :class:`MachineLayout` ``model_post_init`` runs.
        """
        if not self._layouts:
            return
        for path, areas in self._layouts.items():
            if path not in self.lattices:
                layout_type = self._layout_metadata.get(path, {}).get("type", "beam")
                self.lattices[path] = MachineLayout(
                    name=path,
                    sections={
                        area: self.sections[area]
                        for area in areas
                        if area in self.sections
                    },
                    layout_type=layout_type,
                    master_lattice=self.master_lattice,
                    functional_definitions=self.functional_definitions,
                    resolve_functional=self.resolve_functional,
                )
        if len(self.lattices) == 1 and self._default_path is None:
            self._default_path = next(iter(self.lattices))

    def _resolve_all_reference_placements(self) -> None:
        """Resolve reference_placement specs across all sections."""
        for section in self.sections.values():
            section.resolve_reference_placements(self.elements)

    def _resolve_all_positions(self) -> None:
        """Resolve all positioning modes (reference_placement, s, global) for every section."""
        for section in self.sections.values():
            section.resolve_positions(self.elements)

    def resolve_reference_placements(self) -> None:
        """(Re-)resolve all reference_placement and s-coordinate specs.

        Called automatically during construction.  Exposed publicly so that
        callers who build the model incrementally can trigger a re-resolution
        after adding new elements.
        """
        self._resolve_all_positions()

    def resolve_positions(self) -> None:
        """Re-resolve all positioning modes and rebuild section trajectories.

        Equivalent to :meth:`resolve_reference_placements` but with a more
        descriptive name.  Handles ``reference_placement``, ``s``-coordinates,
        and global-xyz elements in one pass.
        """
        self._resolve_all_positions()

    def get_element(self, name: str) -> baseElement:
        """
        Return the LatticeElement object corresponding to a given machine element

        :param str name: Name of the element to look up
        :returns: LatticeElement instance for that element
        """
        if name in self.elements:
            return self.elements[name]
        else:
            message = (
                "Element %s does not exist anywhere in the accelerator lattice" % name
            )
            raise LatticeError(message)

    def get_all_elements(
        self,
        element_type: Union[str, list, None] = None,
        element_model: Union[str, list, None] = None,
        element_class: Union[str, list, None] = None,
        section_type: Union[str, list, None] = None,
    ) -> List[str]:
        """
        Get all elements in the lattice, or filter them by type/model/class
        # TODO function name implies this returns elements rather than names; rename?

        Parameters
        ----------
        element_type: str | list | None
            Filter by element type; if list, gather multiple types; if None, gather all.
        element_model: str | list | None
            Filter by element model; if list, gather multiple models; if None, gather all.
        element_class
            Filter by element hardware class; if list, gather multiple classes; if None, gather all.

        Returns
        -------
        List[str]
            Filtered names of elements.
        """
        return self.elements_between(
            end=None,
            start=None,
            element_type=element_type,
            element_class=element_class,
            element_model=element_model,
            section_type=section_type,
        )

    def get_sections_by_type(
        self,
        section_type: Union[str, list, None] = None,
    ) -> Dict[str, SectionLattice]:
        """Return sections filtered by section type."""
        filtered_types = self._normalise_type_filter(section_type, context="section")
        if filtered_types is None:
            return self.sections

        return {
            name: section
            for name, section in self.sections.items()
            if section.section_type in filtered_types
        }

    def get_layouts_by_type(
        self,
        layout_type: Union[str, list, None] = None,
    ) -> Dict[str, MachineLayout]:
        """Return layouts filtered by layout type."""
        filtered_types = self._normalise_type_filter(layout_type, context="layout")
        if filtered_types is None:
            return self.lattices

        return {
            name: layout
            for name, layout in self.lattices.items()
            if layout.layout_type in filtered_types
        }

    def elements_between(
        self,
        end: str = None,
        start: str = None,
        element_type: Union[str, list, None] = None,
        element_model: Union[str, list, None] = None,
        element_class: Union[str, list, None] = None,
        path: str = None,
        section_type: Union[str, list, None] = None,
    ) -> List[str]:
        """
        Returns a list of all lattice elements (of a specified type) between
        any two points along the accelerator (inclusive). Elements are ordered according
        to their longitudinal position along the beam path.

        Parameters
        ----------
        end: str
            Name of the element defining the end of the search region
        start: str
            Name of the element defining the start of the search region
        element_type: str | list | None
            Filter by element type; if list, gather multiple types; if None, gather all.
        element_model: str | list | None
            Filter by element model; if list, gather multiple models; if None, gather all.
        element_class
            Filter by element hardware class; if list, gather multiple classes; if None, gather all.
        path: str
            Optional beam path, i.e. name of :class:`~laura.models.elementList.MachineLayout`.

        Returns
        -------
        List[str]
            Filtered names of elements.
        """
        # determine the beam path
        if path is None:
            if hasattr(self, "_default_path") and self._default_path in self.lattices:
                path = self._default_path
            else:
                raise Exception(
                    '"default_layout" = %s is not defined, and more than one layout exists.'
                    % self._default_path,
                )
        elif path not in self.lattices:
            raise Exception('"path" = %s is not defined' % path)

        if end is None:
            path_obj = self.lattices[path]
            end = path_obj.elements[-1]
        else:
            end_obj = self.get_element(end)
            beam_path = (
                end_obj.machine_area
                if (end_obj.machine_area in self.lattices)
                else path
            )
            path_obj = self.lattices[beam_path]

        # find the start of the search area
        if start is None:
            start = path_obj.elements[0]

        # return a list of elements along this beam path
        elements = path_obj.elements_between(
            start=start,
            end=end,
            element_type=element_type,
            element_class=element_class,
            element_model=element_model,
            section_type=section_type,
        )
        return elements

    def export_rdf(
        self,
        path: str,
        format: str = "turtle",
        machine_name: str = "machine",
    ) -> None:
        """Serialise this machine model to an RDF file.

        Requires the optional ``rdf`` dependency group::

            pip install "laura-accelerator[rdf]"

        Parameters
        ----------
        path:
            Output file path (e.g. ``"machine.ttl"``).
        format:
            RDF serialisation format.  One of ``"turtle"`` (default),
            ``"json-ld"``, ``"n-triples"`` / ``"nt"``, ``"xml"``.
        machine_name:
            Logical accelerator name embedded in element IRIs.
            Default ``"machine"``.
        """
        from laura.Exporters.RDF import export_machine_rdf  # deferred import

        export_machine_rdf(self, path=path, format=format, machine_name=machine_name)

    def sparql(
        self,
        query: str,
        machine_name: str = "machine",
    ) -> list[dict]:
        """Execute a SPARQL SELECT query over this machine model.

        Builds an in-memory RDF graph from :attr:`elements` (lazily, on first
        call) and runs the given SPARQL SELECT query against it using rdflib.

        Standard PREFIX declarations for ``laura:``, ``schema:``, ``qudt:``,
        ``rdf:``, ``rdfs:``, and ``xsd:`` are automatically prepended.

        Requires the optional ``rdf`` dependency group::

            pip install "laura-accelerator[rdf]"

        Parameters
        ----------
        query:
            SPARQL SELECT query string.
        machine_name:
            Logical accelerator name used when building element IRIs.
            Default ``"machine"``.

        Returns
        -------
        list[dict]
            One dict per result row; keys are variable names, values are
            Python native types.
        """
        from laura.query import LAURAQuery  # deferred import

        return LAURAQuery(self, machine_name=machine_name).sparql(query)
