#!/usr/bin/env python
#
# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import optparse
import os
import sys

from util import build_utils


### erik ### def Jar(class_files, classes_dir, jar_path, manifest_file=None):
def Jar(class_files, classes_dir, jar_path, too_long=False, manifest_file=None):
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
### erik ###
  if too_long:
    classes_dir_rel = os.path.relpath(classes_dir, jar_cwd)
    jar_cmd.extend( ['-C', classes_dir_rel, '.'] )
  else:
    jar_cmd.extend(class_files_rel)
#  jar_cmd.extend(class_files_rel)
### erik ###

  with build_utils.TempDir() as temp_dir:
    empty_file = os.path.join(temp_dir, '.empty')
    build_utils.Touch(empty_file)
    jar_cmd.append(os.path.relpath(empty_file, jar_cwd))
    build_utils.CheckOutput(jar_cmd, cwd=jar_cwd)
    build_utils.Touch(jar_path, fail_if_missing=True)


### erik ###
#def JarDirectory(classes_dir, excluded_classes, jar_path, manifest_file=None):
#  class_files = build_utils.FindInDirectory(classes_dir, '*.class')
#  class_files = [f for f in class_files
#                 if not build_utils.MatchesGlob(f, excluded_classes)]
#
#  Jar(class_files, classes_dir, jar_path, manifest_file=manifest_file)
def JarDirectory(classes_dir, jar_path, too_long=False, manifest_file=None, predicate=None):
  class_files = []
  if not too_long:
    class_files = build_utils.FindInDirectory(classes_dir, '*.class')
    if predicate:
      class_files = [f for f in class_files if predicate(f)]

  Jar(class_files, classes_dir, jar_path, too_long=too_long, manifest_file=manifest_file)
### erik ###


def main():
  parser = optparse.OptionParser()
  parser.add_option('--classes-dir', help='Directory containing .class files.')
  parser.add_option('--jar-path', help='Jar output path.')
  parser.add_option('--excluded-classes',
      help='List of .class file patterns to exclude from the jar.')
  parser.add_option('--stamp', help='Path to touch on success.')

  options, _ = parser.parse_args()

  predicate = None
  if options.excluded_classes:
    excluded_classes = build_utils.ParseGypList(options.excluded_classes)
    predicate = lambda f: not build_utils.MatchesGlob(f, excluded_classes)

  JarDirectory(options.classes_dir, options.jar_path, predicate=predicate)

  if options.stamp:
    build_utils.Touch(options.stamp)


if __name__ == '__main__':
  sys.exit(main())

