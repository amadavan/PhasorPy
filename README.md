<!--<img src="assets/phasor-banner.png" width="1000">-->
![Logo](assets/phasor-banner.png)
----
<!--[![Build Status](https://travis-ci.org/amadavan/phasor.svg?branch=master)]-->

Power systems simulations in academic work are frequently solved using
the [MATPOWER](http://www.pserc.cornell.edu/matpower/) package. The
package provides MATLAB and Octave M-files in order to solve power flow,
continuation power flow and optimal power flow problems. The goal of the
Phasor package is remove the need for MATLAB or Octave while
providing access to the wide array of existing MATPOWER case files.

# Requirements
#### External software
- [Stuka]() - C++ optimization library
- Python

# Installation
Download the library using
```
git clone git://github.com/amadavan/stuka.git
```
Enter the Phasor directory and install the library using
```
python setup.py install
```

Hopefully, in the near future we will allow this library to be installed
using
```
pip install phasorpy
```

# Acknowledgements
