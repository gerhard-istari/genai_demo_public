# LM GenAI Workflow Execution

This program is part of the LM GenAI project and executes a workflow that extracts requirements and parameters, validates them, and, if needed, prompts you to update any failing CAD parameter values. Once all parameters meet their requirements, the program finishes with a confirmation message.

## Folder Structure

The repository is organized as follows:

```
lm_genai/
└── genai_demo/
    ├── execute_workflow.py
    ├── components/
    │   ├── extract_requirements.py
    │   ├── extract_parameters.py
    │   ├── update_parameters.py
    │   └── validate_requirements.py
    └── shared/
        ├── helpers.py
        └── constants.py
```

• execute_workflow.py – The main script that runs the workflow.
• components/ – Contains modules for extracting requirements and parameters, performing validations, and updating parameters.
• shared/ – Provides helper functions and constant definitions used across the project.

## Prerequisites
• Python 3.6+
Ensure you have Python installed. You can download it from python.org.
• Dependencies
If a requirements.txt file exists in the repository, install the necessary Python packages using:

`pip install -r requirements.txt`

Otherwise, ensure that any libraries used within the components and shared modules are installed.

## Running the Program
1.	Navigate to the Program Directory
Open your terminal or command prompt and change directory to the genai_demo folder:

`cd /path/to/your/repo/lm_genai/genai_demo`


2.	Run the Workflow Script
Execute the main script by running:

`python execute_workflow.py``


3.	Follow On-Screen Prompts
The script will:
	• Extract and display requirements and parameters.
	• Validate parameter values against the requirements.
	• If any parameter fails to meet its requirement, you will be prompted to update the value.
Simply follow the instructions in your terminal to input new values where necessary.

## Configuration
• Client Setup
The program retrieves a client instance using the get_client() function from the shared/helpers.py module. If the client requires any specific configuration (e.g., API keys or environment variables), make sure these are set up according to your project’s documentation.
• File Paths and Constants
The names and paths for requirement and parameter files are defined in shared/constants.py using the constants REQ_FILE_NAME, PARAM_FILE_NAME, and UPDATE_PARAM_FILE_NAME. Adjust these if your file locations differ.

## Troubleshooting
• Missing Modules:
If you encounter ModuleNotFoundError issues, verify that your Python module search path includes the repository’s root folder or properly install the required packages.
• Dependency Issues:
Ensure all dependencies are installed as expected. If the repository includes a requirements.txt, running the pip installation command should resolve any dependency issues.
• Client Configuration:
Check that any required client or API configuration is properly set in your environment. Refer to your project’s documentation for additional configuration details.

## License

(Include license information if applicable.)



