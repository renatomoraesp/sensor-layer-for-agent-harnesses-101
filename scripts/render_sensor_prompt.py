"""Convenience wrapper for rendering sensor prompts."""

import sys

from harness_sensors.cli import main

raise SystemExit(main(["render", *sys.argv[1:]]))
