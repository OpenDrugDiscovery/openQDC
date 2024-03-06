import importlib
import os
from typing import TYPE_CHECKING  # noqa F401

# The below lazy import logic is coming from openff-toolkit:
# https://github.com/openforcefield/openff-toolkit/blob/b52879569a0344878c40248ceb3bd0f90348076a/openff/toolkit/__init__.py#L44

# Dictionary of objects to lazily import; maps the object's name to its module path

_lazy_imports_obj = {
    "BaseInteractionDataset": "openqdc.datasets.interaction.base",
    "DES370K": "openqdc.datasets.interaction.des370k",
    "DES5M": "openqdc.datasets.interaction.des5m",
    "Metcalf": "openqdc.datasets.interaction.metcalf",
    "DESS66": "openqdc.datasets.interaction.dess66",
    "DESS66x8": "openqdc.datasets.interaction.dess66x8",
}

_lazy_imports_mod = {}


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
    from .base import BaseInteractionDataset
    from .des370k import DES370K
    from .des5m import DES5M
    from .metcalf import Metcalf
    from .dess66 import DESS66
    from .dess66x8 import DESS66x8

    __all__ = [
        "BaseInteractionDataset",
        "DES370K",
        "DES5M",
        "Metcalf",
        "DESS66",
        "DESS66x8",
    ]
