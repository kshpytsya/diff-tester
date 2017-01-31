"""
"""

from abc import ABCMeta, abstractmethod
import sys
from collections import namedtuple
from pluggy import HookspecMarker, HookimplMarker


def warning(msg):
    sys.stderr.write("warning: {}\n".format(msg))


def error(msg, code=1):
    sys.stderr.write("error: {}\n".format(msg))
    sys.exit(code)


TestDecl = namedtuple("TestDecl", "name description expected_success skipped")
TestResult = namedtuple("TestResult", "success output")


class ISink(metaclass=ABCMeta):
    @abstractmethod
    def start(self, tests):
        """ TODO
        """

    @abstractmethod
    def test_start(self, id):
        """ TODO
        """

    @abstractmethod
    def test_done(self, id, result):
        """ TODO
        """

    @abstractmethod
    def finish(self):
        """ TODO
        """


HOOKTAG = "diff-tester"

hookspec = HookspecMarker(HOOKTAG)
hookimpl = HookimplMarker(HOOKTAG)


@hookspec
def difftester_addoption(parser, action):
    """ add command line options for specific action or global ones
    action is None to the argparse-style parser object."""


@hookspec
def difftester_create_sink(args):
    """ possibly create ISink-implementing object if enabled by args.
    """
