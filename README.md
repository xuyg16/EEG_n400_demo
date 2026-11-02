
## Setup and Usage

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency management.

### 1. Install uv

If uv is not installed, follow the [installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

### 2. Set up the environment

Clone the repository and install the dependencies:

```bash
git clone <repository-url>
cd EEG_n400_demo
uv sync
```

### 3. Run the experiment

```bash
uv run python n400_experiment.py
```

Enter a participant ID when prompted. Press **Space** to start the experiment.

- **Left arrow:** Related
- **Right arrow:** Unrelated
- **Escape:** Exit the experiment

### 4. Event Markers and Behavioral Data
"condition": "related",
"marker": 1
"True": 1


"condition": "unrelated",
"marker": 2
"False": 0