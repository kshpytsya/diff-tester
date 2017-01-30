import json
import os
import requests
from diff_tester.hookspecs import hookimpl, ISink

ENV = "APPVEYOR_API_URL"


class AppveyorSink(ISink):
    def __init__(self):
        self._state = "init"
        self.url = os.environ[ENV]

    def _post_request(self, endpoint, j):
        r = requests.post(self.url + endpoint, json=j)
        try:
            print(r.status_code, r.json())
        except:
            print(r.status_code, r.text)

    def start(self, tests):
        assert self._state == "init"

        self.tests = tests

        self._post_request("api/build/messages", {
            "message": "This is a test message",
            "category": "warning",
            "details": "Additional information for the message"
        })

        self._post_request("api/tests/batch", [
            {
                "testName": test.name,
                "testFramework": "diff-tester",
                "fileName": "some.file",
                "outcome": "None",
                "durationMilliseconds": "0",
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
