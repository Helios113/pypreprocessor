from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py


class BuildPy(build_py):
    def run(self):
        super().run()

        name = "install.pth"
        input_file = Path("src/pypreprocessor") / name
        output_file = Path(self.build_lib) / name
        # install path configuration file
        self.copy_file(str(input_file), str(output_file), preserve_mode=0)


setup(
    cmdclass={"build_py": BuildPy},
)
