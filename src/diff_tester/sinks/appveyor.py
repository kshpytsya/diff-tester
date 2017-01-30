import json
import os
import sys
import requests
from diff_tester.hookspecs import hookimpl, ISink, error, warning

ENV = "APPVEYOR_API_URL"


class AppveyorSink(ISink):
    def __init__(self, fail_on_errors):
        self._state = "init"
        self.url = os.environ[ENV]
        self.fail_on_errors = fail_on_errors

    def _post_request(self, endpoint, j):
        r = requests.post(self.url + endpoint, json=j)
        if 400 <= r.status_code < 600:
            try:
                msg = r.json()["Message"]
            except:
                msg = r.text

            [warning, error][self.fail_on_errors]("AppVeyor API failed: " + msg)

    def start(self, tests):
        assert self._state == "init"

        self.tests = tests

        self._post_request("api/tests/batch", [
            {
                "testName": test.name,
                "testFramework": "diff-tester",
                # "fileName": "",
                "outcome": ["None", "Skipped"][test.skipped],
                # "durationMilliseconds": "0",
                "ErrorMessage": "",
                "ErrorStackTrace": "",
                "StdOut": "",
                "StdErr": ""
            }
            for test in self.tests
        ])

        self._state = "started"

    def test_start(self, id):
        assert self._state == "started"

        test = self.tests[id]

        self._post_request("api/tests",
            {
                "testName": test.name,
                "testFramework": "diff-tester",
                # "fileName": "",
                "outcome": "Running",
                # "durationMilliseconds": "0",
                # "ErrorMessage": "",
                # "ErrorStackTrace": "",
                # "StdOut": "",
                # "StdErr": ""
            }
        )

    def test_done(self, id, result):
        assert self._state == "started"

        test = self.tests[id]

        self._post_request("api/tests",
            {
                "testName": test.name,
                "testFramework": "diff-tester",
                # "fileName": "",
                "outcome": ["Failed", "Passed"][test.success],
                # "durationMilliseconds": "0",
                # "ErrorMessage": "",
                # "ErrorStackTrace": "",
                "StdOut": test.output,
                # "StdErr": ""
            }
        )

    def finish(self):
        assert self._state == "started"
        self._state = "finished"


@hookimpl
def difftester_addoption(parser, action):
    if action in ("test", "run"):
        parser.add_argument('--no-appveyor-sink', action='store_true', help="disable reporting via AppVeyor Build Worker API")
        parser.add_argument('--appveyor-sink-fail', action='store_true', help="fail on AppVeyor Build Worker API errors")


@hookimpl
def difftester_create_sink(args):
    if not args.no_appveyor_sink and ENV in os.environ:
        return AppveyorSink(args.appveyor_sink_fail)
