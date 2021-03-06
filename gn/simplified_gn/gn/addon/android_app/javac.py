#!/usr/bin/env python
#
# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import optparse
import os
import shutil
import re
import sys
import textwrap

sys.path.append(os.path.join(os.path.dirname(__file__), '../../script/pylib'))
from util import build_utils

import jar




def _FilterJavaFiles(paths, filters):
  return [f for f in paths
          if not filters or build_utils.MatchesGlob(f, filters)]


_MAX_MANIFEST_LINE_LEN = 72


def _CreateManifest(manifest_path, classpath, main_class=None,
                    manifest_entries=None):
  """Creates a manifest file with the given parameters.

  This generates a manifest file that compiles with the spec found at
  http://docs.oracle.com/javase/7/docs/technotes/guides/jar/jar.html#JAR_Manifest

  Args:
    manifest_path: The path to the manifest file that should be created.
    classpath: The JAR files that should be listed on the manifest file's
      classpath.
    main_class: If present, the class containing the main() function.
    manifest_entries: If present, a list of (key, value) pairs to add to
      the manifest.

  """
  output = ['Manifest-Version: 1.0']
  if main_class:
    output.append('Main-Class: %s' % main_class)
  if manifest_entries:
    for k, v in manifest_entries:
      output.append('%s: %s' % (k, v))
  if classpath:
    sanitized_paths = []
    for path in classpath:
      sanitized_paths.append(os.path.basename(path.strip('"')))
    output.append('Class-Path: %s' % ' '.join(sanitized_paths))
  output.append('Created-By: ')
  output.append('')

  wrapper = textwrap.TextWrapper(break_long_words=True,
                                 drop_whitespace=False,
                                 subsequent_indent=' ',
                                 width=_MAX_MANIFEST_LINE_LEN - 2)
  output = '\r\n'.join(w for l in output for w in wrapper.wrap(l))

  with open(manifest_path, 'w') as f:
    f.write(output)


def _ExtractClassFiles(jar_path, dest_dir, java_files):
  """Extracts all .class files not corresponding to |java_files|."""
  # Two challenges exist here:
  # 1. |java_files| have prefixes that are not represented in the the jar paths.
  # 2. A single .java file results in multiple .class files when it contains
  #    nested classes.
  # Here's an example:
  #   source path: ../../base/android/java/src/org/chromium/Foo.java
  #   jar paths: org/chromium/Foo.class, org/chromium/Foo$Inner.class
  # To extract only .class files not related to the given .java files, we strip
  # off ".class" and "$*.class" and use a substring match against java_files.
  def extract_predicate(path):
    if not path.endswith('.class'):
      return False
    path_without_suffix = re.sub(r'(?:\$[^/]+)?\.class$', '', path)
    preduced_java_name = path_without_suffix + '.java'
    return not any(preduced_java_name in p for p in java_files)

  build_utils.ExtractAll(jar_path, path=dest_dir, predicate=extract_predicate)


def _OnStaleMd5(changes, options, javac_cmd, java_files, classpath_inputs,
                runtime_classpath):
  with build_utils.TempDir() as temp_dir:
    srcjars = options.java_srcjars
    # The .excluded.jar contains .class files excluded from the main jar.
    # It is used for incremental compiles.
    excluded_jar_path = options.jar_path.replace('.jar', '.excluded.jar')

    classes_dir = os.path.join(temp_dir, 'classes')
    os.makedirs(classes_dir)
    excluded_classes_dir = os.path.join(temp_dir, 'excluded_classes')
    os.makedirs(excluded_classes_dir)

    changed_paths = None
    if options.incremental and changes.AddedOrModifiedOnly():
      changed_paths = set(changes.IterChangedPaths())
      # Do a full compile if classpath has changed.
      if any(p in changed_paths for p in classpath_inputs):
        changed_paths = None
      else:
        java_files = [p for p in java_files if p in changed_paths]
        srcjars = [p for p in srcjars if p in changed_paths]

    if srcjars:
      java_dir = os.path.join(temp_dir, 'java')
      os.makedirs(java_dir)
      for srcjar in options.java_srcjars:
        extract_predicate = None
        if changed_paths:
          changed_subpaths = set(changes.IterChangedSubpaths(srcjar))
          extract_predicate = lambda p: p in changed_subpaths
        build_utils.ExtractAll(srcjar, path=java_dir, pattern='*.java',
                               predicate=extract_predicate)
      jar_srcs = build_utils.FindInDirectory(java_dir, '*.java')
      java_files.extend(_FilterJavaFiles(jar_srcs, options.javac_includes))

    if java_files:
      if changed_paths:
        # When no files have been removed and the output jar already
        # exists, reuse .class files from the existing jar.
        _ExtractClassFiles(options.jar_path, classes_dir, java_files)
        _ExtractClassFiles(excluded_jar_path, classes_dir, java_files)
        # Add the extracted files to the classpath.
        classpath_idx = javac_cmd.index('-classpath')
        javac_cmd[classpath_idx + 1] += ':' + classes_dir

      java_list_file = os.path.join(temp_dir, 'java_list.txt')
      with open(java_list_file, 'w') as f:
        java_files = [ line + '\n' for line in java_files]
        f.writelines(java_files)
      # Don't include the output directory in the initial set of args since it
      # being in a temp dir makes it unstable (breaks md5 stamping).
      cmd = javac_cmd + ['-d', classes_dir] + [ '@' + java_list_file ]

      build_utils.CheckOutput(
          cmd,
          print_stdout=0)

    if options.main_class or options.manifest_entry:
      entries = []
      if options.manifest_entry:
        entries = [e.split(':') for e in options.manifest_entry]
      manifest_file = os.path.join(temp_dir, 'manifest')
      _CreateManifest(manifest_file, runtime_classpath, options.main_class,
                      entries)
    else:
      manifest_file = None

    glob = options.jar_excluded_classes
    inclusion_predicate = lambda f: not build_utils.MatchesGlob(f, glob)
    exclusion_predicate = lambda f: not inclusion_predicate(f)

    class_files = build_utils.FindInDirectory(classes_dir, '*.class')
    for c in class_files:
      if exclusion_predicate(c):
        new_c = os.path.join(excluded_classes_dir, os.path.relpath(c, classes_dir))
        os.rename(c, new_c)

    jar.JarDirectory(classes_dir,
                     options.jar_path,
                     manifest_file=manifest_file)
    jar.JarDirectory(excluded_classes_dir,
                     excluded_jar_path)


def _ParseOptions(argv):
  parser = optparse.OptionParser()
  build_utils.AddDepfileOption(parser)

  parser.add_option(
      '--src-gendirs',
      help='Directories containing generated java files.')
  parser.add_option(
      '--java-srcjars',
      action='append',
      default=[],
      help='List of srcjars to include in compilation.')
  parser.add_option(
      '--bootclasspath',
      action='append',
      default=[],
      help='Boot classpath for javac. If this is specified multiple times, '
      'they will all be appended to construct the classpath.')
  parser.add_option(
      '--classpath',
      action='append',
      help='Classpath for javac. If this is specified multiple times, they '
      'will all be appended to construct the classpath.')
  parser.add_option(
      '--use-ijars',
      action='store_true',
      help='Whether to use interface jars (.interface.jar) when compiling')
  parser.add_option(
      '--java-source',
      default='',
      help='Specify the source version ')
  parser.add_option(
      '--java-target',
      default='',
      help='Specify the target version')
  parser.add_option(
      '--incremental',
      action='store_true',
      help='Whether to re-use .class files rather than recompiling them '
           '(when possible).')
  parser.add_option(
      '--javac-includes',
      default='',
      help='A list of file patterns. If provided, only java files that match'
      'one of the patterns will be compiled.')
  parser.add_option(
      '--jar-excluded-classes',
      default='',
      help='List of .class file patterns to exclude from the jar.')

  parser.add_option('--jar-path', help='Jar output path.')
  parser.add_option(
      '--main-class',
      help='The class containing the main method.')
  parser.add_option(
      '--manifest-entry',
      action='append',
      help='Key:value pairs to add to the .jar manifest.')

  parser.add_option('--stamp', help='Path to touch on success.')


  options, args = parser.parse_args(argv)
  build_utils.CheckOptions(options, parser, required=('jar_path',))

  bootclasspath = []
  for arg in options.bootclasspath:
    bootclasspath += build_utils.ParseGypList(arg)
  options.bootclasspath = bootclasspath

  classpath = []
  for arg in options.classpath:
    classpath += build_utils.ParseGypList(arg)
  options.classpath = classpath

  java_srcjars = []
  for arg in options.java_srcjars:
    java_srcjars += build_utils.ParseGypList(arg)
  options.java_srcjars = java_srcjars

  if options.src_gendirs:
    options.src_gendirs = build_utils.ParseGypList(options.src_gendirs)

  options.javac_includes = build_utils.ParseGypList(options.javac_includes)
  options.jar_excluded_classes = (
      build_utils.ParseGypList(options.jar_excluded_classes))
  return options, args


def main(argv):

  argv = build_utils.ExpandFileArgs(argv)
  options, list_file = _ParseOptions(argv)

  java_files = []
  for item in list_file:
    if item.startswith('@'):
      with open(item[1:], 'r') as f:
        for line in f.readlines():
          java_files.append(line.strip())
    else:
      java_files.append(item)

  if options.src_gendirs:
    java_files += build_utils.FindInDirectories(options.src_gendirs, '*.java')

  java_files = _FilterJavaFiles(java_files, options.javac_includes)

  runtime_classpath = [os.path.normpath(p) for p in options.classpath]
  compile_classpath = runtime_classpath
  if options.use_ijars:
    ijar_re = re.compile(r'\.jar$')
    compile_classpath = (
        [ijar_re.sub('.interface.jar', p) for p in runtime_classpath])

  javac_cmd = ['javac']

  javac_cmd.extend((
      '-g',
      # Only allows UTF8 source files.  Being explicit avoids
      # javac pulling a default encoding from the user's environment.
      '-encoding', 'UTF-8',
      '-classpath', ':'.join(compile_classpath),
      # Prevent compiler from compiling .java files not listed as inputs.
      # See: http://blog.ltgt.net/most-build-tools-misuse-javac/
      '-sourcepath', ''
  ))

  if options.bootclasspath:
    javac_cmd.extend([
        '-bootclasspath', ':'.join(options.bootclasspath),
        '-source', options.java_source,
        '-target', options.java_target,
    ])

  # XDignore.symbol.file makes javac compile against rt.jar instead of
  # ct.sym. This means that using a java internal package/class will not
  # trigger a compile warning or error.
  javac_cmd.extend(['-XDignore.symbol.file'])

  classpath_inputs = options.bootclasspath
  # TODO(agrieve): Remove this .TOC heuristic once GYP is no more.
  if options.use_ijars:
    classpath_inputs.extend(compile_classpath)
  else:
    for path in compile_classpath:
      if os.path.exists(path + '.TOC'):
        classpath_inputs.append(path + '.TOC')
      else:
        classpath_inputs.append(path)

  # Compute the list of paths that when changed, we need to rebuild.
  input_paths = classpath_inputs + options.java_srcjars + java_files

  output_paths = [
      options.jar_path,
      options.jar_path.replace('.jar', '.excluded.jar'),
  ]

  # An escape hatch to be able to check if incremental compiles are causing
  # problems.
  force = int(os.environ.get('DISABLE_INCREMENTAL_JAVAC', 0))

  # List python deps in input_strings rather than input_paths since the contents
  # of them does not change what gets written to the depsfile.
  build_utils.CallAndWriteDepfileIfStale(
      lambda changes: _OnStaleMd5(changes, options, javac_cmd, java_files,
                                  classpath_inputs, runtime_classpath),
      options,
      input_paths=input_paths,
      input_strings=javac_cmd,
      output_paths=output_paths,
      force=force,
      pass_changes=True)

if __name__ == '__main__':
  sys.exit(main(sys.argv[1:]))

