"""Convenience wrapper for installing target-repo templates."""

import sys

from harness_sensors.cli import main

raise SystemExit(main(["install", *sys.argv[1:]]))
