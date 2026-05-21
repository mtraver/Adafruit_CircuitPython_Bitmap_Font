# SPDX-FileCopyrightText: 2026 Michael Traver for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import sys

import tests.fontio

# Make the mock fontio available during testing.
sys.modules["fontio"] = tests.fontio
