=====================
Configuration utility
=====================

Overview
********

For now, all `fmanalyser` features aim to rely on a single configuration file.
This file is optional and is used to override default values defined by the
different modules.

This file, if it exists must be located at this path : `~/.fmanalyser/config.ini`.

Each module documentation specify which sections/values are used for the features
they provide.

Test environment specific file
******************************

If needed, the `~/.fmanalyser/test.ini` config file can be created. It will then
override what is defined in `config.ini`. Read more : :ref:`test-configuration`. 

