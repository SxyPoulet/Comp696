#!/usr/bin/env python3
"""
Setup Verification Script for Sales Intelligence Agent
This script checks if all required components are properly configured.
"""

import sys
import subprocess
import os
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def check_command(command, name):
    """Check if a command is available."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            timeout=5
        )
        if result.returncode == 0:
            output = result.stdout.decode().strip().split('\n')[0]
            print(f"{Colors.GREEN}✓{Colors.END} {name}: {output}")
            return True
        else:
            print(f"{Colors.RED}✗{Colors.END} {name}: Not found or error")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {name}: {str(e)}")
        return False


def check_file_exists(filepath, name):
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"{Colors.GREEN}✓{Colors.END} {name}: Found at {filepath}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {name}: Not found at {filepath}")
        return False


def check_env_variable(var_name, required=True):
    """Check if environment variable is set."""
    # Try to load from .env file
    env_path = Path(__file__).parent / "backend" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == var_name:
                            if value and value != f"your-{var_name.lower().replace('_', '-')}-here":
                                print(f"{Colors.GREEN}✓{Colors.END} {var_name}: Configured")
                                return True
                            else:
                                status = "REQUIRED" if required else "Optional"
                                print(f"{Colors.YELLOW}⚠{Colors.END} {var_name}: Not configured ({status})")
                                return not required

    status = "REQUIRED" if required else "Optional"
    print(f"{Colors.YELLOW}⚠{Colors.END} {var_name}: Not found ({status})")
    return not required


def check_docker_services():
    """Check if Docker services are running."""
    try:
        result = subprocess.run(
            "docker-compose ps",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=Path(__file__).parent,
            timeout=10
        )
        output = result.stdout.decode()

        services = ["postgres", "redis", "backend", "celery_worker", "flower"]
        running_services = []

        for service in services:
            if service in output and "Up" in output:
                running_services.append(service)
                print(f"{Colors.GREEN}✓{Colors.END} Docker service '{service}' is running")
            else:
                print(f"{Colors.RED}✗{Colors.END} Docker service '{service}' is not running")

        return len(running_services) == len(services)
    except Exception as e:
        print(f"{Colors.YELLOW}⚠{Colors.END} Could not check Docker services: {str(e)}")
        return False


def check_api_endpoint(url, name):
    """Check if API endpoint is accessible."""
    try:
        import urllib.request
        import json

        response = urllib.request.urlopen(url, timeout=5)
        data = json.loads(response.read().decode())
        print(f"{Colors.GREEN}✓{Colors.END} {name}: Accessible")
        print(f"  Response: {data}")
        return True
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {name}: Not accessible ({str(e)})")
        return False


def main():
    """Run all verification checks."""
    print_header("Sales Intelligence Agent - Setup Verification")

    results = {
        "prerequisites": [],
        "files": [],
        "configuration": [],
        "services": [],
        "api": []
    }

    # Check Prerequisites
    print(f"\n{Colors.BOLD}1. Prerequisites{Colors.END}")
    results["prerequisites"].append(check_command("docker --version", "Docker"))
    results["prerequisites"].append(check_command("docker-compose --version", "Docker Compose"))
    results["prerequisites"].append(check_command("python --version", "Python") or
                                   check_command("python3 --version", "Python3"))

    # Check Project Files
    print(f"\n{Colors.BOLD}2. Project Files{Colors.END}")
    base_path = Path(__file__).parent
    results["files"].append(check_file_exists(base_path / "docker-compose.yml", "docker-compose.yml"))
    results["files"].append(check_file_exists(base_path / "backend" / "app" / "main.py", "Backend main.py"))
    results["files"].append(check_file_exists(base_path / "backend" / ".env", ".env file"))
    results["files"].append(check_file_exists(base_path / "backend" / "pyproject.toml", "pyproject.toml"))

    # Check Configuration
    print(f"\n{Colors.BOLD}3. Configuration (API Keys){Colors.END}")
    results["configuration"].append(check_env_variable("ANTHROPIC_API_KEY", required=True))
    results["configuration"].append(check_env_variable("CLEARBIT_API_KEY", required=False))
    results["configuration"].append(check_env_variable("HUNTER_API_KEY", required=False))

    # Check Docker Services (if Docker is available)
    if results["prerequisites"][0] and results["prerequisites"][1]:
        print(f"\n{Colors.BOLD}4. Docker Services{Colors.END}")
        services_ok = check_docker_services()
        results["services"].append(services_ok)

        # Check API Endpoints (if services are running)
        if services_ok or any(results["services"]):
            print(f"\n{Colors.BOLD}5. API Endpoints{Colors.END}")
            results["api"].append(check_api_endpoint("http://localhost:8000/health", "Health Check"))
            results["api"].append(check_api_endpoint("http://localhost:8000/", "Root Endpoint"))
    else:
        print(f"\n{Colors.YELLOW}⚠{Colors.END} Docker not available - skipping service checks")
        print(f"  To start services, install Docker and run: docker-compose up")

    # Print Summary
    print_header("Summary")

    total_checks = sum([
        len([x for x in results["prerequisites"] if x is not None]),
        len([x for x in results["files"] if x is not None]),
        len([x for x in results["configuration"] if x is not None]),
        len([x for x in results["services"] if x is not None]),
        len([x for x in results["api"] if x is not None]),
    ])

    passed_checks = sum([
        sum([1 for x in results["prerequisites"] if x]),
        sum([1 for x in results["files"] if x]),
        sum([1 for x in results["configuration"] if x]),
        sum([1 for x in results["services"] if x]),
        sum([1 for x in results["api"] if x]),
    ])

    print(f"Passed: {passed_checks}/{total_checks} checks")

    # Recommendations
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")

    if not all(results["prerequisites"]):
        print(f"{Colors.YELLOW}→{Colors.END} Install missing prerequisites (Docker, Python)")

    if not all(results["files"]):
        print(f"{Colors.YELLOW}→{Colors.END} Some project files are missing - check setup")

    if not results["configuration"][0]:  # ANTHROPIC_API_KEY
        print(f"{Colors.YELLOW}→{Colors.END} Configure ANTHROPIC_API_KEY in backend/.env")

    if not any(results["services"]):
        print(f"{Colors.YELLOW}→{Colors.END} Start services with: docker-compose up -d")

    if not any(results["api"]):
        print(f"{Colors.YELLOW}→{Colors.END} API not accessible - check if services are running")

    if passed_checks == total_checks:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed! System is ready.{Colors.END}")
        print(f"\nAccess your application at:")
        print(f"  • API: http://localhost:8000")
        print(f"  • API Docs: http://localhost:8000/docs")
        print(f"  • Flower: http://localhost:5555")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠ Some checks failed. Review the output above.{Colors.END}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.END}")
        sys.exit(1)
