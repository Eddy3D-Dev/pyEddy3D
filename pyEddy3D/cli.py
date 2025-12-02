import argparse
import logging
from pathlib import Path

from colorama import init

from pyEddy3D.simulation import Simulation

# Initialize colorama
init(autoreset=True)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Eddy3D simulations.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="Path to the simulation directory (default: current directory)",
    )
    args = parser.parse_args()

    print("Analyzing directory with pyEddy3D...")
    s = Simulation(args.path)
    s.analyze()


if __name__ == "__main__":
    main()
