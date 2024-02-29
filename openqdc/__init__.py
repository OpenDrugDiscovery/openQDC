import importlib
import os
from typing import TYPE_CHECKING  # noqa F401

# The below lazy import logic is coming from openff-toolkit:
# https://github.com/openforcefield/openff-toolkit/blob/b52879569a0344878c40248ceb3bd0f90348076a/openff/toolkit/__init__.py#L44

# Dictionary of objects to lazily import; maps the object's name to its module path

_lazy_imports_obj = {
    "__version__": "openqdc._version",
    "BaseDataset" : "openqdc.datasets",
    "ANI1": "openqdc.datasets",
    "ANI1CCX": "openqdc.datasets",
    "ANI1X": "openqdc.datasets",
    "Spice": "openqdc.datasets",
    "GEOM": "openqdc.datasets",
    "QMugs": "openqdc.datasets",
    "ISO17": "openqdc.datasets",
    "COMP6": "openqdc.datasets",
    "GDML": "openqdc.datasets",
    "Molecule3D": "openqdc.datasets",
    "OrbnetDenali": "openqdc.datasets",
    "SN2RXN": "openqdc.datasets",
    "QM7X": "openqdc.datasets",
    "DESS": "openqdc.datasets",
    "NablaDFT": "openqdc.datasets",
    "SolvatedPeptides": "openqdc.datasets",
    "WaterClusters": "openqdc.datasets",
    "TMQM": "openqdc.datasets",
    "Dummy": "openqdc.datasets",
    "PCQM_B3LYP": "openqdc.datasets",
    "PCQM_PM6": "openqdc.datasets",
    "Transition1X": "openqdc.datasets",
}

_lazy_imports_mod = {"datasets": "openqdc.datasets",
                     "utils": "openqdc.utils"}


def __getattr__(name):
    """Lazily import objects from _lazy_imports_obj or _lazy_imports_mod

    Note that this method is only called by Python if the name cannot be found
    in the current module."""
    obj_mod = _lazy_imports_obj.get(name)
    if obj_mod is not None:
        mod = importlib.import_module(obj_mod)
        return mod.__dict__[name]

    lazy_mod = _lazy_imports_mod.get(name)
    if lazy_mod is not None:
        return importlib.import_module(lazy_mod)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Add _lazy_imports_obj and _lazy_imports_mod to dir(<module>)"""
    keys = (*globals().keys(), *_lazy_imports_obj.keys(), *_lazy_imports_mod.keys())
    return sorted(keys)


if TYPE_CHECKING or os.environ.get("OPENQDC_DISABLE_LAZY_LOADING", "0") == "1":
    # These types are imported lazily at runtime, but we need to tell type
    # checkers what they are.
    from ._version import __version__
    from .datasets.ani import ANI1, ANI1CCX, ANI1X  # noqa
    from .datasets.comp6 import COMP6  # noqa
    from .datasets.dess import DESS  # noqa
    from .datasets.dummy import Dummy  # noqa
    from .datasets.gdml import GDML  # noqa
    from .datasets.geom import GEOM  # noqa
    from .datasets.iso_17 import ISO17  # noqa
    from .datasets.molecule3d import Molecule3D  # noqa
    from .datasets.nabladft import NablaDFT  # noqa
    from .datasets.orbnet_denali import OrbnetDenali  # noqa
    from .datasets.pcqm import PCQM_B3LYP, PCQM_PM6  # noqa
    from .datasets.qm7x import QM7X  # noqa
    from .datasets.qmugs import QMugs  # noqa
    from .datasets.sn2_rxn import SN2RXN  # noqa
    from .datasets.solvated_peptides import SolvatedPeptides  # noqa
    from .datasets.spice import Spice  # noqa
    from .datasets.tmqm import TMQM  # noqa
    from .datasets.transition1x import Transition1X  # noqa
    from .datasets.waterclusters3_30 import WaterClusters  # noqa
    from .datasets.base import BaseDataset  # noqa
