Overview
########

Install
*******

For now, no release available, so install from github : https://github.com/gaftech/fmanalyser.

Requirements
------------
* Python 2.6 or 2.7. 


Optional dependencies
---------------------

* pyudev : needed by the client's device autodetect feature.
* unittest2 : needed to run tests. will be dropped when python 2.6 will stop to be supported. 


Quick module descriptions
*************************

:mod:`fmanalyser.client`
------------------------

Probes device over serial port and returns value with no particular
computing, except value conversion when it makes sense.

Future
******

The development is just beginning. I first work on the lowest level feature : the client module.
When it will be working, several higher level functionalities could be developed :

* a modbus client or any tool allowing to use the P175 device in existing scada/monitoring systems.
* a daemon providing a rest api
* etc., any ideas and contributions are welcome. 

This is not a priority but some work on compatibility should be done :

* to support Python 3
* to support other OS (for now test are done with stable Debian and Ubuntu)


Contributing
************

Any help would be welcome. Particularly :

* as my English is very poor, this documentation and the code documentation surely need big improvements.   

License
*******

This project is provided under the MIT License.
See `LICENSE.txt <https://github.com/gaftech/fmanalyser/blob/master/LICENSE.txt>`_ file.



