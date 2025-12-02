#!/usr/bin/env python

import os
import re
from enum import Enum
from pathlib import Path
from typing import List, Tuple, Optional

from colorama import init
from termcolor import colored

# Initialize colorama
init(autoreset=True)


class Status(Enum):
    COMPLETED = 0
    CRASHED = 1
    NOT_STARTED = 2
    CONVERGED = 3
    IN_PROGRESS = 4
    NOT_CHECKED = 5
    MESH_CRASHED = 6


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
        self.subdirs = self.get_subdirs(self.cwd)
        self.control_dicts, self.end_iteration = self.get_control_dicts(self.cwd)
        self.sim_dirs, self.last_iters = self.get_last_iterations(self.control_dicts)

        for cnt, dir_path in enumerate(self.sim_dirs):
            self.check_case_status(Path(dir_path), cnt)
            self.print_status(dir_path)

        self.n_completed = len(self.cases_completed) + len(self.cases_converged)
        self.n_crashed = len(self.cases_crashed)
        self.n_mesh_crashed = len(self.cases_mesh_crashed)
        self.n_converged = len(self.cases_converged)
        self.n_not_started = len(self.cases_not_started)
        self.n_inprogress = len(self.cases_inprogress)
        self.number_sim_dirs = len(self.sim_dirs)

        self.ratio = (
            self.n_completed / self.number_sim_dirs if self.number_sim_dirs != 0 else 0
        )

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
                # Assuming Windows path structure based on original code
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

    def print_status(self, current_dir: str) -> None:
        if self.sim_status == Status.CONVERGED:
            self.cases_converged.append(current_dir)
            print(f"{current_dir} - {colored('Converged', 'green')}")

        elif self.sim_status == Status.IN_PROGRESS:
            self.cases_inprogress.append(current_dir)
            print(
                f"{current_dir} - "
                f"{colored(str(round(self.current_iteration, 1)) + '% Done', 'cyan')}"
            )

        elif self.sim_status == Status.NOT_STARTED:
            self.cases_not_started.append(current_dir)
            print(f"{current_dir} - {colored('Not Started', 'white')}")

        elif self.sim_status == Status.CRASHED:
            self.cases_crashed.append(current_dir)
            print(f"{current_dir} - {colored('Crashed', 'red')}")

        elif self.sim_status == Status.MESH_CRASHED:
            self.cases_mesh_crashed.append(current_dir)
            print(f"{current_dir} - {colored('Meshes Crashed', 'red')}")

        elif self.sim_status == Status.COMPLETED:
            self.cases_completed.append(current_dir)
            print(f"{current_dir} - {colored('Done', 'cyan')}")

    def check_case_status(self, dir_path: Path, cnt: int) -> None:
        self.check_case_progress(cnt)
        self.check_if_converged(dir_path)

    def check_if_done(self, dir_path: Path) -> None:
        if dir_path.is_dir():
            # Checking if the directory is empty or not
            if any(dir_path.iterdir()):
                self.sim_status = Status.COMPLETED

    def get_subdirs(self, path: Path) -> List[str]:
        return [f.name for f in path.iterdir() if f.is_dir()]

    def get_control_dicts(self, cwd: Path) -> Tuple[List[str], List[str]]:
        control_dicts = []
        end_times = []
        for root, dirs, files in os.walk(cwd):
            for file in files:
                if file.startswith("controlDict") and "mesh" not in str(root):
                    p = os.path.join(root, file)
                    control_dicts.append(p)
                    try:
                        with open(p, "r") as fp:
                            for line in fp:
                                if "endTime" in str(line):
                                    words = re.split(r"\s+", line)
                                    # Ensure we have enough words and the value is numeric
                                    if len(words) > 2:
                                        val = words[2].split(";")[0]
                                        if val.replace(".", "", 1).isdigit():
                                            end_times.append(val)
                    except Exception as e:
                        print(f"Error reading {p}: {e}")

        return control_dicts, end_times

    def get_last_iterations(
        self, control_dicts: List[str]
    ) -> Tuple[List[str], List[int]]:
        sim_dirs = []
        last_iters = []

        for d in control_dicts:
            path = os.sep.join(d.split(os.sep)[0:-2])
            sim_dirs.append(path)
            
            # Use pathlib for more robust directory listing
            path_obj = Path(path)
            last_iter = 0
            if path_obj.exists():
                for el in path_obj.iterdir():
                    if el.is_dir() and el.name.isdigit():
                        if int(el.name) > last_iter:
                            last_iter = int(el.name)
            last_iters.append(last_iter)

        return sim_dirs, last_iters

    def check_case_progress(self, cnt: int) -> None:
        if cnt < len(self.last_iters) and cnt < len(self.end_iteration):
            try:
                end_iter = float(self.end_iteration[cnt])
                if end_iter == 0:
                    progress = 0.0
                else:
                    progress = float(self.last_iters[cnt]) / end_iter * 100
            except ValueError:
                progress = 0.0
        else:
            progress = 0.0

        if 0 < progress < 100:
            self.sim_status = Status.IN_PROGRESS
            self.current_iteration = progress

        elif progress >= 100:
            self.sim_status = Status.COMPLETED
            self.current_iteration = progress

        else:
            self.sim_status = Status.NOT_STARTED

    def check_if_converged(self, dir_path: Path) -> None:
        # Check if converged
        logfile = dir_path / "log"
        if logfile.is_file():
            try:
                with open(logfile, "r") as fp:
                    lines = fp.readlines()
                    for line in lines:
                        if "SIMPLE solution converged in" in str(line):
                            match = re.search(r"\d+", line)
                            if match:
                                iteration = int(match.group())
                                if iteration < 1000:  # make dependent from endtime
                                    self.sim_status = Status.MESH_CRASHED
                                else:
                                    self.sim_status = Status.CONVERGED
                            break
                        elif "job aborted:" in str(line):
                            self.sim_status = Status.CRASHED
                        elif "simpleFoam ended prematurely and may have crashed" in str(
                            line
                        ):
                            self.sim_status = Status.CRASHED
                        elif "[0] process exited without calling finalize" in str(line):
                            self.sim_status = Status.CRASHED
                        elif "---- error analysis ----" in str(line):
                            self.sim_status = Status.CRASHED
                        elif "Finalising parallel run" in str(line):
                            self.sim_status = Status.COMPLETED
                            break
            except Exception as e:
                print(f"Error reading logfile {logfile}: {e}")

