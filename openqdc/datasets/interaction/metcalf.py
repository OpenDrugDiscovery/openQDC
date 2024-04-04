import os
from typing import Dict, List

import numpy as np

from openqdc.datasets.interaction.base import BaseInteractionDataset
from openqdc.methods import InteractionMethod, InterEnergyType
from openqdc.utils.constants import ATOM_TABLE


class Metcalf(BaseInteractionDataset):
    """
    Hydrogen-bonded dimers of NMA with 126 molecules as described in:

    Approaches for machine learning intermolecular interaction energies and
    application to energy components from symmetry adapted perturbation theory.
    Derek P. Metcalf, Alexios Koutsoukas, Steven A. Spronk, Brian L. Claus,
    Deborah A. Loughney, Stephen R. Johnson, Daniel L. Cheney, C. David Sherrill;
    J. Chem. Phys. 21 February 2020; 152 (7): 074103.
    https://doi.org/10.1063/1.5142636

    Further details:
    "Hydrogen-bonded dimers involving N-methylacetamide (NMA) and 126 molecules
    (46 donors and 80 acceptors; Figs. 2 and 3) were used. Optimized geometries
    for the 126 individual monomers were obtained and paired with NMA in broad
    arrays of spatial configurations to generate thousands of complexes for training.
    """

    __name__ = "metcalf"
    __energy_unit__ = "kcal/mol"
    __distance_unit__ = "ang"
    __forces_unit__ = "kcal/mol/ang"
    __energy_methods__ = [
        InteractionMethod.SAPT0_JUN_CC_PVDZ,
        InteractionMethod.SAPT0_JUN_CC_PVDZ,
        InteractionMethod.SAPT0_JUN_CC_PVDZ,
        InteractionMethod.SAPT0_JUN_CC_PVDZ,
        InteractionMethod.SAPT0_JUN_CC_PVDZ,
    ]
    __energy_type__ = [
        InterEnergyType.TOTAL,
        InterEnergyType.ES,
        InterEnergyType.EX,
        InterEnergyType.IND,
        InterEnergyType.DISP,
    ]
    energy_target_names = [
        "total energy",
        "electrostatic energy",
        "exchange energy",
        "induction energy",
        "dispersion energy",
    ]

    def read_raw_entries(self) -> List[Dict]:
        data = []
        for dirname in os.listdir(self.root):
            xyz_dir = os.path.join(self.root, dirname)
            if not os.path.isdir(xyz_dir):
                continue
            subset = np.array([dirname.split("-")[0].lower()])  # training, validation, or test
            for filename in os.listdir(xyz_dir):
                if not filename.endswith(".xyz"):
                    continue
                lines = list(map(lambda x: x.strip(), open(os.path.join(xyz_dir, filename), "r").readlines()))
                line_two = lines[1].split(",")
                energies = np.array([line_two[1:6]], dtype=np.float32)
                num_atoms = np.array([int(lines[0])])

                elem_xyz = np.array([x.split() for x in lines[2:]])
                elements = elem_xyz[:, 0]
                xyz = elem_xyz[:, 1:].astype(np.float32)
                atomic_nums = np.expand_dims(np.array([ATOM_TABLE.GetAtomicNumber(x) for x in elements]), axis=1)
                charges = np.expand_dims(np.array([0] * num_atoms[0]), axis=1)

                atomic_inputs = np.concatenate((atomic_nums, charges, xyz), axis=-1, dtype=np.float32)

                item = dict(
                    n_atoms=num_atoms,
                    subset=subset,
                    energies=energies,
                    positions=xyz,
                    atomic_inputs=atomic_inputs,
                    name=np.array([""]),
                    n_atoms_first=np.array([-1]),
                )
                data.append(item)
        return data
