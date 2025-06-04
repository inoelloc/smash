import argparse
import os
import re
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        nargs="+",
        type=str,
        help="Paths to files in order to generate f2py-f90wrap files",
    )
    parser.add_argument(
        "--build-dir",
        default=".",
        type=str,
        help="All f2py-f90wrap generated files are created in this directory",
        required=False,
    )
    args = parser.parse_args()

    cmd_args = [
        "f2py-f90wrap", "--build-dir", args.build_dir, "--lower", "-m", "_libfcore"
    ]
    cmd_args.extend(args.files)
    subprocess.run(cmd_args, check=True)

    if sys.platform == "win32":
        libfile = os.path.join(args.build_dir, "_libfcoremodule.c")
        with open(libfile, "r+") as f:
            buffer = f.read()
            buffer = re.sub("setjmpex", "setjmp", buffer, flags=re.DOTALL)
            f.seek(0)
            f.write(buffer)

if __name__ == "__main__":
    main()
