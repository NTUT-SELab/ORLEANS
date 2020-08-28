import os
import time
from subprocess import (Popen, SubprocessError, PIPE)
from server_instance.i_server_instance_manager import ServerInstanceManager
import Example.server_instance.server_instance_helper as server_instance_helper


class TimeOffManagementServer(ServerInstanceManager):
    def __init__(self, server_port=3000):
        self._server_port = server_port
        self._dockerFolder = os.getcwd() + "/dockerFile/"
        self._compose_file = ""
        self._MAXIMUM_WAITING_COUNT = 20
        self._MAXIMUM_WAITING_TIMEOUT = 20
        self._create_docker_compose_file()

    def create_server_instance(self):
        waiting_count = 0
        self._create_server()
        while not server_instance_helper.is_server_active(self._server_port):
            time.sleep(0.5)
            waiting_count += 1
            if waiting_count == self._MAXIMUM_WAITING_COUNT:
                self._find_busy_process_and_kill_it()
                self._recreate_time_off_management()
            elif waiting_count == self._MAXIMUM_WAITING_COUNT * 2:
                raise RuntimeError("Something went wrong when creating Timeoff-management...")

    def close_server_instance(self):
        close_process = Popen(['docker-compose', '-f', self._compose_file, 'rm', '-svf'], stdout=PIPE)
        close_process.communicate(timeout=self._MAXIMUM_WAITING_TIMEOUT)

    def _create_docker_compose_file(self):
        self._create_docker_file_folder()
        compose_file_content = 'timeoff_management_with_coverage_{id}:\n' \
                               ' image: ntutselab/timeoff_management_with_coverage\n' \
                               ' ports:\n' \
                               '  - "{port}:3000"'
        # ' net: "host"'
        compose_file_content = compose_file_content.format(id=str(self._server_port % 3000),
                                                           port=str(self._server_port))
        self._compose_file = self._dockerFolder + "docker_compose_timeoff_" + str(self._server_port % 3000) + ".yml"
        compose_file = open(self._compose_file, "w+")
        compose_file.write(compose_file_content)
        compose_file.close()

    def _create_docker_file_folder(self):
        try:

            os.mkdir(self._dockerFolder)
        except FileExistsError:
            print("Folder is exist, not going to create it...")
        except OSError:
            raise RuntimeError("Something wrong when create the server_instance folder...")
    def _find_busy_process_and_kill_it(self):
        # reference :
        #   https://success.docker.com/article/how-to-find-and-resolve-devicemapper-device-or-resource-busy-error
        container_id = self._find_busy_process()
        self._kill_busy_process(container_id)

    def _find_busy_process(self):
        container_id, errs = Popen(['docker-compose', '-f', self._compose_file, 'ps', '-q'], stdout=PIPE).communicate()
        print("find the container id is :", container_id)
        if errs:
            raise RuntimeError("Environment Index : " + str(self._server_port % 3000),
                               "Something wrong when find busy process...")
        return container_id

    def _kill_busy_process(self, container_id):
        fix_device_error_script = os.getcwd() + "/Example/server_instance/find-busy-mnt.sh"
        _, errs = Popen(['sh', fix_device_error_script, container_id]).communicate()
        if errs:
            raise RuntimeError("Environment Index : " + str(self._server_port % 3000),
                               "Something wrong when kill busy process...")

    def _create_server(self):
        create_process = Popen(["docker-compose", "-f", self._compose_file, "up", "-d"])
        start_time = time.time()
        try:
            comment, errs = create_process.communicate(timeout=self._MAXIMUM_WAITING_TIMEOUT)
            print("\nServer Port is", self._server_port, ", Waiting time is :", time.time() - start_time)
            print("Server Port is", self._server_port, "The comment is : ", comment)
            print("Server Port is", self._server_port, "The error is : ", errs)
        except SubprocessError:
            # 1st kind of fix
            print("Something wrong when re-create server_instance... try again!!")
            create_process.kill()
            create_process.communicate()

            # 2nd kind of fix
            # reference :
            #   https://success.docker.com/article/how-to-find-and-resolve-devicemapper-device-or-resource-busy-error
            # self._find_busy_process_and_kill_it()
            # _, errs = create_process.communicate(timeout=self._MAXIMUM_WAITING_TIMEOUT)
            #
            # if errs is not None:
            #     raise RuntimeError("Something wrong when re-create server_instance...")

    def _recreate_time_off_management(self):
        self.close_server_instance()
        self._create_server()



