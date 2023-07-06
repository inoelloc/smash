from __future__ import annotations

from smash._constant import STRUCTURE_NAME, INPUT_DATA_FORMAT

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smash.solver._mwd_setup import SetupDT

import pandas as pd
import os
import warnings
import errno


def _standardize_setup(setup: SetupDT):
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