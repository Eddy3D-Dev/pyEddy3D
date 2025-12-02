[![Python application](https://github.com/kastnerp/Eddy3D-SimCompleted/actions/workflows/python-app.yml/badge.svg)](https://github.com/kastnerp/Eddy3D-SimCompleted/actions/workflows/python-app.yml)

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

## Related repositories

https://github.com/kastnerp/Eddy3D-Helperfunctions  
https://github.com/kastnerp/Eddy3D-Issues  
https://github.com/kastnerp/Eddy3D-SimCompleted  
https://github.com/kastnerp/Eddy3D-Residuals  
https://github.com/kastnerp/Eddy3D-CaseStudies  
