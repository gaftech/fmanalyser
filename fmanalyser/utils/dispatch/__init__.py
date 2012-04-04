"""Multi-consumer multi-producer dispatching mechanism

Based on Django signal feature. https://www.djangoproject.com/
Originally based on pydispatch (BSD) http://pypi.python.org/pypi/PyDispatcher/2.0.1

See license.txt for original license.

Heavily modified for Django's purposes.
"""

from .dispatcher import Signal, receiver