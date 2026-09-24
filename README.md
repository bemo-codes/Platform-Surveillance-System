# Platform Surveillance System

A Python-based system monitoring and automation tool that periodically collects system information, generates detailed log files, and sends an email alert when CPU utilization reaches a defined threshold.

## Features

- Monitors CPU utilization
- Monitors RAM utilization
- Reports total, used, and available RAM
- Monitors disk usage
- Monitors network data transfer
- Scans currently running processes
- Records process CPU and RAM usage
- Generates timestamped system reports
- Automatically executes at a configurable interval
- Sends email alerts when CPU utilization reaches 80%
- Uses environment variables to protect email credentials
- Accepts configuration through command-line arguments
- Handles processes that terminate during scanning

## Technologies Used

- Python
- psutil
- schedule
- smtplib
- email
- os
- sys
- time

## Project Structure

```text
Platform-Surveillance-System/
│
├── PlatformSurveillance_Process_Log.py
├── requirements.txt
├── .gitignore
├── README.md
└── Logs/