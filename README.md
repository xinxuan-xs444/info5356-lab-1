# INFO 5356 Lab 1: Reachy Mini

## Team Members
Vishnupriya Rayaprolu - vr362

Xinxuan shen - xs444

## Overview
This repository contains our team's work for Lab 1, covering Reachy Mini installation,
simulation testing, and development of a custom greeting application (`team_greeting_app`)

## Environment Setup

- **Operating System:** macOS 15.6.1 (Build 24G90) - Vishnu; Ubuntu 24.04.4 LTS (Nobel Numbat) - Xinxuan
- **Architecture:** arm64 (Apple Silicon) - Vishnu; x86_64 (64-bit) - Xinxuan
- **Python Version:** 3.12.1
- **Reachy Mini SDK Version:** 1.10.0
- **MuJoCo Version:** 3.3.0

## Repository Structure
```
apps
├──team_greeting_app
    ├── index.html              # Hugging Face Space landing page
    ├── style.css               # Landing page styles
    ├── pyproject.toml          # Package config with entry points
    ├── README.md               # Must contain reachy_mini_python_app tag
    └── team_greeting_app
        ├── __init__.py
        ├── main.py             # Your app logic
        └── static/             # Optional web UI
            ├── index.html
            ├── style.css
            └── main.js
.gitignore
README.md
```
