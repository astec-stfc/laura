from warnings import warn

cheetah_unsupported = [
    "Octupole",
    "TwissMatch",
    "Laser",
    "Plasma",
    "Wakefield",
    "Decapole",
    "ActivePlasmaLens",
    "CrabCavity",
]

_STATS = (
    "sigma_x",
    "sigma_y",
    "sigma_tau",
    "sigma_p",
    "normalized_emittance_x",
    "normalized_emittance_y",
)


def choose_cheetah_tracking_method(
    segment: object, beam: object, tolerance: float = 0.01, num_particles: int = 1000
) -> str:
    """
    Resolves ``cheetah_tracking_method = "auto"`` for a beam: which order is needed depends
    on its energy spread and the lattice. A subsample of ``beam`` is tracked
    through ``segment`` at first and second order, and the segment's drifts, quadrupoles
    and dipoles are set to ``second_order`` (with a warning) if any final beam size or
    emittance differs by more than ``tolerance``; otherwise, or for a ``ParameterBeam``,
    which second order can't track, to ``linear``.

    Parameters
    ----------
    segment: cheetah.Segment
        The segment, from :meth:`~laura.translator.converters.section.SectionLatticeTranslator.to_cheetah`
    beam: cheetah.Beam
        The beam to be tracked
    tolerance: float
        Largest relative difference for which linear tracking is kept
    num_particles: int
        Size of the subsample

    Returns
    -------
    str
        The tracking method set
    """
    import cheetah
    import torch

    elements = [
        e
        for e in segment.flattened().elements
        if isinstance(e, (cheetah.Drift, cheetah.Quadrupole, cheetah.Dipole))
    ]
    method = "linear"
    if isinstance(beam, cheetah.ParticleBeam):
        idx = torch.randperm(beam.num_particles)[:num_particles]
        sample = cheetah.ParticleBeam(
            beam.particles[idx],
            beam.energy,
            particle_charges=beam.particle_charges[idx],
            species=beam.species,
            dtype=beam.particles.dtype,
        )
        stats = {}
        for m in ("linear", "second_order"):
            for e in elements:
                e.tracking_method = m
            out = segment.track(sample)
            stats[m] = torch.stack([getattr(out, k) for k in _STATS])
        error = (
            (
                (stats["linear"] - stats["second_order"]).abs()
                / stats["second_order"].abs().clamp_min(1e-30)
            )
            .max()
            .item()
        )
        if error > tolerance:
            method = "second_order"
            warn(
                f"{segment.name}: Cheetah's linear tracking is {error:.1%} off second order for "
                f"this beam, so second_order is used; set cheetah_tracking_method in the "
                f"simulation settings to choose"
            )
    for e in elements:
        e.tracking_method = method
    return method
