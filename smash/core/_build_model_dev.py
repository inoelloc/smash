from __future__ import annotations

from smash.core._constant_dev import (
    STRUCTURE_NAME,
    STRUCTURE_COMPUTE_CI,
    INPUT_DATA_FORMAT,
)
from smash.core._read_input_data_dev import (
    _read_qobs_dev,
    _read_prcp_dev,
    _read_pet_dev,
    _read_descriptor_dev,
)

from smash.solver._mw_sparse_storage_dev import compute_rowcol_to_ind_sparse_dev
from smash.solver._mw_atmos_statistic_dev import compute_mean_atmos_dev
from smash.solver._mw_interception_capacity_dev import compute_interception_capacity_dev

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smash.solver._mwd_setup_dev import SetupDT_dev
    from smash.solver._mwd_mesh_dev import MeshDT_dev
    from smash.solver._mwd_input_data_dev import Input_DataDT_dev

import pandas as pd
import os


def _map_dict_to_object_dev(dct: dict, obj: object):
    for key, value in dct.items():
        if hasattr(obj, key):
            setattr(obj, key, value)


# % TODO: Maybe move standardize somewhere else
def _standardize_setup_dev(setup: SetupDT_dev):
    setup.structure = setup.structure.lower()
    if setup.structure not in STRUCTURE_NAME:
        raise ValueError(
            f"Unknown structure '{setup.structure}'. Choices: {STRUCTURE_NAME}"
        )

    if setup.dt < 0:
        raise ValueError("argument dt is lower than 0")

    if not setup.dt in [900, 3_600, 86_400]:
        warnings.warn(
            "argument dt is not set to a classical value (900, 3600, 86400 seconds)",
            UserWarning,
        )

    if setup.start_time == "...":
        raise ValueError("argument start_time is not defined")

    if setup.end_time == "...":
        raise ValueError("argument end_time is not defined")

    try:
        st = pd.Timestamp(setup.start_time)
    except:
        raise ValueError("argument start_time is not a valid date")

    try:
        et = pd.Timestamp(setup.end_time)
    except:
        raise ValueError("argument end_time is not a valid date")

    if (et - st).total_seconds() < 0:
        raise ValueError(
            "argument end_time corresponds to an earlier date than start_time"
        )

    if setup.read_qobs and setup.qobs_directory == "...":
        raise ValueError("argument read_qobs is True and qobs_directory is not defined")

    if setup.read_qobs and not os.path.exists(setup.qobs_directory):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            setup.qobs_directory,
        )

    if setup.read_prcp and setup.prcp_directory == "...":
        raise ValueError("argument read_prcp is True and prcp_directory is not defined")

    if setup.read_prcp and not os.path.exists(setup.prcp_directory):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            setup.prcp_directory,
        )

    if setup.prcp_format not in INPUT_DATA_FORMAT:
        raise ValueError(
            f"Unknown prcp_format '{setup.prcp_format}'. Choices: {INPUT_DATA_FORMAT}"
        )

    if setup.prcp_conversion_factor < 0:
        raise ValueError("argument prcp_conversion_factor is lower than 0")

    if setup.read_pet and setup.pet_directory == "...":
        raise ValueError("argument read_pet is True and pet_directory is not defined")

    if setup.read_pet and not os.path.exists(setup.pet_directory):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            setup.pet_directory,
        )

    if setup.pet_format not in INPUT_DATA_FORMAT:
        raise ValueError(
            f"Unknown pet_format '{setup.pet_format}'. Choices: {INPUT_DATA_FORMAT}"
        )

    if setup.pet_conversion_factor < 0:
        raise ValueError("argument pet_conversion_factor is lower than 0")

    if setup.read_descriptor and setup.descriptor_directory == "...":
        raise ValueError(
            "argument read_descriptor is True and descriptor_directory is not defined"
        )

    if setup.read_descriptor and not os.path.exists(setup.descriptor_directory):
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            setup.descriptor_directory,
        )

    if setup.read_descriptor and setup.nd == 0:
        raise ValueError(
            "argument read_descriptor is True and descriptor_name is not defined"
        )

    if setup.descriptor_format not in INPUT_DATA_FORMAT:
        raise ValueError(
            f"Unknown descriptor_format '{setup.descriptor_format}'. Choices: {INPUT_DATA_FORMAT}"
        )


def _build_setup_dev(setup: SetupDT_dev):
    _standardize_setup_dev(setup)

    st = pd.Timestamp(setup.start_time)

    et = pd.Timestamp(setup.end_time)

    setup.ntime_step = (et - st).total_seconds() / setup.dt


def _build_mesh_dev(setup: SetupDT_dev, mesh: MeshDT_dev):
    if setup.sparse_storage:
        compute_rowcol_to_ind_sparse_dev(
            mesh
        )  # % Fortran subroutine mw_sparse_storage_dev


def _build_input_data_dev(
    setup: SetupDT_dev, mesh: MeshDT_dev, input_data: Input_DataDT_dev
):
    if setup.read_qobs:
        _read_qobs_dev(setup, mesh, input_data)

    if setup.read_prcp:
        _read_prcp_dev(setup, mesh, input_data)

    if setup.read_pet:
        _read_pet_dev(setup, mesh, input_data)

    if setup.read_descriptor:
        _read_descriptor_dev(setup, mesh, input_data)

    compute_mean_atmos_dev(
        setup, mesh, input_data
    )  # % Fortran subroutine mw_atmos_statistic_dev


def _build_parameters_dev(
    setup: SetupDT_dev,
    mesh: MeshDT_dev,
    input_data: Input_DataDT_dev,
    parameters: ParametersDT_dev,
):
    if STRUCTURE_COMPUTE_CI[setup.structure] and setup.dt < 86_400:
        # % Date
        day_index = pd.date_range(
            start=setup.start_time, end=setup.end_time, freq=f"{int(setup.dt)}s"
        )[1:].to_series()

        # % Date to proleptic Gregorian ordinal
        day_index = day_index.apply(lambda x: x.toordinal()).to_numpy()

        # % Scale to 1 (Fortran indexing)
        day_index = day_index - day_index[0] + 1

        opr_parameters = getattr(parameters.opr_parameters, setup.structure)

        compute_interception_capacity_dev(
            setup, mesh, input_data, day_index, day_index[-1], opr_parameters.ci
        )  # % Fortran subroutine mw_interception_capacity_dev