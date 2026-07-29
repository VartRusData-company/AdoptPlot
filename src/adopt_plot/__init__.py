"""Adopt Plot package"""
# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2026 VartRusData. All rights reserved.
class TooManyVariablesError(ValueError):
    """Исключение, возникающее при попытке построить график для более чем двух переменных."""
    pass
class PltNotFoundError(ModuleNotFoundError):
    pass
from .plot import AdoptPlot
__all__ = ["AdoptPlot", "TooManyVariablesError"]