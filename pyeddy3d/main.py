from pyeddy3d import SimCompleted


def main() -> None:
    print("Analyzing current directory with pyEddy3D...")
    s = SimCompleted.Simulation()
    s.analyze()


if __name__ == "__main__":
    main()




