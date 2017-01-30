import os
import requests
from diff_tester.hookspecs import hookimpl, ISink, error, warning

ENV = "APPVEYOR_API_URL"


class AppveyorSink(ISink):
    def __init__(self, fail_on_errors):
        self._state = "init"
        self.url = os.environ[ENV]
        self.fail_on_errors = fail_on_errors

    def _request(self, method, endpoint, j):
        r = requests.request(method, self.url + endpoint, json=j)
        if 400 <= r.status_code < 600:
            try:
                msg = r.json()["Message"]
            except:
                msg = r.text

            [warning, error][self.fail_on_errors]("AppVeyor API failed: " + msg)

    def start(self, tests):
        assert self._state == "init"

        self.tests = tests

        self._request("POST", "api/tests/batch", [
            {
                "testName": test.name,
                "testFramework": "diff-tester",
                "outcome": ["None", "Skipped"][test.skipped],
                "fileName": "",
            }
            for test in self.tests
        ])

        self._state = "started"

    def test_start(self, id):
        assert self._state == "started"

        test = self.tests[id]

        self._request("PUT", "api/tests",
            {
                "testName": test.name,
                "outcome": "Running"
            }
        )

    def test_done(self, id, result):
        assert self._state == "started"

        test = self.tests[id]

        self._request("PUT", "api/tests",
            {
                "testName": test.name,
                "outcome": ["Failed", "Passed"][result.success],
                # "durationMilliseconds": "0",
                # "ErrorMessage": "",
                # "ErrorStackTrace": "",
                "StdOut": result.output,
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
