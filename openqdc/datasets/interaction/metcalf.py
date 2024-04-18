import os
from glob import glob
from io import StringIO
from os.path import join as p_join
from typing import Dict, List

import numpy as np
from loguru import logger
from tqdm import tqdm

from openqdc.datasets.interaction.base import BaseInteractionDataset
from openqdc.methods import InteractionMethod, InterEnergyType
from openqdc.raws.config_factory import decompress_tar_gz
from openqdc.utils.constants import ATOM_TABLE

EXPECTED_TAR_FILES = {
    "train": [
        "TRAINING-2073-ssi-neutral.tar.gz",
        "TRAINING-2610-donors-perturbed.tar.gz",
        "TRAINING-4795-acceptors-perturbed.tar.gz",
    ],
    "val": ["VALIDATION-125-donors.tar.gz", "VALIDATION-254-acceptors.tar.gz"],
    "test": [
        "TEST-Acc--3-methylbutan-2-one_Don--NMe-acetamide-PLDB.tar.gz",
        "TEST-Acc--Cyclohexanone_Don--NMe-acetamide-PLDB.tar.gz",
        "TEST-Acc--Isoquinolone_NMe-acetamide.tar.gz",
        "TEST-Acc--NMe-acetamide_Don--Aniline-CSD.tar.gz",
        "TEST-Acc--NMe-acetamide_Don--Aniline-PLDB.tar.gz",
        "TEST-Acc--NMe-acetamide_Don--N-isopropylacetamide-PLDB.tar.gz",
        "TEST-Acc--NMe-acetamide_Don--N-phenylbenzamide-PLDB.tar.gz",
        "TEST-Acc--NMe-acetamide_Don--Naphthalene-1H-PLDB.tar.gz",
        "TEST-Acc--NMe-acetamide_Don--Uracil-PLDB.tar.gz",
        "TEST-Acc--Tetrahydro-2H-pyran-2-one_NMe-acetamide-PLDB.tar.gz",
        "TEST-NMe-acetamide_Don--Benzimidazole-PLDB.tar.gz",
    ],
}


def extract_raw_tar_gz(folder):
    logger.info(f"Extracting all tar.gz files in {folder}")
    for subset in EXPECTED_TAR_FILES:
        for tar_file in EXPECTED_TAR_FILES[subset]:
            tar_file_path = p_join(folder, tar_file)
            try:
                decompress_tar_gz(tar_file_path)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"File {tar_file_path} not found") from e


def content_to_xyz(content, subset):
    try:
        num_atoms = np.array([int(content.split("\n")[0])])
        tmp = content.split("\n")[1].split(",")
        name = tmp[0]
        e = tmp[1:-1]
    except Exception as e:
        logger.warning(f"Encountered exception in {content} : {e}")
        return None

    s = StringIO(content)
    d = np.loadtxt(s, skiprows=2, dtype="str")
    z, positions = d[:, 0], d[:, 1:].astype(np.float32)
    z = np.array([ATOM_TABLE.GetAtomicNumber(s) for s in z])
    xs = np.stack((z, np.zeros_like(z)), axis=-1)

    item = dict(
        n_atoms=num_atoms,
        subset=np.array([subset]),
        energies=e,
        atomic_inputs=np.concatenate((xs, positions), axis=-1, dtype=np.float32),
        name=np.array([name]),
        n_atoms_ptr=np.array([-1]),
    )

    return item


def read_xyz(fname, subset):
    with open(fname, "r") as f:
        contents = f.read().split("\n\n")
    res = [content_to_xyz(content, subset) for content in tqdm(contents)]
    return res


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
        # extract in folders
        extract_raw_tar_gz(self.root)
        data = []
        for filename in glob(self.root + f"{os.sep}*.xyz"):
            data.extend(read_xyz(filename, self.__name__))
        return data
