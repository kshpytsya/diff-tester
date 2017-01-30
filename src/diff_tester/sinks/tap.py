import sys
from diff_tester.hookspecs import hookimpl, ISink


class TapSink(ISink):
    def __init__(self):
        self._state = "init"

    def start(self, tests):
        assert self._state == "init"

        self.tests = tests

        sys.stdout.write("TAP version 13\n1..{}\n".format(len(tests)))

        for id, test in enumerate(self.tests):
            if test.skipped:
                sys.stdout.write("ok {} # skip {}\n".format(id + 1, test.name))

        self._state = "started"

    def test_start(self, id):
        assert self._state == "started"

    def test_done(self, id, result):
        assert self._state == "started"

        sys.stdout.write("{}ok {} - {}\n".format(["not ", ""][result.success], id + 1, self.tests[id].name))

    def finish(self):
        assert self._state == "started"
        self._state = "finished"


@hookimpl
def difftester_addoption(parser, action):
    if action in ("test", "run"):
        parser.add_argument('--sink-tap', action='store_true', help="output test results as TAP (Test Anything Protocol) v13 to stdout")


@hookimpl
def difftester_create_sink(args):
    if args.sink_tap:
        return TapSink()
