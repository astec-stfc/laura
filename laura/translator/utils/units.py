"""
Unit-carrying numpy arrays for field maps.

Unit symbols, dimensions and SI prefixes come from
`openPMD-beamphysics <https://github.com/ChristopherMayes/openPMD-beamphysics>`_,
imported lazily as it pulls in matplotlib.
"""

from functools import cache

import numpy as np


def unit_power(string, power_factor=1):
    """# Takes a string in the form 'a^x' and returns ('a', x)"""
    if isinstance(string, (list, tuple)) and len(string) == 2:
        return string
    if "^" in string:
        pre, power = string.split("^")
        power = power.replace("(", "").replace(")", "")
        if "/" in power:
            powers = [int(s) for s in power.split("/")]
            power = powers[0]
            for p in powers[1:]:
                power /= p
        return pre, power_factor * float(power)
    return string, power_factor


def unit_power_multiply(string1, string2, power_factor=1):
    """Takes two strings in the form ('a', x) and ('a', y) and returns ('a', (x+y))"""
    unit1, power1 = unit_power(string1)
    unit2, power2 = unit_power(string2)
    if unit1 == unit2:
        power = power_factor * (power1 + power2)
        if power == 0:
            return "", 0
        if float(power).is_integer():
            return unit1, int(power)
        return unit1, float(power)


def unit_power_string(power_list, power_factor=1):
    """Returns a unit in ('a', x) format and makes a unit string"""
    unit, power = power_list
    power = power_factor * power
    if power == 0:
        return ""
    if float(power).is_integer():
        if power == 1:
            return unit
        return f"{unit}^{int(power)!s}"
    num, denom = power.as_integer_ratio()
    return f"{unit}^({num!s}/{denom!s})"


def unit_fraction(string):
    """split a tring into numerator and denominator taking into account () - input is string in form 'a^x*b/c^y'"""
    num = []
    denom = []
    substrings = num
    substring = ""
    inhat = False
    inbracket = False
    individe = False
    inhatdivide = 0
    for s in string:
        if s == "/":
            if not inhat:
                inhatdivide = 0
                individe = True
                if not substring.isnumeric() and not substring == "":
                    substrings.append(substring)
                substring = ""
                if individe and inbracket:
                    substrings = num
                else:
                    substrings = denom
            else:
                inhatdivide += 1
                if inhatdivide > 1:
                    inhatdivide = 0
                    if not substring.isnumeric() and not substring == "":
                        substrings.append(substring)
                    substring = ""
                    if individe and inbracket:
                        substrings = num
                    else:
                        substrings = denom
                else:
                    substring += s
        elif s == "*":
            individe = False
            inhatdivide = 0
            inhat = False
            if not substring.isnumeric() and not substring == "":
                substrings.append(substring)
            substring = ""
            if not inbracket:
                substrings = num
        elif s == " ":
            if inhat:
                inhatdivide = 0
                if substring[-1] == "/":
                    individe = True
                    substring = substring[:-1]
            inhat = False
            if not substring.isnumeric() and not substring == "":
                substrings.append(substring)
            substring = ""
            if individe:
                substrings = denom
        elif s == "(":
            inbracket = True
        elif s == ")":
            inbracket = False
        elif s == "^":
            inhat = True
            substring += s
        elif inhat and not s.isnumeric():
            inhat = False
            inhatdivide = 0
            if substring[-1] == "/":
                individe = True
                substring = substring[:-1]
            if not substring.isnumeric() and not substring == "":
                substrings.append(substring)
            substring = s
            if individe:
                substrings = denom
        else:
            substring += s

    if not substring.isnumeric() and not substring == "":
        substrings.append(substring)
    return num, denom


def expand_units(unit_list, power_factor=1):
    """Takes a list of units (normally numerator or denominator) and collects units and powers
    Returns units ('a^x') and unitnames (('a',x))"""

    unitnames = [unit_power(u, power_factor=power_factor) for u in unit_list]
    unique_units = list(set([u[0] for u in unitnames]))
    units = []
    for uu in unique_units:
        subunits = [u for u in unitnames if u[0] == uu]
        unit = subunits[0]
        if len(subunits) > 1:
            for u in subunits[1:]:
                unit = unit_power_multiply(unit, u)
            if not unit[1] == 0:
                units.append(unit)
        else:
            units.append(unit)
    return units


def collect_units(unit_powers):
    """Collects units into numerator ands denominator and uses '*' and '/' correctly"""
    combined_list = sorted(unit_powers, key=lambda x: -x[1])
    if len(combined_list) > 0:
        finalunit = unit_power_string(combined_list[0])
        for u in combined_list[1:]:
            if u[1] > 0:
                finalunit += f"*{unit_power_string(u)}"
            else:
                finalunit += f"/{unit_power_string(u, power_factor=-1)}"
    else:
        finalunit = ""
    return finalunit


def unit_powers(string, power_factor=1):
    num, denom = unit_fraction(string)
    return expand_units(
        expand_units(num, power_factor=power_factor)
        + expand_units(denom, power_factor=(-1 * power_factor))
    )


# cached: every UnitValue * and / re-parses both unit strings
@cache
def unit_multiply(string1, string2=False, divide=False):
    """multiply/divide two unit strings"""
    if divide:
        pf = [1, -1]
    else:
        pf = [1, 1]
    up1 = expand_units(unit_powers(string1, power_factor=pf[0]))
    if string2:
        up2 = expand_units(unit_powers(string2, power_factor=pf[1]))
    else:
        up2 = []
    return collect_units(expand_units(up1 + up2))


def unit_to_the_power(string1, power=1):
    """raise units to a power"""
    up1 = expand_units(unit_powers(string1, power_factor=power))
    return collect_units(up1)


def get_base_units(string):
    if isinstance(string, (UnitValue)):
        string = string.units
    from beamphysics.units import pmd_unit

    units_powers = unit_powers(string)
    return np.sum(
        [np.array(pmd_unit(u[0]).unitDimension) * u[1] for u in units_powers], axis=0
    )


@cache  # as unit_multiply, for every + and -
def are_units_equal(string1, string2):
    return (get_base_units(string1) == get_base_units(string2)).all()


class UnitValue(np.ndarray):
    """Subclass of ndarray MUST be initialized with a numpy array as first argument."""

    nounits = ["sin", "cos", "tan", "arcsin", "arccos", "arctan", "arctan2"]

    def __new__(cls, input_array, units=None, dtype=None):
        obj = np.asarray(input_array, dtype=dtype).view(cls)
        if units is None:
            units = ""
        obj.units = units
        return obj

    def __array_finalize__(self, obj):
        if obj is None:  # __new__ handles instantiation
            return
        """we essentially need to set all our attributes that are set in __new__ here again (including their default values).
        Otherwise numpy's view-casting and new-from-template mechanisms would break our class.
        """
        self.units = getattr(obj, "units", "")

    def __reduce__(self):
        """Keep the units through a pickle."""
        reconstruct, args, state = super().__reduce__()
        return reconstruct, args, state + (self.units,)

    def __setstate__(self, state):
        self.units = state[-1]
        super().__setstate__(state[:-1])

    def __array_ufunc__(
        self, ufunc, method, *inputs, **kwargs
    ):  # this method is called whenever you use a ufunc
        """this implementation of __array_ufunc__ makes sure that all custom attributes are maintained when a ufunc operation is performed on our class."""

        # convert inputs and outputs of class ArraySubclass to np.ndarray to prevent infinite recursion
        args = ((i.view(np.ndarray) if isinstance(i, UnitValue) else i) for i in inputs)
        outputs = kwargs.pop("out", None)
        if outputs:
            kwargs["out"] = tuple(
                (o.view(np.ndarray) if isinstance(o, UnitValue) else o) for o in outputs
            )
        else:
            outputs = (None,) * ufunc.nout
        # call numpys implementation of __array_ufunc__
        results = super().__array_ufunc__(ufunc, method, *args, **kwargs)  # pylint: disable=no-member
        if results is NotImplemented:
            return NotImplemented
        if method == "at":
            # method == 'at' means that the operation is performed in-place. Therefore, we are done.
            return
        # now we need to make sure that outputs that where specified with the 'out' argument are handled corectly:
        if ufunc.nout == 1:
            results = (results,)

        units = self.units if hasattr(self, "units") else ""

        if not ufunc.__name__ in self.nounits:
            if ufunc.__name__ == "sqrt":
                return UnitValue(
                    results[0] if len(results) == 1 else results,
                    units=unit_to_the_power(units, 0.5),
                )
            elif ufunc.__name__ == "square":
                return UnitValue(
                    results[0] if len(results) == 1 else results,
                    units=unit_to_the_power(units, 2),
                )
            return UnitValue(results[0] if len(results) == 1 else results, units=units)
        else:
            results = tuple(
                (self._copy_attrs_to(result) if output is None else output)
                for result, output in zip(results, outputs)
            )
            return results[0] if len(results) == 1 else results

    def _copy_attrs_to(self, target):
        """copies all attributes of self to the target object. target must be a (subclass of) ndarray"""
        target = target.view(UnitValue)
        try:
            target.units = self.units
        except AttributeError:
            pass
        return target

    @property
    def _isint(self):
        return "int" in str(self.val.dtype)

    @property
    def _isfloat(self):
        return "float" in str(self.val.dtype)

    def __repr__(self):
        from beamphysics.units import nice_scale_prefix

        if self.val.shape == ():
            if self._isint or self._isfloat:
                f, prefix = nice_scale_prefix(self.val)
                if self._isint:
                    return str(
                        f"{int.__repr__(int(self.val / f))} {prefix}{self.units}"
                    )
                return str(
                    f"{float.__repr__(float(self.val / f))} {prefix}{self.units}"
                )
            return str.__repr__(str(self.val))
        else:
            return str(f"{np.ndarray.__repr__(self.val)[:-1]}, units='{self.units}')")

    def __getitem__(self, key):
        if isinstance(key, slice):
            arr = super().__getitem__(key)
            return UnitValue(arr, units=self.units)
        elif isinstance(key, int):
            return UnitValue(super().__getitem__(key), units=self.units)
        return super().__getitem__(key)

    def _mul_div_units(self, m, newval, divide=False):
        if newval is NotImplemented:
            return newval
        if hasattr(m, "units"):
            newunit = unit_multiply(self.units, m.units, divide=divide)
            return UnitValue(newval, newunit)
        else:
            return UnitValue(newval, "")

    def __mul__(self, m):
        newarr = np.ndarray.__mul__(self, m)
        return self._mul_div_units(m, newarr)

    def __rmul__(self, m):
        newarr = np.ndarray.__rmul__(self, m)
        return self._mul_div_units(m, newarr)

    def __truediv__(self, m):
        newarr = np.ndarray.__truediv__(self, m)
        return self._mul_div_units(m, newarr, divide=True)

    def _add_sub_units(self, m, newval):
        if newval is NotImplemented:
            return newval
        if hasattr(m, "units"):
            if are_units_equal(m.units, self.units):
                return UnitValue(newval, self.units)
            else:
                return UnitValue(newval, "")
        else:
            return UnitValue(newval, self.units)

    def __add__(self, m):
        newarr = np.ndarray.__add__(self, m)
        return self._add_sub_units(m, newarr)

    def __sub__(self, m):
        newarr = np.ndarray.__sub__(self, m)
        return self._add_sub_units(m, newarr)

    def __pow__(self, m):
        newval = np.ndarray.__pow__(self, m)
        if newval is NotImplemented:
            return newval
        newunit = unit_to_the_power(self.units, m)
        return UnitValue(newval, newunit)

    def __round__(self, m):
        newval = np.round(self, m)
        if newval is NotImplemented:
            return newval
        return UnitValue(newval, self.units)

    def mean(self, *args, **kwargs):
        val = np.ndarray.mean(np.asarray(self), *args, **kwargs)
        return UnitValue(val, units=self.units)

    def std(self, *args, **kwargs):
        val = np.ndarray.std(np.asarray(self), *args, **kwargs)
        return UnitValue(val, units=self.units)

    def var(self, *args, **kwargs):
        val = np.ndarray.var(np.asarray(self), *args, **kwargs)
        return UnitValue(val, units=unit_to_the_power(self.units, 2))

    def sum(self, *args, **kwargs):
        val = np.ndarray.sum(np.asarray(self), *args, **kwargs)
        return UnitValue(val, units=self.units)

    def sqrt(self, *args, **kwargs):
        val = np.sqrt(np.asarray(self), *args, **kwargs)
        return UnitValue(val, units=unit_to_the_power(self.units, 0.5))

    @property
    def val(self):
        return np.asarray(self, dtype=self.dtype)

    @property
    def nice(self):
        from beamphysics.units import nice_scale_prefix

        f, prefix = nice_scale_prefix(self.val)
        return self.val / f, prefix

    def in_units_of(self, prefix):
        from beamphysics.units import PREFIX_FACTOR, SHORT_PREFIX_FACTOR

        if prefix in SHORT_PREFIX_FACTOR:
            f = SHORT_PREFIX_FACTOR[prefix]
        else:
            f = PREFIX_FACTOR.get(prefix.rstrip("-") + "-", 1)
        return self.val / f
