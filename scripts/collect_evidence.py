"""Convenience wrapper for collecting evidence."""

import sys

from harness_sensors.cli import main

raise SystemExit(main(["collect", *sys.argv[1:]]))
