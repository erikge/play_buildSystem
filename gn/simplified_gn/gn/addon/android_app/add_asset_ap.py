#!/usr/bin/env python
#
# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import optparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../script/pylib'))
from util import build_utils


def _ParseArgs(args):
  args = build_utils.ExpandFileArgs(args)

  parser = optparse.OptionParser()
  build_utils.AddDepfileOption(parser)

  parser.add_option('--android-sdk', help='path to the Android SDK folder')
  parser.add_option('--aapt-path',
                    help='path to the Android aapt tool')
  parser.add_option('--ap-path',
                    help='Path to (partial) apk.')

  options, add_files = parser.parse_args(args)

  required_options = ('android_sdk', 'aapt_path', 'ap_path')

  build_utils.CheckOptions(options, parser, required=required_options)

  return options, add_files



def _OnStaleMd5(package_command, options):
  build_utils.CheckOutput(package_command, print_stdout=False, print_stderr=False)


def main(args):
  options, add_files = _ParseArgs(args)
  
  package_command = [
      options.aapt_path,
      'a',
      options.ap_path
  ]
  package_command.extend(add_files)

  input_paths = []
  input_paths.extend(add_files)

  output_paths = [ options.ap_path ]


  build_utils.CallAndWriteDepfileIfStale(
      lambda: _OnStaleMd5(package_command, options),
      options,
      input_paths=input_paths,
      input_strings=package_command,
      output_paths=output_paths)


if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))
