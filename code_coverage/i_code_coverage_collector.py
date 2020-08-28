import abc


class CodeCoverageCollector(abc.ABC):
    @abc.abstractmethod
    def __init__(self, server_port):
        """
        Give the port number, let coverage collector know which server he want to get
        :param server_port:
        """
        pass

    @abc.abstractmethod
    def reset_coverage(self):
        """
        reset the coverage
        """
        pass

    @abc.abstractmethod
    def get_coverage_vector(self):
        """
        get the coverage vector, which type is List<int>
        :return:
            coverage_vector : List<int>
        """
        pass


class DefaultCoverageCollector(CodeCoverageCollector):
    def __init__(self, server_port):
        super().__init__(server_port)

    def reset_coverage(self):
        raise NotImplementedError

    def get_coverage_vector(self):
        raise NotImplementedError
