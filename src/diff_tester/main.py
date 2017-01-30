import argparse
import sys
import pkgutil
import pluggy

import diff_tester
from .hookspecs import ISink, TestDecl, TestResult
from . import hookspecs
import diff_tester.sinks


def pm_register_all_modules(pm, package):
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
        module = importer.find_module(modname).load_module(modname)
        pm.register(module)
        if ispkg:
            pm_register_all_modules(pm, module)


def warning(msg):
    sys.stderr.write("warning: {}\n".format(msg))


class SinkSet(ISink):
    def __init__(self, pm, args):
        self.sinks = pm.hook.difftester_create_sink(args=args)
        assert all(isinstance(sink, ISink) for sink in self.sinks)
        if len(self.sinks) == 0:
            warning("no test sinks defined")

    def start(self, *args, **kw):
        for sink in self.sinks:
            sink.start(*args, **kw)

    def test_start(self, *args, **kw):
        for sink in self.sinks:
            sink.test_start(*args, **kw)

    def test_done(self, *args, **kw):
        for sink in self.sinks:
            sink.test_done(*args, **kw)

    def finish(self, *args, **kw):
        for sink in self.sinks:
            sink.finish(*args, **kw)


def action_test(pm, args):
    sink = SinkSet(pm, args)
    tests = [
        TestDecl(name="alpha", description="successful test expected to succeed", expected_success=True, skipped=False),
        TestDecl(name="beta", description="successful test expected to fail", expected_success=False, skipped=False),
        TestDecl(name="gamma", description="failed test expected to succeed", expected_success=True, skipped=False),
        TestDecl(name="delta", description="failed test expected to fail", expected_success=False, skipped=False),
        TestDecl(name="epsilon", description="skipped test", expected_success=True, skipped=True),
    ]
    sink.start(tests)

    for i in range(len(tests)):
        sink.test_start(i)

    sink.test_done(0, TestResult(success=True, output="alpha output"))
    sink.test_done(1, TestResult(success=True, output="beta output"))
    sink.test_done(2, TestResult(success=False, output="delta output"))
    sink.test_done(3, TestResult(success=False, output="epsilon output"))

    sink.finish()


def action_run(pm, args):
    pass


def action_gold(pm, args):
    pass


def action_lint(pm, args):
    pass


def main():
    pm = pluggy.PluginManager(hookspecs.TAG)
    pm.add_hookspecs(hookspecs)
    pm_register_all_modules(pm, diff_tester.sinks)
    pm.load_setuptools_entrypoints(hookspecs.TAG)
    pm.check_pending()

    parser = argparse.ArgumentParser(
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + diff_tester.__version__)
    pm.hook.difftester_addoption(parser=parser, action=None)

    subparsers = parser.add_subparsers(title="actions", dest="action", description="")
    subparsers.required = True

    parser_test = subparsers.add_parser('test', help='')
    parser_run = subparsers.add_parser('run', help='')
    parser_gold = subparsers.add_parser('gold', help='')
    parser_lint = subparsers.add_parser('lint', help='')

    pm.hook.difftester_addoption(parser=parser_test, action="test")
    pm.hook.difftester_addoption(parser=parser_run, action="run")

    args = parser.parse_args()

    globals()["action_" + args.action](pm, args)


if __name__ == "__main__":
    main()
