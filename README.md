# ACI to Apstra Converter

A tool for converting an ACI APIC configuration to an Apstra configuration, outputted as a Terraform configuration.

## Getting Started

These instructions will help you set up and run the project on your local machine.

## Prerequisites

You need to have the following installed:
- Python 3.x
- Required Python packages (listed in `requirements.txt`)

## Installing

Follow these steps to set up the development environment:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/aci-to-apstra.git
    cd aci-to-apstra
    ```

2. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Project

To run the project, the user must download the APIC configuration JSON file directly from the APIC appliance.

Once the APIC config JSON is downloaded, run the following command:
```bash
python3 src/main.py
```

## Deployment

Additional notes on how to deploy this project on a live system will be provided here.

## Built With

* Python - The main programming language used
* Jinja2 - Template engine for Python
* Terraform - Infrastructure as Code tool

## Authors

* Adam Jarvis
* Mohamed Abouzeina

## License

This project is licensed under the MIT License - see the LICENSE file for details.