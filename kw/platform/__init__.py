__version__ = "0.2.1"

__title__ = "kiwi-platform"
__description__ = "Company standards as code for Kiwi.com"
__url__ = "https://github.com/kiwicom/kiwi-platform-py/"
__uri__ = __url__

__author__ = "Bence Nagy"
__email__ = "bence@kiwi.com"

__license__ = "Blue Oak License"
__copyright__ = "Copyright (c) 2019 Kiwi.com"

from .monkey import patch


__all__ = ["patch"]
