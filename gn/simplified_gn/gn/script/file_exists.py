#!/usr/bin/env python
# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
"""Writes True if the argument is a directory."""

import os.path
import sys

def main():
  sys.stdout.write(_is_file(sys.argv[1]))
  return 0

def _is_file(file_name):
  return str(os.path.isfile(file_name))

def DoMain(args):
  """Hook to be called from gyp without starting a separate python
  interpreter."""
  return _is_file(args[0])

if __name__ == '__main__':
  sys.exit(main())
