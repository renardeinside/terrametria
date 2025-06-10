from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from pathlib import Path
import subprocess
import shutil


class YarnBuildHook(BuildHookInterface):
    def initialize(self, _, __):
        self.app.display_info(
            f"Running build hook for project {self.metadata.name} in directory {Path.cwd()}"
        )

        process = subprocess.Popen(
            ["yarn", "--cwd", "src/frontend", "build"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        for line in process.stdout:
            self.app.display_info(line, end="")

        for line in process.stderr:
            self.app.display_error(line, end="")

        process.wait()

    def finalize(self, version, build_data, artifact_path):
        self.app.display_info(
            f"Finalizing build hook for project {self.metadata.name} in directory {Path.cwd()} with artifact path {artifact_path}"
        )
        # cleanup the .build directory
        build_dir = Path.cwd() / ".build"
        if build_dir.exists():
            self.app.display_info(f"Removing {build_dir}")
            shutil.rmtree(build_dir)

        # copy the build artifacts to the .build directory
        self.app.display_info(f"Copying build artifacts to {build_dir}")
        artifact_path = Path(artifact_path)
        shutil.copytree(artifact_path.parent, build_dir)

        # write .build/requirements.txt with artifact path
        reqs_file = build_dir / "requirements.txt"
        reqs_file.write_text(f"{artifact_path.name}\n")

        self.app.display_info(f"Build dir {build_dir} is ready for deployment")