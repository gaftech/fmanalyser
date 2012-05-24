# -*- coding: utf-8 -*-
"""This package provides access to user configuration files.

By default, those files are located in '~/.fmanalyser'.
They are ini-format files whose section_classes can be extended by subsections,
using the [section:subsection] syntax.


"""
from .base import BaseConfig
from .declarative import DeclarativeOptionMetaclass
from .holder import OptionHolder, EnableableSectionOptionHolder, EnableableOptionHolder
from .section import BaseConfigSection
from .source import IniFileSource