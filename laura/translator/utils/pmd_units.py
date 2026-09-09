"""
Simple units functionality for the openPMD beamphysics records.

For more advanced units, use a package like Pint:
    https://pint.readthedocs.io/
"""

c_light = 299792458
e_charge = 1.602176634e-19


class pmd_unit:
    """

    Params
    ------

    unitSymbol: Native units name
    unitSI:     Conversion factor to the the correspontign SI unit
    unitDimension: SI Base Exponents

    Base unit dimensions are defined as:

    .. code-block:: text

       Base dimension  | exponents.       | SI unit
       ---------------- -----------------   -------
       length          : (1,0,0,0,0,0,0)     m
       mass            : (0,1,0,0,0,0,0)     kg
       time            : (0,0,1,0,0,0,0)     s
       current         : (0,0,0,1,0,0,0)     A
       temperture      : (0,0,0,0,1,0,0)     K
       mol             : (0,0,0,0,0,1,0)     mol
       luminous        : (0,0,0,0,0,0,1)     cd


    Example:

        ``pmd_unit('eV', 1.602176634e-19, (2, 1, -2, 0, 0, 0, 0))``

        defines that an eV is 1.602176634e-19 of base units m^2 kg/s^2, which is a Joule (J)

    If ``unitSI=0`` (default), init with a known symbol:

        ``pmd_unit('T')``

        returns ``pmd_unit('T', 1, (0, 1, -2, -1, 0, 0, 0))``


    Simple equalities are provided:

        ``u1 == u2``

        Returns True if the params are all the same.

    """

    def __init__(self, unitSymbol="", unitSI=0, unitDimension=(0, 0, 0, 0, 0, 0, 0)):

        # Allow to return an internally known unit
        if unitSI == 0:
            if unitSymbol in known_unit:
                # Copy internals
                u = known_unit[unitSymbol]
                unitSI = u.unitSI
                unitDimension = u.unitDimension
            else:
                raise ValueError(f"unknown unitSymbol: {unitSymbol}")

        self._unitSymbol = unitSymbol
        self._unitSI = unitSI
        if isinstance(unitDimension, str):
            self._unitDimension = DIMENSION[unitDimension]
        else:
            self._unitDimension = unitDimension

    @property
    def unitSymbol(self):
        return self._unitSymbol

    @property
    def unitSI(self):
        return self._unitSI

    @property
    def unitDimension(self):
        return self._unitDimension

    def __mul__(self, other):
        return multiply_units(self, other)

    def __truediv__(self, other):
        return divide_units(self, other)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.unitSymbol

    def __repr__(self):
        return f"pmd_unit('{self.unitSymbol}', {self.unitSI}, {self.unitDimension})"


def is_identity(u):
    """Checks if the unit is equivalent to 1"""
    return u.unitSI == 1 and u.unitDimension == (0, 0, 0, 0, 0, 0, 0)


def multiply_units(u1, u2):
    """
    Multiplies two pmd_unit symbols
    """

    if is_identity(u1):
        return u2
    if is_identity(u2):
        return u1

    s1 = u1.unitSymbol
    s2 = u2.unitSymbol
    if s1 == s2:
        symbol = f"{s1}^2"
    else:
        symbol = s1 + "*" + s2
    d1 = u1.unitDimension
    d2 = u2.unitDimension
    dim = tuple(sum(x) for x in zip(d1, d2))
    unitSI = u1.unitSI * u2.unitSI

    return pmd_unit(unitSymbol=symbol, unitSI=unitSI, unitDimension=dim)


def divide_units(u1, u2):
    """
    Divides two pmd_unit symbols : u1/u2
    """

    if is_identity(u2):
        return u1

    s1 = u1.unitSymbol
    s2 = u2.unitSymbol
    if s1 == s2:
        symbol = "1"
    else:
        symbol = s1 + "/" + s2
    d1 = u1.unitDimension
    d2 = u2.unitDimension
    dim = tuple(a - b for a, b in zip(d1, d2))
    unitSI = u1.unitSI / u2.unitSI

    return pmd_unit(unitSymbol=symbol, unitSI=unitSI, unitDimension=dim)


DIMENSION = {
    "1": (0, 0, 0, 0, 0, 0, 0),
    # Base units
    "length": (1, 0, 0, 0, 0, 0, 0),
    "mass": (0, 1, 0, 0, 0, 0, 0),
    "time": (0, 0, 1, 0, 0, 0, 0),
    "current": (0, 0, 0, 1, 0, 0, 0),
    "temperture": (0, 0, 0, 0, 1, 0, 0),
    "mol": (0, 0, 0, 0, 0, 1, 0),
    "luminous": (0, 0, 0, 0, 0, 0, 1),
    #
    "charge": (0, 0, 1, 1, 0, 0, 0),
    "electric_field": (1, 1, -3, -1, 0, 0, 0),
    "electric_potential": (1, 2, -3, -1, 0, 0, 0),
    "magnetic_field": (0, 1, -2, -1, 0, 0, 0),
    "velocity": (1, 0, -1, 0, 0, 0, 0),
    "energy": (2, 1, -2, 0, 0, 0, 0),
    "momentum": (1, 1, -1, 0, 0, 0, 0),
}

known_unit = {
    "1": pmd_unit("", 1, "1"),
    "rad": pmd_unit("", 1, "1"),
    "m": pmd_unit("m", 1, "length"),
    "kg": pmd_unit("kg", 1, "mass"),
    "g": pmd_unit("g", 0.001, "mass"),
    "s": pmd_unit("s", 1, "time"),
    "A": pmd_unit("A", 1, "current"),
    "K": pmd_unit("K", 1, "temperture"),
    "mol": pmd_unit("mol", 1, "mol"),
    "cd": pmd_unit("cd", 1, "luminous"),
    "C": pmd_unit("C", 1, "charge"),
    "charge_num": pmd_unit("charge #", 1, "charge"),
    "V/m": pmd_unit("V/m", 1, "electric_field"),
    "V": pmd_unit("V", 1, "electric_potential"),
    "c_light": pmd_unit("vel/c", c_light, "velocity"),
    "c": pmd_unit("vel/c", c_light, "velocity"),
    "m/s": pmd_unit("m/s", 1, "velocity"),
    "eV": pmd_unit("eV", e_charge, "energy"),
    "J": pmd_unit("J", 1, "energy"),
    "eV/c": pmd_unit("eV/c", e_charge / c_light, "momentum"),
    "T": pmd_unit("T", 1, "magnetic_field"),
}


def unit(symbol):
    """
    Returns a pmd_unit from a known symbol.

    * is allowed between two known symbols:
    """
    if symbol in known_unit:
        return known_unit[symbol]

    if "*" in symbol:
        subunits = [known_unit[s] for s in symbol.split("*")]
        # Require these to be in known units
        assert len(subunits) == 2, "TODO: more complicated units"
        return multiply_units(subunits[0], subunits[1])

    raise ValueError(f"Unknown unit symbol: {symbol}")
