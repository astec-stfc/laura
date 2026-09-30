from dataclasses import dataclass
from typing import Optional

# Every CLARA element type LAURA hits today resolves through
# BaseElementTranslator.to_slipstream()'s drift-equivalent fallback, so
# there is nothing to reject yet -- kept for parity with the other
# per-code `<code>_unsupported` lists (see section.py's
# `_check_elements_supported`).
slipstream_unsupported = []


@dataclass
class SlipstreamElement:
    """One element's parameters for the ``slipstream`` accelerator-tracking
    package, as consumed by
    ``slipstream.tracking.native.laura_import.parse_laura_lattice``.

    Deliberately a plain dataclass, not a pydantic model or a LAURA
    :class:`~laura.models.element.Element` subclass -- this is an interchange
    format between two independently-versioned packages, not part of either
    one's own internal schema. Every field defaults so an element only needs
    to fill in what its own type actually uses (mirrors slipstream's own
    ``ElementSpec``, a similarly flat dataclass with a ``kind`` string used
    only for readability, not dispatch).

    Covers two independent downstream consumers:

    - **Linear-optics linac elements** (``name, hardware_type, length, angle,
      k1, k2, e1, e2, tilt, dx, dy``): fed to slipstream's ``ElementSpec`` for
      its single-pass ``LinacTracker`` (drift/quad/sext/bend/RF-as-lumped-kick).
      ``phase_deg`` here is elegant's own PHASE convention (``90 -
      <LAURA's off-crest-is-zero phase>``).
    - **Raw-field injector elements** (``field_map_hdf5_path,
      wakefield_hdf5_path, e_max_v_per_m, b_max_t, frequency_hz, n_cells,
      injector_phase_deg, crest_deg, grad_T_per_m, aperture_shape,
      aperture_radius_m, aperture_horizontal_m, aperture_vertical_m``): for
      slipstream's space-charge-dominated ``Injector`` (real on-axis field
      tables read directly from LAURA's own HDF5 field-map format, a Boris
      pusher) -- the *raw source* HDF5 path, not an ASTRA-regenerated copy;
      slipstream reads it directly (optional dependency on ``laura`` itself,
      already established by the linac-optics path) via its own
      ``laura.translator.utils.fields.FieldMap`` reader.
      ``injector_phase_deg`` is ASTRA's/``Injector``'s own convention
      (LAURA's ``self.phase`` verbatim, off-crest-is-zero) -- deliberately a
      separate field from ``phase_deg`` above since the two consumers use
      different phase conventions for the same physical quantity.
      ``grad_T_per_m`` is a real field gradient (ASTRA's ``Q_grad``), not the
      normalized ``k1`` above. Aperture fields mirror ``to_astra()``'s own
      shape dispatch (``aperture.py``) -- a "rectangular"/"planar"/"scraper"
      shape can need *two* ``Injector.Aperture`` objects (X and Y) from one
      LAURA element, decided on the slipstream side.
    """

    name: str
    hardware_type: str
    length: float
    z_m: float = 0.0
    angle: float = 0.0
    k1: float = 0.0
    k2: float = 0.0
    e1: float = 0.0
    e2: float = 0.0
    tilt: float = 0.0
    dx: float = 0.0
    dy: float = 0.0
    field_map_hdf5_path: Optional[str] = None
    wakefield_hdf5_path: Optional[str] = None
    e_max_v_per_m: float = 0.0
    b_max_t: float = 0.0
    frequency_hz: float = 0.0
    n_cells: int = 0
    phase_deg: float = 0.0
    injector_phase_deg: float = 0.0
    crest_deg: Optional[float] = None
    voltage_v: float = 0.0
    n_kicks: int = 1
    change_p0: bool = False
    end1_focus: bool = False
    end2_focus: bool = False
    body_focus_model: str = "none"
    grad_T_per_m: float = 0.0
    # Aperture (Injector's raw-field path only): aperture_shape is one of
    # LAURA's own ApertureElement.shape values ("circular"/"elliptical"/
    # "planar"/"rectangular"/"scraper"); radius_m for the former two,
    # horizontal_m/vertical_m for the latter two (mirrors to_astra()'s own
    # RAD-vs-COL_X/COL_Y-vs-SCR_X/SCR_Y dispatch -- see aperture.py).
    aperture_shape: Optional[str] = None
    aperture_radius_m: float = 0.0
    aperture_horizontal_m: float = 0.0
    aperture_vertical_m: float = 0.0
