# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A utility to run functions with timeouts and retries."""
# pylint: disable=W0702

import logging
import threading
import time
import traceback

from devil.utils import reraiser_thread
from devil.utils import watchdog_timer


class TimeoutRetryThread(reraiser_thread.ReraiserThread):
  def __init__(self, func, timeout, name):
    super(TimeoutRetryThread, self).__init__(func, name=name)
    self._watcher = watchdog_timer.WatchdogTimer(timeout)
    self._expired = False

  def GetWatcher(self):
    """Returns the watchdog keeping track of this thread's time."""
    return self._watcher

  def GetElapsedTime(self):
    return self._watcher.GetElapsed()

  def GetRemainingTime(self, required=0, msg=None):
    """Get the remaining time before the thread times out.

    Useful to send as the |timeout| parameter of async IO operations.

    Args:
      required: minimum amount of time that will be required to complete, e.g.,
        some sleep or IO operation.
      msg: error message to show if timing out.

    Returns:
      The number of seconds remaining before the thread times out, or None
      if the thread never times out.

    Raises:
      reraiser_thread.TimeoutError if the remaining time is less than the
        required time.
    """
    remaining = self._watcher.GetRemaining()
    if remaining is not None and remaining < required:
      if msg is None:
        msg = 'Timeout expired'
      if remaining > 0:
        msg += (', wait of %.1f secs required but only %.1f secs left'
                % (required, remaining))
      self._expired = True
      raise reraiser_thread.TimeoutError(msg)
    return remaining

  def LogTimeoutException(self):
    """Log the exception that terminated this thread."""
    if not self._expired:
      return
    logging.critical('*' * 80)
    logging.critical('%s on thread %r', self._exc_info[0].__name__, self.name)
    logging.critical('*' * 80)
    fmt_exc = ''.join(traceback.format_exception(*self._exc_info))
    for line in fmt_exc.splitlines():
      logging.critical(line.rstrip())
    logging.critical('*' * 80)


def CurrentTimeoutThread():
  """Get the current thread if it is a TimeoutRetryThread.

  Returns:
    The current thread if it is a TimeoutRetryThread, otherwise None.
  """
  current_thread = threading.current_thread()
  if isinstance(current_thread, TimeoutRetryThread):
    return current_thread
  else:
    return None


def WaitFor(condition, wait_period=5, max_tries=None):
  """Wait for a condition to become true.

  Repeatedly call the function condition(), with no arguments, until it returns
  a true value.

  If called within a TimeoutRetryThread, it cooperates nicely with it.

  Args:
    condition: function with the condition to check
    wait_period: number of seconds to wait before retrying to check the
      condition
    max_tries: maximum number of checks to make, the default tries forever
      or until the TimeoutRetryThread expires.

  Returns:
    The true value returned by the condition, or None if the condition was
    not met after max_tries.

  Raises:
    reraiser_thread.TimeoutError if the current thread is a TimeoutRetryThread
      and the timeout expires.
  """
  condition_name = condition.__name__
  timeout_thread = CurrentTimeoutThread()
  while max_tries is None or max_tries > 0:
    result = condition()
    if max_tries is not None:
      max_tries -= 1
    msg = ['condition', repr(condition_name), 'met' if result else 'not met']
    if timeout_thread:
      # pylint: disable=no-member
      msg.append('(%.1fs)' % timeout_thread.GetElapsedTime())
    logging.info(' '.join(msg))
    if result:
      return result
    if timeout_thread:
      # pylint: disable=no-member
      timeout_thread.GetRemainingTime(wait_period,
          msg='Timed out waiting for %r' % condition_name)
    time.sleep(wait_period)
  return None


def Run(func, timeout, retries, args=None, kwargs=None, desc=None):
  """Runs the passed function in a separate thread with timeouts and retries.

  Args:
    func: the function to be wrapped.
    timeout: the timeout in seconds for each try.
    retries: the number of retries.
    args: list of positional args to pass to |func|.
    kwargs: dictionary of keyword args to pass to |func|.
    desc: An optional description of |func| used in logging. If omitted,
      |func.__name__| will be used.

  Returns:
    The return value of func(*args, **kwargs).
  """
  if not args:
    args = []
  if not kwargs:
    kwargs = {}

  # The return value uses a list because Python variables are references, not
  # values. Closures make a copy of the reference, so updating the closure's
  # reference wouldn't update where the original reference pointed.
  ret = [None]
  def RunOnTimeoutThread():
    ret[0] = func(*args, **kwargs)

  num_try = 1
  while True:
    child_thread = TimeoutRetryThread(
      RunOnTimeoutThread, timeout,
      name='TimeoutThread-%d-for-%s' % (num_try,
                                        threading.current_thread().name))
    try:
      thread_group = reraiser_thread.ReraiserThreadGroup([child_thread])
      thread_group.StartAll()
      while True:
        thread_group.JoinAll(watcher=child_thread.GetWatcher(), timeout=60)
        if thread_group.IsAlive():
          logging.info('Still working on %s', desc if desc else func.__name__)
        else:
          return ret[0]
    except:
      child_thread.LogTimeoutException()
      if num_try > retries:
        raise
      num_try += 1
