import docker
from docker.errors import DockerException

from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.ptvenv_components import PtVenvConfig
from pytoolbelt.core.project.tool_components import ToolConfig
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools.noxtemplating import NoxfileTemplater, PytestIniTemplater
from pytoolbelt.environment.config import get_logger

logger = get_logger(__name__)


class TestController:
    def __init__(self, ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig) -> None:
        self.ptc = ptc
        self.toolbelt = toolbelt
        self.toolbelt_paths = ToolbeltPaths(toolbelt_root=toolbelt.path)

    def pull(self) -> int:
        docker_client = docker.from_env()
        try:
            logger.info(f"Pulling image {self.ptc.test_image}...")
            _ = docker_client.images.pull(self.ptc.test_image)
        except DockerException:
            raise PytoolbeltError(f"Failed to pull image {self.ptc.test_image}")

        logger.info(f"Successfully pulled image {self.ptc.test_image}")
        return 0

    def list(self) -> None:
        docker_client = docker.from_env()

        container = docker_client.containers.run(
            image=self.ptc.test_image, command="nox --list -f /code/noxfile.py", volumes={self.toolbelt_paths.toolbelt_dir: {"bind": "/code", "mode": "rw"}}
        )
        logger.info(f"Container output: {container.decode()}")

    def run(self) -> int:
        logger.info("Running test command")
        docker_client = docker.from_env()

        try:
            container = docker_client.containers.run(
                image=self.ptc.test_image,
                command="nox",
                volumes={self.toolbelt_paths.toolbelt_dir: {"bind": "/code", "mode": "rw"}},
                detach=True,
                working_dir="/code",
            )

            for log in container.logs(stream=True):
                logger.info(log.decode().strip())
            container.wait()

        except DockerException:
            raise PytoolbeltError("Failed to run test command")
        return 0

    def render(self) -> int:
        logger.info("Rendering noxfile.py")

        ptvenv_configs = {}
        for p in self.toolbelt_paths.ptvenvs_dir.iterdir():
            config = PtVenvConfig.from_file(p / f"{p.name}.yml")
            ptvenv_configs[config.name] = {"config": config, "tools": []}

        for t in self.toolbelt_paths.tools_dir.iterdir():
            config = ToolConfig.from_file(t / "config.yml")

            if config.ptvenv.name in ptvenv_configs:
                ptvenv_configs[config.ptvenv.name]["tools"].append(config)

        self.toolbelt_paths.noxfile.touch(exist_ok=True)
        self.toolbelt_paths.pytest_ini.touch(exist_ok=True)

        nox_templater = NoxfileTemplater()
        noxfile = nox_templater.render_noxfile(ptvenv_configs)
        self.toolbelt_paths.noxfile.write_text(noxfile)

        logger.info("Rendering pytest.ini")
        pytest_templater = PytestIniTemplater()
        tools = [t.name for t in self.toolbelt_paths.tools_dir.iterdir() if t.is_dir()]
        pytest_ini = pytest_templater.render_pytest_ini(tools=tools)
        self.toolbelt_paths.pytest_ini.write_text(pytest_ini)

        return 0
