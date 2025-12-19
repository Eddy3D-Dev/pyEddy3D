import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from termcolor import colored

from pyEddy3D.status import Status

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CaseData:
    control_dict: Path
    sim_dir: Path
    end_time: float
    last_iteration: int

    @property
    def log_file(self) -> Path:
        return self.sim_dir / "log"


@dataclass(frozen=True)
class CaseResult:
    case: CaseData
    status: Status
    progress: float


class Simulation:
    def __init__(self, root_folder: Optional[Path] = None) -> None:
        self.cwd: Path = root_folder if root_folder is not None else Path.cwd()

        self.subdirs: List[str] = []
        self.control_dicts: List[str] = []
        self.end_iteration: List[str] = []
        self.sim_dirs: List[str] = []
        self.last_iters: List[int] = []

        self.sim_status: Status = Status.NOT_CHECKED

        self.cases_completed: List[str] = []
        self.cases_crashed: List[str] = []
        self.cases_mesh_crashed: List[str] = []
        self.cases_not_started: List[str] = []
        self.cases_inprogress: List[str] = []
        self.cases_converged: List[str] = []

        self.current_iteration: float = 0.0
        self.n_completed: int = 0
        self.n_crashed: int = 0
        self.n_mesh_crashed: int = 0
        self.n_converged: int = 0
        self.n_not_started: int = 0
        self.n_inprogress: int = 0
        self.number_sim_dirs: int = 0
        self.ratio: float = 0.0

    def analyze(self) -> None:
        self._reset_results()

        cases = self._collect_cases(self.cwd)
        self.subdirs = self.get_subdirs(self.cwd)
        self.control_dicts = [str(case.control_dict) for case in cases]
        self.end_iteration = [str(case.end_time) for case in cases]
        self.sim_dirs = [str(case.sim_dir) for case in cases]
        self.last_iters = [case.last_iteration for case in cases]
        self.number_sim_dirs = len(cases)

        for case in cases:
            result = self._evaluate_case(case)
            self.sim_status = result.status
            self.current_iteration = result.progress
            self._record_result(result)
            self.print_status(str(case.sim_dir), result.status, result.progress)

        self._finalize_counts()
        self.print_verdict()

    def print_verdict(self) -> None:
        string_done = (
            f"{self.n_completed} out of {self.number_sim_dirs} "
            f"simulations done or {round(100 * self.ratio, 1)}%"
        )
        print(colored(string_done, "green"))

        if self.ratio > 0:
            print("\n###")
            print("\nCrashed Cases:", str(self.n_crashed))

            for i in self.cases_crashed:
                print("start", i)

            print("\n###")
            print("\nNot started:", str(self.n_not_started))

            for i in self.cases_not_started:
                parts = str(i).split(os.sep)
                if len(parts) > 1:
                    print(os.sep.join(parts[:-1]) + os.sep + "run.bat")
                else:
                    print(str(i) + os.sep + "run.bat")

            print("\n###")
            print("\nRename cases remaining")
            for i in self.cases_not_started:
                parts = str(i).split(os.sep)
                base_path = os.sep.join(parts[:-1])
                print(
                    f"ren {base_path}"
                    r"\\Batch_ESLTower64\_mesh_and_sim_ESLTower64.bat _mesh_and_sim_ESLTower64_next.bat"
                )

    def print_status(
        self,
        current_dir: str,
        status: Optional[Status] = None,
        progress: Optional[float] = None,
    ) -> None:
        case_status = status or self.sim_status
        current_progress = progress if progress is not None else self.current_iteration

        if case_status == Status.CONVERGED:
            print(f"{current_dir} - {colored('Converged', 'green')}")

        elif case_status == Status.IN_PROGRESS:
            print(
                f"{current_dir} - "
                f"{colored(str(round(current_progress, 1)) + '% Done', 'cyan')}"
            )

        elif case_status == Status.NOT_STARTED:
            print(f"{current_dir} - {colored('Not Started', 'white')}")

        elif case_status == Status.CRASHED:
            print(f"{current_dir} - {colored('Crashed', 'red')}")

        elif case_status == Status.MESH_CRASHED:
            print(f"{current_dir} - {colored('Meshes Crashed', 'red')}")

        elif case_status == Status.COMPLETED:
            print(f"{current_dir} - {colored('Done', 'cyan')}")

    def get_subdirs(self, path: Path) -> List[str]:
        return [f.name for f in path.iterdir() if f.is_dir()]

    def get_control_dicts(self, cwd: Path) -> Tuple[List[str], List[str]]:
        cases = self._collect_cases(cwd)
        control_dicts = [str(case.control_dict) for case in cases]
        end_times = [str(case.end_time) for case in cases]
        return control_dicts, end_times

    def get_last_iterations(
        self, control_dicts: List[str]
    ) -> Tuple[List[str], List[int]]:
        sim_dirs = []
        last_iters = []

        for control_dict in control_dicts:
            sim_dir = Path(control_dict).parent.parent
            sim_dirs.append(str(sim_dir))
            last_iters.append(self._find_last_iteration(sim_dir))

        return sim_dirs, last_iters

    def _reset_results(self) -> None:
        self.subdirs = []
        self.control_dicts = []
        self.end_iteration = []
        self.sim_dirs = []
        self.last_iters = []

        self.cases_completed = []
        self.cases_crashed = []
        self.cases_mesh_crashed = []
        self.cases_not_started = []
        self.cases_inprogress = []
        self.cases_converged = []

        self.current_iteration = 0.0
        self.n_completed = 0
        self.n_crashed = 0
        self.n_mesh_crashed = 0
        self.n_converged = 0
        self.n_not_started = 0
        self.n_inprogress = 0
        self.number_sim_dirs = 0
        self.ratio = 0.0
        self.sim_status = Status.NOT_CHECKED

    def _collect_cases(self, cwd: Path) -> List[CaseData]:
        cases: List[CaseData] = []
        for control_dict in cwd.rglob("controlDict*"):
            if "mesh" in control_dict.parts:
                continue

            end_time = self._parse_end_time(control_dict)
            sim_dir = control_dict.parent.parent
            last_iteration = self._find_last_iteration(sim_dir)
            cases.append(
                CaseData(
                    control_dict=control_dict,
                    sim_dir=sim_dir,
                    end_time=end_time,
                    last_iteration=last_iteration,
                )
            )

        return cases

    def _evaluate_case(self, case: CaseData) -> CaseResult:
        progress = self._calculate_progress(case.end_time, case.last_iteration)
        status = self._status_from_progress(progress)
        status = self._status_from_log(case.log_file, status)
        return CaseResult(case=case, status=status, progress=progress)

    def _parse_end_time(self, control_dict: Path) -> float:
        end_time = 0.0
        try:
            with control_dict.open("r") as fp:
                for line in fp:
                    if "endTime" not in line:
                        continue

                    match = re.search(r"([-+]?\d*\.?\d+)", line)
                    if match:
                        end_time = float(match.group(1))
                        break
        except Exception as exc:
            logger.error(f"Error reading {control_dict}: {exc}")

        return end_time

    def _find_last_iteration(self, sim_dir: Path) -> int:
        last_iter = 0
        if sim_dir.exists():
            for el in sim_dir.iterdir():
                if el.is_dir() and el.name.isdigit():
                    last_iter = max(last_iter, int(el.name))
        return last_iter

    def _calculate_progress(self, end_time: float, last_iteration: int) -> float:
        if end_time <= 0:
            return 0.0
        return float(last_iteration) / end_time * 100

    def _status_from_progress(self, progress: float) -> Status:
        if 0 < progress < 100:
            return Status.IN_PROGRESS
        if progress >= 100:
            return Status.COMPLETED
        return Status.NOT_STARTED

    def _status_from_log(self, logfile: Path, current_status: Status) -> Status:
        status = current_status

        if logfile.is_file():
            try:
                with logfile.open("r") as fp:
                    for line in fp:
                        if "SIMPLE solution converged in" in line:
                            match = re.search(r"\d+", line)
                            if match:
                                iteration = int(match.group())
                                if iteration < 1000:
                                    return Status.MESH_CRASHED
                                return Status.CONVERGED
                        elif "job aborted:" in line:
                            status = Status.CRASHED
                        elif "simpleFoam ended prematurely and may have crashed" in line:
                            status = Status.CRASHED
                        elif "[0] process exited without calling finalize" in line:
                            status = Status.CRASHED
                        elif "---- error analysis ----" in line:
                            status = Status.CRASHED
                        elif "Finalising parallel run" in line:
                            return Status.COMPLETED
            except Exception as exc:
                logger.error(f"Error reading logfile {logfile}: {exc}")

        return status

    def _record_result(self, result: CaseResult) -> None:
        case_dir = str(result.case.sim_dir)
        status = result.status

        if status == Status.CONVERGED:
            self.cases_converged.append(case_dir)
        elif status == Status.IN_PROGRESS:
            self.cases_inprogress.append(case_dir)
        elif status == Status.NOT_STARTED:
            self.cases_not_started.append(case_dir)
        elif status == Status.CRASHED:
            self.cases_crashed.append(case_dir)
        elif status == Status.MESH_CRASHED:
            self.cases_mesh_crashed.append(case_dir)
        elif status == Status.COMPLETED:
            self.cases_completed.append(case_dir)

    def _finalize_counts(self) -> None:
        self.n_completed = len(self.cases_completed) + len(self.cases_converged)
        self.n_crashed = len(self.cases_crashed)
        self.n_mesh_crashed = len(self.cases_mesh_crashed)
        self.n_converged = len(self.cases_converged)
        self.n_not_started = len(self.cases_not_started)
        self.n_inprogress = len(self.cases_inprogress)

        if self.number_sim_dirs != 0:
            self.ratio = self.n_completed / self.number_sim_dirs
        else:
            self.ratio = 0.0
