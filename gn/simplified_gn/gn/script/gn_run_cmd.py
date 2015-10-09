# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Helper script for GN to run an arbitrary command.

Run with:
  python gn_run_cmd.py <command_name> [args ...]
"""

import sys
import subprocess

args = sys.argv[1:]

sys.exit(subprocess.call(args))
