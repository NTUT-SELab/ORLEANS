import abc


class ServerInstanceManager(abc.ABC):
    @abc.abstractmethod
    def create_server_instance(self):
        """
        create server instance
        """
        pass

    @abc.abstractmethod
    def close_server_instance(self):
        """
        close server instance
        """
        pass


class DefaultServerInstanceManager(ServerInstanceManager):
    def create_server_instance(self):
        raise NotImplementedError

    def close_server_instance(self):
        raise NotImplementedError
