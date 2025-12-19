[![Python tests](https://github.com/Eddy3D-Dev/pyEddy3D/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Eddy3D-Dev/pyEddy3D/actions/workflows/python-tests.yml)
[![GitHub release](https://img.shields.io/github/v/release/Eddy3D-Dev/pyEddy3D)](https://github.com/Eddy3D-Dev/pyEddy3D/releases)

# pyEddy3D

A Python tool to check the status of Eddy3D simulations.

## Installation

This project is managed with `uv`.

### Prerequisites

- [uv](https://github.com/astral-sh/uv)

### Install from Source

```bash
git clone https://github.com/kastnerp/pyEddy3D.git
cd pyEddy3D
uv sync
```

## Usage

You can run the tool using `uv run`:

```bash
# Analyze the current directory
uv run pyeddy3d

# Analyze a specific directory
uv run pyeddy3d /path/to/simulations
```

## Development

### Run Tests

```bash
uv run pytest
```
