"""
Unit and phase conventions shared by the AC dipole translator and the Bmad
importer.
"""

MV_PER_VOLT = 1e-6
"""LAURA holds ``field_amplitude`` in volts."""

SINE_TO_COSINE_TURNS = -0.25
"""Phase shift taking LAURA's sine convention to Bmad's cosine one, in turns.
LAURA's ``phase`` is in degrees, so ``phi = phase/360 - 0.25``."""
