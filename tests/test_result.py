import pathlib
import unittest
from pyEddy3D.simulation import Simulation


class TestSimCompleted(unittest.TestCase):
    def fix_cwd(self, p: str) -> pathlib.Path:
        cwd = pathlib.Path.cwd()
        # If we are running from the root, append 'tests'
        if cwd.name != "tests":
            base_path = cwd / "tests"
        else:
            base_path = cwd
        
        path = base_path / p
        return path

    def printout(self, s: Simulation) -> None:
        print(f"Mesh Crashed {s.n_mesh_crashed}")
        print(f"Crashed {s.n_crashed}")
        print(f"Completed {s.n_completed}")
        print(f"In progress {s.n_inprogress}")
        print(f"Not started {s.n_not_started}")
        print(f"Converged {s.n_converged}")

    def test_crashed(self) -> None:
        folder = "12_Case_Type_Slab_NS_Height_30_Dist_20_dir_0_crashed"
        path = self.fix_cwd(folder)

        s = Simulation(path)
        s.analyze()

        self.printout(s)

        self.assertEqual(1, s.n_crashed)
        self.assertEqual(0, s.n_mesh_crashed)
        self.assertEqual(0, s.n_completed)
        self.assertEqual(0, s.n_inprogress)
        self.assertEqual(0, s.n_not_started)
        self.assertEqual(0, s.n_converged)

    def test_crashed_2(self) -> None:
        folder = "Case_36_crashed"
        path = self.fix_cwd(folder)

        s = Simulation(path)
        s.analyze()

        self.printout(s)

        self.assertEqual(1, s.n_crashed)
        self.assertEqual(0, s.n_mesh_crashed)
        self.assertEqual(0, s.n_completed)
        self.assertEqual(0, s.n_inprogress)
        self.assertEqual(0, s.n_not_started)
        self.assertEqual(0, s.n_converged)

    def test_mesh_crashed(self) -> None:
        folder = "Case_17_m_crashed"
        path = self.fix_cwd(folder)

        s = Simulation(path)
        s.analyze()

        self.printout(s)

        self.assertEqual(0, s.n_crashed)
        self.assertEqual(1, s.n_mesh_crashed)
        self.assertEqual(0, s.n_completed)
        self.assertEqual(0, s.n_inprogress)
        self.assertEqual(0, s.n_not_started)
        self.assertEqual(0, s.n_converged)

    def test_completed(self) -> None:
        folder = "6_Case_Type_Scatter_Height_20_Dist_20_dir_30_completed"
        path = self.fix_cwd(folder)

        s = Simulation(path)
        s.analyze()

        self.printout(s)

        self.assertEqual(0, s.n_crashed)
        self.assertEqual(0, s.n_mesh_crashed)
        self.assertEqual(1, s.n_completed)
        self.assertEqual(0, s.n_inprogress)
        self.assertEqual(0, s.n_not_started)
        self.assertEqual(0, s.n_converged)

    def test_in_progress(self) -> None:
        folder = "6_Case_Type_Scatter_Height_20_Dist_20_dir_40_inprogress"
        path = self.fix_cwd(folder)

        s = Simulation(path)
        s.analyze()

        self.printout(s)

        self.assertEqual(0, s.n_crashed)
        self.assertEqual(0, s.n_mesh_crashed)
        self.assertEqual(0, s.n_completed)
        self.assertEqual(1, s.n_inprogress)
        self.assertEqual(0, s.n_not_started)
        self.assertEqual(0, s.n_converged)

    def test_converged(self) -> None:
        folder = "6_Case_Type_Scatter_Height_20_Dist_20_dir_40_converged"
        path = self.fix_cwd(folder)

        s = Simulation(path)
        s.analyze()

        self.printout(s)

        self.assertEqual(0, s.n_crashed)
        self.assertEqual(0, s.n_mesh_crashed)
        self.assertEqual(1, s.n_completed)
        self.assertEqual(0, s.n_inprogress)
        self.assertEqual(0, s.n_not_started)
        self.assertEqual(1, s.n_converged)

    def test_not_started(self) -> None:
        folder = "6_Case_Type_Scatter_Height_20_Dist_20_dir_40_notstarted"
        path = self.fix_cwd(folder)

        s = Simulation(path)
        s.analyze()

        self.printout(s)

        self.assertEqual(0, s.n_crashed)
        self.assertEqual(0, s.n_mesh_crashed)
        self.assertEqual(0, s.n_completed)
        self.assertEqual(0, s.n_inprogress)
        self.assertEqual(1, s.n_not_started)
        self.assertEqual(0, s.n_converged)

    def test_all(self) -> None:
        # This test assumes it's running from the root of the repo where 'tests' folder is visible
        # or from inside 'tests' folder.
        # However, Simulation default init uses Path.cwd().
        # If we run from root, cwd is root.
        # If we run from tests, cwd is tests.
        # We need to make sure we point to the tests directory if we want to scan it.
        
        cwd = pathlib.Path.cwd()
        if cwd.name != "tests":
            target_dir = cwd / "tests"
        else:
            target_dir = cwd

        s = Simulation(target_dir)
        s.analyze()

        self.printout(s)

        self.assertEqual(2, s.n_crashed)
        self.assertEqual(1, s.n_mesh_crashed)
        self.assertEqual(2, s.n_completed)
        self.assertEqual(1, s.n_inprogress)
        self.assertEqual(1, s.n_not_started)
        self.assertEqual(1, s.n_converged)

    def test_all_in_progress(self) -> None:
        cwd = pathlib.Path.cwd()
        if cwd.name != "tests":
            target_dir = cwd / "tests"
        else:
            target_dir = cwd
            
        s = Simulation(target_dir)
        s.analyze()

        self.printout(s)
        self.assertEqual(1, s.n_inprogress)

    def test_all_not_started(self) -> None:
        cwd = pathlib.Path.cwd()
        if cwd.name != "tests":
            target_dir = cwd / "tests"
        else:
            target_dir = cwd
            
        s = Simulation(target_dir)
        s.analyze()

        self.printout(s)
        self.assertEqual(1, s.n_not_started)

    def test_all_completed(self) -> None:
        cwd = pathlib.Path.cwd()
        if cwd.name != "tests":
            target_dir = cwd / "tests"
        else:
            target_dir = cwd
            
        s = Simulation(target_dir)
        s.analyze()

        self.printout(s)
        self.assertEqual(2, s.n_completed)

    def test_all_crashed(self) -> None:
        cwd = pathlib.Path.cwd()
        if cwd.name != "tests":
            target_dir = cwd / "tests"
        else:
            target_dir = cwd
            
        s = Simulation(target_dir)
        s.analyze()

        self.printout(s)

        self.assertEqual(2, s.n_crashed)
        self.assertEqual(1, s.n_mesh_crashed)

    def test_all_simfolders(self) -> None:
        cwd = pathlib.Path.cwd()
        if cwd.name != "tests":
            target_dir = cwd / "tests"
        else:
            target_dir = cwd
            
        s = Simulation(target_dir)
        s.analyze()

        self.printout(s)

        self.assertEqual(7, s.number_sim_dirs)


if __name__ == "__main__":
    unittest.main()
