Testing
#######

I'm currently using `nose <http://readthedocs.org/docs/nose/en/latest/>`_ to run tests.

.. _test-configuration:

Test configuration
******************
Test cases inherits :class:`fmanalyser.test.TestCase`.
It allows to define a test specific configuration file, named `test.ini`,
which, if it exists, will replace the usual `conf.ini` file.

In the config file, a special section is used to set
test specific parameters. As usual, the `conf.example.ini` file aims to provide
details about available parameters. 

Some available test parameters
******************************

Disabling live tests
====================

By default, some test needs a device connected to the system.
That requirement can be disabled by setting `live_tests` to `false`
in the config file `[test]` section.
