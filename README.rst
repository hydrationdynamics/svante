=======================
Svante: Arrhenius Plots
=======================
.. badges-begin

| |PyPi| |Python Version| |Repo| |Downloads| |Dlrate|
| |License| |Tests| |Coverage| |Codacy| |Issues|

.. |PyPI| image:: https://img.shields.io/pypi/v/svante.svg
   :target: https://pypi.org/project/svante/
   :alt: PyPI package
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/svante
   :target: https://pypi.org/project/svante
   :alt: Supported Python Versions
.. |Repo| image:: https://img.shields.io/github/last-commit/hydrationdynamics/svante
    :target: https://github.com/hydrationdynamics/svante
    :alt: GitHub repository
.. |Downloads| image:: https://pepy.tech/badge/svante
     :target: https://pepy.tech/project/pytest_datadir_mgr
     :alt: Download stats
.. |Dlrate| image:: https://img.shields.io/pypi/dm/svante
   :target: https://github.com/hydrationdynamics/svante
   :alt: PYPI download rate
.. |License| image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.s
vg
    :target: https://github.com/hydrationdynamics/svante/blob/master/LICENSE.
txt
    :alt: License terms
.. |Tests| image:: https://github.com/hydrationdynamics/svante/workflows/Tests/badge.svg
   :target: https://github.com/hydrationdynamics/svante/actions?workflow=Tests
   :alt: Tests
.. |Coverage| image:: https://codecov.io/gh/hydrationdynamics/svante/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/hydrationdynamics/svante
    :alt: Codecov.io test coverage
.. |Codacy| image:: https://api.codacy.com/project/badge/Grade/d9c8687d3c544049a293b2faf8919c07
    :target: https://www.codacy.com/gh/hydrationdynamics/svante?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hydrationdynamics/svante&amp;utm_campaign=Badge_Grade
    :alt: Codacy.io grade
.. |Issues| image:: https://img.shields.io/github/issues/hydrationdynamics/svante.svg
    :target:  https://github.com/hydrationdynamics/svante/issues
    :alt: Issues reported
.. |Read the Docs| image:: https://img.shields.io/readthedocs/svante/latest.svg?label=Read%20the%20Docs
   :target: https://svante.readthedocs.io/
   :alt: Read the documentation at https://svante.readthedocs.io/
.. badges-end

.. image:: https://raw.githubusercontent.com/hydrationdynamics/svante/main/do
cs/_static/logo.png
   :target: https://raw.githubusercontent.com/hydrationdynamics/svante/main/LICENSE.artwork.txt
   :alt: Fly Svante logo

.. |Codecov| image:: https://codecov.io/gh/hydrationdynamics/svante/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/hydrationdynamics/svante
   :alt: Codecov

Features
--------

* Combines rate columns from multiple input TSV files
* Handles uncertainties in rates and uncertainties
* Creates Arrhenius plots
* Fits activation enthalpies and prefactors to rates
* Optionally, plots ratios of two rates


Requirements
------------

* Python 3.7 to 3.9 on Linux or Mac


Installation
------------

You can install *Svante* via pip_ from PyPI_:

.. code:: console

   $ pip install svante


Usage
-----

Please see the `Command-line Reference <Usage_>`_ for details.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `BSD 3-Clause license`_,
*Svante* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

Svante was written by Joel Berendzen.

.. github-only
.. _Contributor Guide: CONTRIBUTING.rst
.. _Usage: https://svante.readthedocs.io/en/latest/usage.html
