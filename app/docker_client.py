import database
import docker
import time

client = docker.from_env()


def run_command(task: database.Task):
    try:
        logs = ""
        image = task.image
        command = task.command
        start_t = time.time()
        container = client.containers.run(image, command, detach=True)
        for line in container.logs(stream=True):
            logs = logs + line.strip().decode("utf-8") + "\n"
        end_t = time.time()
        exec_time = end_t - start_t
        task.status = "finished"
        task.logs = logs
        task.execution_time = str(exec_time)
        task.save()
    except docker.errors.APIError:
        task.status = "failed"
        task.save()
