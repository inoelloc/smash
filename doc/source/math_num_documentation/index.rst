.. _math_num_documentation:

========================
Math / Num Documentation
========================

`smash` is a computational software framework dedicated to **S**\patially distributed **M**\odeling and
**AS**\similation for **H**\ydrology, enabling the tackling of spatially distributed differentiable hydrological
modeling, with learnable parameterization-regionalization. This platform enables the combination of vertical and
lateral flow operators, either process-based conceptual or hybrid with neural networks, and performs high-dimensional
non-linear optimization from multi-source data. It is designed to simulate discharge hydrographs 
and hydrological states at any spatial location within a basin and reproduce the hydrological response of
contrasted catchments, both for operational forecasting of floods and low flows, by taking advantage of
spatially distributed meteorological forcings, physiographic data, and hydrometric observations.

`smash` is a modular platform, open source, and designed for collaborative research and operational applications.
It is based on a computationally efficient Fortran kernel enabling parallel computations over large domains, and is automatically differentiable with the Tapenade engine :cite:p:`hascoet2013tapenade` to generate the numerical adjoint model. The adjoint model enables the accurate computation of the gradient of a cost function to high-dimensional (spatially distributed) parameters and to perform optimization and learning.
It is interfaced in Python using f90wrap :cite:p:`Kermode2020-f90wrap` to (``i``) provide a user-friendly and versatile interface for quick learning 
and efficient development of research and applications, as well as to (``ii``) directly make accessible the wealth of Python modules and libraries developed by a large and active community (Data pre/post-Processing, Geographic Information System, Deep Learning, etc.).

This documentation details the conceptual and mathematical basis of the forward and inverse modeling problems, their numerical resolution, along with optimization and estimation algorithms.

.. toctree::
    :maxdepth: 2

    forward_inverse_problem

.. toctree::
    :maxdepth: 1

    precipitation_partitioning
    forward_structure
    mapping
    efficiency_error_metric
    hydrograph_segmentation
    hydrological_signature
    regularization_function
    cost_function
    optimization_algorithms
    bayesian_estimation
