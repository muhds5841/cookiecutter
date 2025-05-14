#!/usr/bin/env python3
"""Development environment setup script for Process project.

This script automates the setup of a development environment for the Process project,
including installing dependencies, configuring pre-commit hooks, and setting up
environment variables.
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional


def print_step(message: str) -> None:
    """Print a step message with formatting.
    
    Args:
        message: Message to print
    """
    print(f"\n\033[1;34m==>\033[0m \033[1m{message}\033[0m")


def print_success(message: str) -> None:
    """Print a success message with formatting.
    
    Args:
        message: Message to print
    """
    print(f"\033[1;32m✓\033[0m {message}")


def print_error(message: str) -> None:
    """Print an error message with formatting.
    
    Args:
        message: Message to print
    """
    print(f"\033[1;31m✗\033[0m {message}")


def run_command(command: List[str], cwd: Optional[Path] = None) -> bool:
    """Run a shell command.
    
    Args:
        command: Command to run as a list of strings
        cwd: Working directory
        
    Returns:
        True if command succeeded, False otherwise
    """
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(command)}")
        print(f"Error: {e.stderr}")
        return False


def check_dependencies() -> bool:
    """Check if required dependencies are installed.
    
    Returns:
        True if all dependencies are installed, False otherwise
    """
    print_step("Checking dependencies")
    
    dependencies = ["python", "pip", "docker", "docker-compose", "git"]
    all_installed = True
    
    for dep in dependencies:
        try:
            subprocess.run(
                ["which", dep],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print_success(f"{dep} is installed")
        except subprocess.CalledProcessError:
            print_error(f"{dep} is not installed")
            all_installed = False
    
    return all_installed


def install_python_dependencies() -> bool:
    """Install Python dependencies.
    
    Returns:
        True if installation succeeded, False otherwise
    """
    print_step("Installing Python dependencies")
    
    # Check if Poetry is installed
    try:
        subprocess.run(
            ["poetry", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print_success("Poetry is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Poetry not found, installing...")
        if not run_command(["pip", "install", "poetry"]):
            print_error("Failed to install Poetry")
            return False
    
    # Install dependencies for each component
    components = ["process", "grpc", "rest", "mcp"]
    project_root = Path(__file__).parent
    
    for component in components:
        component_dir = project_root / component
        if component_dir.exists():
            print(f"Installing dependencies for {component}...")
            if not run_command(["poetry", "install"], cwd=component_dir):
                print_error(f"Failed to install dependencies for {component}")
                return False
            print_success(f"Installed dependencies for {component}")
    
    return True


def setup_git_hooks() -> bool:
    """Set up Git hooks.
    
    Returns:
        True if setup succeeded, False otherwise
    """
    print_step("Setting up Git hooks")
    
    try:
        # Install pre-commit
        if not run_command(["pip", "install", "pre-commit"]):
            return False
        
        # Install the Git hooks
        project_root = Path(__file__).parent
        if not run_command(["pre-commit", "install"], cwd=project_root):
            return False
        
        print_success("Git hooks installed")
        return True
    except Exception as e:
        print_error(f"Failed to set up Git hooks: {e}")
        return False


def create_env_files() -> bool:
    """Create environment files from examples.
    
    Returns:
        True if creation succeeded, False otherwise
    """
    print_step("Creating environment files")
    
    components = ["process", "grpc", "rest", "mcp"]
    project_root = Path(__file__).parent
    
    for component in components:
        component_dir = project_root / component
        env_example = component_dir / ".env.example"
        env_file = component_dir / ".env"
        
        if env_example.exists() and not env_file.exists():
            try:
                shutil.copy(env_example, env_file)
                print_success(f"Created .env file for {component}")
            except Exception as e:
                print_error(f"Failed to create .env file for {component}: {e}")
                return False
    
    return True


def configure_vscode() -> bool:
    """Configure VSCode settings.
    
    Returns:
        True if configuration succeeded, False otherwise
    """
    print_step("Configuring VSCode settings")
    
    project_root = Path(__file__).parent
    vscode_dir = project_root / ".vscode"
    
    try:
        # Create .vscode directory if it doesn't exist
        vscode_dir.mkdir(exist_ok=True)
        
        # Create settings.json
        settings = {
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
            "python.linting.mypyEnabled": True,
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "python.testing.pytestEnabled": True,
            "python.testing.unittestEnabled": False,
            "python.testing.nosetestsEnabled": False,
            "python.testing.pytestArgs": [
                "tests"
            ]
        }
        
        settings_file = vscode_dir / "settings.json"
        with open(settings_file, "w") as f:
            import json
            json.dump(settings, f, indent=4)
        
        # Create launch.json
        launch = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Process: Run Process",
                    "type": "python",
                    "request": "launch",
                    "module": "process",
                    "cwd": "${workspaceFolder}/process"
                },
                {
                    "name": "gRPC: Run Server",
                    "type": "python",
                    "request": "launch",
                    "module": "grpc.server",
                    "cwd": "${workspaceFolder}"
                },
                {
                    "name": "REST: Run Server",
                    "type": "python",
                    "request": "launch",
                    "module": "rest.server",
                    "cwd": "${workspaceFolder}"
                },
                {
                    "name": "MCP: Run Server",
                    "type": "python",
                    "request": "launch",
                    "module": "mcp.mcp_server",
                    "cwd": "${workspaceFolder}"
                }
            ]
        }
        
        launch_file = vscode_dir / "launch.json"
        with open(launch_file, "w") as f:
            import json
            json.dump(launch, f, indent=4)
        
        print_success("VSCode settings configured")
        return True
    except Exception as e:
        print_error(f"Failed to configure VSCode settings: {e}")
        return False


def setup_development_environment(args: argparse.Namespace) -> bool:
    """Set up the development environment.
    
    Args:
        args: Command-line arguments
        
    Returns:
        True if setup succeeded, False otherwise
    """
    print_step("Setting up development environment")
    
    # Check dependencies
    if not args.skip_dependency_check and not check_dependencies():
        if not args.force:
            print_error("Missing dependencies. Install them and try again, or use --force to continue anyway.")
            return False
        print("Continuing despite missing dependencies...")
    
    # Install Python dependencies
    if not args.skip_python_deps and not install_python_dependencies():
        if not args.force:
            print_error("Failed to install Python dependencies. Fix the issues and try again, or use --force to continue.")
            return False
        print("Continuing despite Python dependency installation failure...")
    
    # Set up Git hooks
    if not args.skip_git_hooks and not setup_git_hooks():
        if not args.force:
            print_error("Failed to set up Git hooks. Fix the issues and try again, or use --force to continue.")
            return False
        print("Continuing despite Git hook setup failure...")
    
    # Create environment files
    if not args.skip_env_files and not create_env_files():
        if not args.force:
            print_error("Failed to create environment files. Fix the issues and try again, or use --force to continue.")
            return False
        print("Continuing despite environment file creation failure...")
    
    # Configure VSCode
    if not args.skip_vscode and not configure_vscode():
        if not args.force:
            print_error("Failed to configure VSCode. Fix the issues and try again, or use --force to continue.")
            return False
        print("Continuing despite VSCode configuration failure...")
    
    print_success("Development environment setup complete!")
    
    # Print next steps
    print("\nNext steps:")
    print("1. Review the .env files in each component directory and adjust as needed")
    print("2. Run 'docker-compose up -d' to start the services")
    print("3. Start developing!")
    
    return True


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(description="Set up development environment for Process project")
    parser.add_argument("--force", action="store_true", help="Continue even if some steps fail")
    parser.add_argument("--skip-dependency-check", action="store_true", help="Skip dependency check")
    parser.add_argument("--skip-python-deps", action="store_true", help="Skip Python dependency installation")
    parser.add_argument("--skip-git-hooks", action="store_true", help="Skip Git hook setup")
    parser.add_argument("--skip-env-files", action="store_true", help="Skip environment file creation")
    parser.add_argument("--skip-vscode", action="store_true", help="Skip VSCode configuration")
    
    args = parser.parse_args()
    
    if setup_development_environment(args):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
