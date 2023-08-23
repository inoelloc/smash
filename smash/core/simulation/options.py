from __future__ import annotations

from smash.core.simulation._standardize import (
    _standardize_simulation_optimize_options,
    _standardize_simulation_cost_options,
    _standardize_default_optimize_options_args,
    _standardize_default_cost_options_args,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smash.core.model.model import Model

__all__ = ["default_optimize_options", "default_cost_options"]


# % TODO: add docstring - this function is used for creating and the documentation of optimize_options in model.optimize()
def default_optimize_options(
    model: Model,
    mapping: str = "uniform",
    optimizer: str | None = None,
) -> dict:
    mapping, optimizer = _standardize_default_optimize_options_args(mapping, optimizer)

    return _standardize_simulation_optimize_options(model, mapping, optimizer, None)


# % TODO: add docstring - this function is used for creating and the documentation of cost_options in model.optimize()
# % Future TODO: cost_options depending on (mapping, cost_variant) instead of cost_variant
def default_cost_options(
    model: Model,
    cost_variant: str = "cls",
) -> dict:
    cost_variant = _standardize_default_cost_options_args(cost_variant)

    return _standardize_simulation_cost_options(model, cost_variant, None)