"""
Shared fan-out machinery for the two container translators,
:class:`~laura.translator.converters.layout.MachineLayoutTranslator` and
:class:`~laura.translator.converters.model.MachineModelTranslator`.
"""

from textwrap import wrap
from typing import Any, Callable, Dict, Iterator, Tuple

from ..utils.functions import elegant_functional_definitions, sanitize_string


def wrap_lattice_line(line: str) -> str:
    """
    Wrap one elegant ``LINE = (...)`` definition to 80 columns.
    """
    return "&\n".join(wrap(line, 80, break_long_words=False, break_on_hyphens=False))


class ContainerTranslator:
    """
    Mixin supplying the ``to_CODE`` methods shared by the layout and model
    translators.
    """

    def _children(self) -> Iterator[Tuple[str, Any]]:
        """Yield ``(name, child_translator)`` for each child of this container."""
        raise NotImplementedError

    def _fan_out(
        self,
        method: str,
        key: Callable[[str], str] | None = None,
        child_kwargs: Callable[[str], Dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Call ``method`` on every child, collecting results by child name.

        ``key`` transforms that name into the result's dict key (MAD-X);
        ``child_kwargs`` gives one child its own share of a per-child argument
        (MAD-X ``beam``). Everything in ``kwargs`` goes to every child.
        """
        results = {}
        for name, child in self._children():
            extra = child_kwargs(name) if child_kwargs is not None else {}
            results[key(name) if key is not None else name] = getattr(child, method)(
                **kwargs, **extra
            )
        return results

    def to_astra(self) -> Dict[str, Any]:
        return self._fan_out("to_astra")

    def to_ocelot(self, save: bool = False) -> Dict[str, Any]:
        return self._fan_out("to_ocelot", save=save)

    def to_cheetah(self, save: bool = False) -> Dict[str, Any]:
        return self._fan_out("to_cheetah", save=save)

    def to_xsuite(
        self,
        beam_length: int,
        env: Any = None,
        particle_ref: Any = None,
        save: bool = False,
    ) -> Dict[str, Any]:
        return self._fan_out(
            "to_xsuite",
            beam_length=beam_length,
            env=env,
            particle_ref=particle_ref,
            save=save,
        )

    def to_rftrack(
        self, P_Q: float = float("nan"), save: bool = False
    ) -> Dict[str, Any]:
        """
        Create one RF-Track ``Lattice`` per section.

        Parameters
        ----------
        P_Q: float
            Beam reference momentum-over-charge [MV/c].
        save: bool
            See :meth:`~laura.translator.converters.section.SectionLatticeTranslator.to_rftrack`.
        """
        return self._fan_out("to_rftrack", P_Q=P_Q, save=save)

    def to_madx(
        self, beam: Dict[str, Any] | None = None, refer: str = "entry"
    ) -> Dict[str, Any]:
        """
        Create one MAD-X ``SEQUENCE`` per section, keyed by
        :func:`~laura.translator.utils.functions.sanitize_string` of the child
        name since MAD-X will not accept every name LAURA will.

        Parameters
        ----------
        beam: dict
            Keyed by child name, one level of nesting per container level: a
            layout takes ``{section_name: beam_dict}``, a model takes
            ``{layout_name: {section_name: beam_dict}}``. A section named here
            gets a ``BEAM`` declaration and a ``USE`` statement; the rest get a
            bare sequence definition. See
            :meth:`~laura.translator.converters.section.SectionLatticeTranslator.to_madx`.
        refer: str
            Element reference position, forwarded to every section.
        """
        return self._fan_out(
            "to_madx",
            key=sanitize_string,
            child_kwargs=lambda name: {
                "beam": beam.get(name) if isinstance(beam, dict) else None
            },
            refer=refer,
        )

    def _elegant_body(self, charge: float | None = None) -> Tuple[str, str]:
        """
        This container's elegant output as ``(definitions, lines)``, split so a
        parent can concatenate several containers' element definitions ahead of
        all of their ``LINE`` definitions.
        """
        raise NotImplementedError

    def _genesis_body(self) -> str:
        """This container's Genesis element and ``LINE`` definitions."""
        raise NotImplementedError

    def to_elegant(self, string: str = "", charge: float | None = None) -> str:
        """
        Create an elegant-compatible lattice file.

         Parameters
         ----------
         string: str
            Placed ahead of element definitions
        charge: float, optional
            Adds a ``CHARGE`` element at the head of each ``LINE``.

        Returns
        -------
        str
            String for the ELEGANT lattice file
        """
        definitions, lines = self._elegant_body(charge=charge)
        return (
            elegant_functional_definitions(self.functional_definitions)
            + string
            + definitions
            + lines
        )

    def to_genesis(self, string: str = "") -> str:
        """
        Create a Genesis-compatible (v4) lattice file.

        Parameters
         ----------
         string: str
            Placed ahead of element definitions

        Returns
        -------
        str
            String for the GENESIS lattice file
        """
        return string + self._genesis_body()
