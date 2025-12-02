from enum import Enum


class Status(Enum):
    COMPLETED = 0
    CRASHED = 1
    NOT_STARTED = 2
    CONVERGED = 3
    IN_PROGRESS = 4
    NOT_CHECKED = 5
    MESH_CRASHED = 6
