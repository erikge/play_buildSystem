# Copyright (c) 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Copies the given "win tool" (which the toolchain uses to wrap compiler
# invocations) and the environment blocks for the 32-bit and 64-bit builds on
# Windows to the build directory.
#
# The arguments are the visual studio install location and the location of the
# win tool. The script assumes that the root build directory is the current dir
# and the files will be written to the current directory.

import os
import sys


def _CopyTool(source_path):
  """Copies the given tool to the current directory, including a warning not
  to edit it."""
  with open(source_path) as source_file:
    tool_source = source_file.readlines()

  # Add header and write it out to the current directory (which should be the
  # root build dir).
  with open("gyp-win-tool", 'w') as tool_file:
    tool_file.write(''.join([tool_source[0],
                             '# Generated by setup_toolchain.py do not edit.\n']
                            + tool_source[1:]))

def main():
  if len(sys.argv) < 2:
    print('Usage setup_gcc_toolchain_on_win.py '
          '<win tool path>')
    sys.exit(2)
  tool_source = sys.argv[1]

  _CopyTool(tool_source)


if __name__ == '__main__':
  main()
