import asyncio
import httpx
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from rich.console import Console
from rich.table import Table
from tenacity import retry, stop_after_attempt, wait_exponential
from dataclasses import dataclass
from pathlib import Path

# Configure rich console for better output
console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    module: str
    endpoint: str
    method: str
    data: Dict[str, Any] | None
    expected_status: int = 200
    description: str = ""

class ModuleVerification:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        self.results = []
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def verify_endpoint(
        self,
        client: httpx.AsyncClient,
        test_case: TestCase
    ) -> Tuple[bool, str]:
        try:
            headers = {}
            if self.auth_token and test_case.module != "auth":
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            response = await client.request(
                test_case.method,
                f"{self.base_url}{test_case.endpoint}",
                json=test_case.data,
                headers=headers
            )
            
            if response.status_code != test_case.expected_status:
                return False, f"Expected status {test_case.expected_status}, got {response.status_code}"
                
            # Store auth token if this is a login response
            if test_case.endpoint == "/v1/auth/token" and response.status_code == 200:
                self.auth_token = response.json().get("access_token")
            
            return True, "Success"
            
        except Exception as e:
            return False, str(e)

    def get_test_cases(self) -> List[TestCase]:
        return [
            # Auth Module
            TestCase(
                module="auth",
                endpoint="/v1/auth/token",
                method="POST",
                data={"username": "admin@airms.dev", "password": "admin123"},
                description="Login with admin credentials"
            ),
            
            # Risk Detection Module
            TestCase(
                module="risk",
                endpoint="/v1/risk/analyze",
                method="POST",
                data={
                    "input": "Test email: user@example.com, Phone: 123-456-7890",
                    "config": {"detectors": ["pii", "bias", "hallucination"]}
                },
                description="Test risk analysis with PII data"
            ),
            
            # PII Safety Module
            TestCase(
                module="pii",
                endpoint="/v1/pii/check",
                method="POST",
                data={"text": "SSN: 123-45-6789, Credit Card: 4111-1111-1111-1111"},
                description="Test PII detection"
            ),
            
            # Education Module
            TestCase(
                module="education",
                endpoint="/v1/education/topics",
                method="GET",
                data=None,
                description="Get educational topics"
            ),
            
            # Analytics Module
            TestCase(
                module="analytics",
                endpoint="/v1/analytics/summary",
                method="GET",
                data=None,
                description="Get analytics summary"
            ),
            
            # Fact Checking Module
            TestCase(
                module="fact_checking",
                endpoint="/v1/fact-check/verify",
                method="POST",
                data={"text": "The Earth is flat"},
                description="Verify fact checking"
            ),
            
            # Chat Module
            TestCase(
                module="chat",
                endpoint="/v1/chat/completion",
                method="POST",
                data={"messages": [{"role": "user", "content": "Hello"}]},
                description="Test chat completion"
            ),
            
            # API Keys Module
            TestCase(
                module="api_keys",
                endpoint="/v1/api-keys/list",
                method="GET",
                data=None,
                description="List API keys"
            )
        ]

    async def run_verification(self):
        console.print("\n[bold blue]🚀 Starting AIRMS+ Backend Module Verification[/bold blue]\n")
        
        start_time = datetime.now()
        test_cases = self.get_test_cases()
        
        async with httpx.AsyncClient() as client:
            for test_case in test_cases:
                success, message = await self.verify_endpoint(client, test_case)
                self.results.append({
                    "module": test_case.module,
                    "endpoint": test_case.endpoint,
                    "success": success,
                    "message": message,
                    "description": test_case.description
                })
        
        self.print_report(datetime.now() - start_time)

    def print_report(self, duration):
        # Create results table
        table = Table(title="AIRMS+ Module Verification Report")
        table.add_column("Module", style="cyan")
        table.add_column("Endpoint", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        # Group results by module
        module_results = {}
        for result in self.results:
            module = result["module"]
            if module not in module_results:
                module_results[module] = []
            module_results[module].append(result)
        
        # Add results to table
        for module, results in module_results.items():
            for result in results:
                status = "✅" if result["success"] else "❌"
                table.add_row(
                    module,
                    result["endpoint"],
                    status,
                    result["message"]
                )
        
        # Print summary
        console.print("\n")
        console.print(table)
        console.print("\n[bold]Summary:[/bold]")
        
        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        
        console.print(f"Total Tests: {total_tests}")
        console.print(f"Successful: [green]{successful}[/green]")
        console.print(f"Failed: [red]{total_tests - successful}[/red]")
        console.print(f"Duration: {duration.total_seconds():.2f} seconds")
        
        if successful == total_tests:
            console.print("\n[bold green]✅ All systems operational![/bold green]")
        else:
            console.print("\n[bold red]⚠️ Some systems need attention[/bold red]")

async def main():
    verifier = ModuleVerification()
    await verifier.run_verification()

if __name__ == "__main__":
    asyncio.run(main())