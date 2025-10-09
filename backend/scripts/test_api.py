"""
🧪 AIRMS+ API Testing Script
Tests all API endpoints and generates a detailed report
"""
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import requests
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
import socket
from contextlib import closing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rich console for pretty output
console = Console()

# API Configuration
HOST = "localhost"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}/v1"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your API key

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def check_server(host: str = HOST, port: int = PORT) -> bool:
    """Check if the server is running on the specified port"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            return result == 0
        except:
            return False

# Test Endpoints
ENDPOINTS = [
    {
        "name": "Authentication",
        "method": "POST",
        "path": "/auth/token",
        "payload": {"username": "test", "password": "test123"},
        "expected_status": 200
    },
    {
        "name": "Risk Analysis",
        "method": "POST",
        "path": "/risk/analyze",
        "payload": {"content": "Test content for risk analysis"},
        "expected_status": 200
    },
    {
        "name": "PII Detection",
        "method": "POST",
        "path": "/pii/check",
        "payload": {"text": "Test text for PII detection"},
        "expected_status": 200
    },
    {
        "name": "Education Topics",
        "method": "GET",
        "path": "/education/topics",
        "expected_status": 200
    },
    {
        "name": "Analytics Summary",
        "method": "GET",
        "path": "/analytics/summary",
        "expected_status": 200
    },
    {
        "name": "Fact Checking",
        "method": "POST",
        "path": "/fact-check/verify",
        "payload": {"claim": "Test claim for verification"},
        "expected_status": 200
    },
    {
        "name": "Chat Completion",
        "method": "POST",
        "path": "/chat/completion",
        "payload": {"message": "Hello AI!"},
        "expected_status": 200
    },
    {
        "name": "API Keys",
        "method": "GET",
        "path": "/api-keys/list",
        "expected_status": 200
    }
]

class APITester:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None

    def verify_server(self) -> bool:
        """Verify server is running before tests"""
        if not check_server():
            console.print("\n[bold red]❌ Server is not running![/bold red]")
            console.print("\nPlease ensure:")
            console.print("1. Your virtual environment is activated")
            console.print(f"2. FastAPI server is running on port {PORT}")
            console.print("3. No firewall is blocking the port")
            console.print("\nRun the server with:")
            console.print("python -m uvicorn app.main:app --reload --port 8000")
            return False
        return True

    def test_endpoint(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{BASE_URL}{endpoint['path']}"
        method = endpoint['method'].upper()
        name = endpoint['name']
        
        result = {
            "name": name,
            "endpoint": endpoint['path'],
            "method": method,
            "success": False,
            "status_code": None,
            "response_time": 0,
            "error": None
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=HEADERS, timeout=10)
            elif method == "POST":
                response = requests.post(
                    url,
                    json=endpoint.get("payload", {}),
                    headers=HEADERS,
                    timeout=10
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            result.update({
                "success": response.status_code == endpoint['expected_status'],
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "response": response.json() if response.ok else None
            })

        except requests.exceptions.RequestException as e:
            result.update({
                "success": False,
                "error": str(e)
            })

        return result

    def run_tests(self) -> None:
        """Run all API tests"""
        if not self.verify_server():
            sys.exit(1)

        self.start_time = datetime.now()
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Testing endpoints...", total=len(ENDPOINTS))
            
            for endpoint in ENDPOINTS:
                result = self.test_endpoint(endpoint)
                self.results.append(result)
                progress.update(task, advance=1)
        
        self.end_time = datetime.now()

    def generate_report(self) -> None:
        """Generate a detailed report of the test results"""
        table = Table(title="API Test Results", show_header=True, header_style="bold magenta")
        
        table.add_column("Name", style="dim")
        table.add_column("Endpoint")
        table.add_column("Method")
        table.add_column("Success", justify="center")
        table.add_column("Status Code", justify="center")
        table.add_column("Response Time (s)", justify="right")
        table.add_column("Error")
        
        for result in self.results:
            table.add_row(
                result["name"],
                result["endpoint"],
                result["method"],
                "✅" if result["success"] else "❌",
                str(result["status_code"]),
                f"{result['response_time']:.4f}",
                result["error"] if result["error"] else ""
            )
        
        console.print(table)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - passed_tests
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"Total tests: {total_tests}")
        console.print(f"Passed: {passed_tests}", style="green" if passed_tests == total_tests else "red")
        console.print(f"Failed: {failed_tests}", style="red" if failed_tests > 0 else "green")
        console.print(f"Duration: {self.end_time - self.start_time}", style="blue")

def main():
    tester = APITester()
    tester.run_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()