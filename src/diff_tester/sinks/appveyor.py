import json
import os
import requests
from diff_tester.hookspecs import hookimpl, ISink

ENV = "APPVEYOR_API_URL"


class AppveyorSink(ISink):
    def __init__(self):
        self._state = "init"
        self.url = os.environ[ENV] + "api/tests"

    def start(self, tests):
        assert self._state == "init"

        self.tests = tests

        r = requests.post(self.url + "/batch", data=json.dumps([
            {
                "testName": test.name,
                "testFramework": "diff-tester",
                "fileName": "",
                "outcome": "None",
                "durationMilliseconds": "0",
                "ErrorMessage": "",
                "ErrorStackTrace": "",
                "StdOut": "",
                "StdErr": ""
            }
            for test in self.tests
        ]))
        print(r.status_code)

        self._state = "started"

    def test_start(self, id):
        assert self._state == "started"

    def test_done(self, id, result):
        assert self._state == "started"

    def finish(self):
        assert self._state == "started"
        self._state = "finished"


@hookimpl
def difftester_addoption(parser, action):
    if action in ("test", "run"):
        parser.add_argument('--no-appveyor-sink', action='store_true', help="disable reporting via AppVeyor Build Worker API")


@hookimpl
def difftester_create_sink(args):
    if not args.no_appveyor_sink and ENV in os.environ:
        return AppveyorSink()
