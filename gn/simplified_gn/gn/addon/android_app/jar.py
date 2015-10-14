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


def Jar(class_files, classes_dir, jar_path, manifest_file=None):
  jar_path = os.path.abspath(jar_path)

  # The paths of the files in the jar will be the same as they are passed in to
  # the command. Because of this, the command should be run in
  # options.classes_dir so the .class file paths in the jar are correct.
  jar_cwd = classes_dir
  class_files_rel = [os.path.relpath(f, jar_cwd) for f in class_files]
  jar_cmd = ['jar', 'cf0', jar_path]
  if manifest_file:
    jar_cmd[1] += 'm'
    jar_cmd.append(os.path.abspath(manifest_file))
  jar_cmd.extend(class_files_rel)

  with build_utils.TempDir() as temp_dir:
    empty_file = os.path.join(temp_dir, '.empty')
    build_utils.Touch(empty_file)
    jar_cmd.append(os.path.relpath(empty_file, jar_cwd))
    build_utils.CheckOutput(jar_cmd, cwd=jar_cwd)
    build_utils.Touch(jar_path, fail_if_missing=True)


def JarDirectory(classes_dir, jar_path, manifest_file=None,):
  jar_path = os.path.abspath(jar_path)

  # The paths of the files in the jar will be the same as they are passed in to
  # the command. Because of this, the command should be run in
  # options.classes_dir so the .class file paths in the jar are correct.
  jar_cwd = classes_dir
  classes_dir_rel = os.path.relpath(classes_dir, jar_cwd)
  jar_cmd = ['jar', 'cf0', jar_path]
  if manifest_file:
    jar_cmd[1] += 'm'
    jar_cmd.append(os.path.abspath(manifest_file))
  jar_cmd.extend( ['-C', classes_dir_rel, '.'] )


  with build_utils.TempDir() as temp_dir:
    empty_file = os.path.join(temp_dir, '.empty')
    build_utils.Touch(empty_file)
    jar_cmd.append(os.path.relpath(empty_file, jar_cwd))
    build_utils.CheckOutput(jar_cmd, cwd=jar_cwd)
    build_utils.Touch(jar_path, fail_if_missing=True)


def main():
  parser = optparse.OptionParser()
  parser.add_option('--classes-dir', help='Directory containing .class files.')
  parser.add_option('--jar-path', help='Jar output path.')
  parser.add_option('--stamp', help='Path to touch on success.')

  options, _ = parser.parse_args()

  JarDirectory(options.classes_dir, options.jar_path)

  if options.stamp:
    build_utils.Touch(options.stamp)


if __name__ == '__main__':
  sys.exit(main())


