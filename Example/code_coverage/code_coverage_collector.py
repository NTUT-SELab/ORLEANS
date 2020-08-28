import copy
from Example.code_coverage.request_handler import RequestHandler
from code_coverage.i_code_coverage_collector import CodeCoverageCollector


class IstanbulMiddleware(CodeCoverageCollector):

    def __init__(self, server_port=3000):
        super().__init__(server_port)
        self._verified_coverage_vector = None
        self.request_handler = RequestHandler(server_port=server_port)
        self.reset_coverage()

    def get_coverage_vector(self):
        coverage_vector = self.request_handler.get_branch_coverage_vector()
        if self._verified_coverage_vector is not None:
            coverage_vector = do_or_operation(coverage_vector, self._verified_coverage_vector)
        return list(map(lambda c: 300 if c > 0 else 0, coverage_vector))

    def reset_coverage(self):
        self.request_handler.reset_coverage()

    def get_state_coverage_vector(self):
        state_coverage_vector = self.request_handler.get_state_coverage_vector()
        return list(map(lambda c: 300 if c > 0 else 0, state_coverage_vector))


def do_or_operation(l1, l2):
    l1 = [x + y for x, y in zip(l1, l2)]
    return l1

