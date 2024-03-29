from os.path import join as p_join

import numpy as np
from openqdc.methods import QmPotentialMethod
from openqdc.datasets.base import BaseDataset
from openqdc.raws.fetch import decompress_tar_gz

trajectories = {
    "rmd17_aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "rmd17_benzene": "c1ccccc1",
    "rmd17_malonaldehyde": "C(C=O)C=O",
    "rmd17_paracetamol": "CC(=O)Nc1ccc(cc1)O",
    "rmd17_toluene": "Cc1ccccc1",
    "rmd17_azobenzene": "C1=CC=C(C=C1)N=NC2=CC=CC=C2",
    "rmd17_ethanol": "CCO",
    "rmd17_naphthalene": "C1=CC=C2C=CC=CC2=C1",
    "rmd17_salicylic": "C1=CC=C(C(=C1)C(=O)O)O",
    "rmd17_uracil": "C1=CNC(=O)NC1=O",
}


def shape_atom_inputs(coords, atom_species):
    reshaped_coords = coords.reshape(-1, 3)
    frame, atoms, _ = coords.shape
    z = np.tile(atom_species, frame)
    xs = np.stack((z, np.zeros_like(z)), axis=-1)
    return np.concatenate((xs, reshaped_coords), axis=-1, dtype=np.float32)


def read_npz_entry(filename, root):
    data = np.load(create_path(filename, root))
    nuclear_charges, coords, energies, forces = (
        data["nuclear_charges"],
        data["coords"],
        data["energies"],
        data["forces"],
    )
    frames = coords.shape[0]
    res = dict(
        name=np.array([trajectories[filename]] * frames),
        subset=np.array([filename] * frames),
        energies=energies[:, None].astype(np.float32),
        forces=forces.reshape(-1, 3, 1).astype(np.float32),
        atomic_inputs=shape_atom_inputs(coords, nuclear_charges),
        n_atoms=np.array([len(nuclear_charges)] * frames, dtype=np.int32),
    )
    return res


def create_path(filename, root):
    return p_join(root, "rmd17", "npz_data", filename + ".npz")


class RevMD17(BaseDataset):
    """
    - Benzene: 627000 samples
    - Uracil: 133000 samples
    - Naptalene: 326000 samples
    - Aspirin: 211000 samples
    - Salicylic Acid: 320000 samples
    - Malonaldehyde: 993000 samples
    - Ethanol: 555000 samples
    - Toluene: 100000 samples

    Usage
    ```python
    from openqdc.datasets import RevMD17
    dataset = RevMD17()
    ```

    References:
    - https://arxiv.org/abs/2007.09593
    """

    __name__ = "revmd17"

    __energy_methods__ = [
        QmPotentialMethod.PBE_DEF2_TZVP
        # "pbe/def2-tzvp",
    ]

    energy_target_names = [
        "PBE-TS Energy",
    ]

    __force_methods__ = [
        "pbe/def2-tzvp",
    ]

    force_target_names = [
        "PBE-TS Gradient",
    ]

    __energy_unit__ = "kcal/mol"
    __distance_unit__ = "ang"
    __forces_unit__ = "kcal/mol/ang"

    def read_raw_entries(self):
        entries_list = []
        decompress_tar_gz(p_join(self.root, "rmd17.tar.bz2"))
        for trajectory in trajectories:
            entries_list.append(read_npz_entry(trajectory, self.root))
        return entries_list
