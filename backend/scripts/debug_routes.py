"""
Debug script to check available routes
"""
import requests
from rich.console import Console
from rich.json import JSON

console = Console()

def check_routes():
    """Check what routes are available"""
    try:
        # First check if server is running
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            console.print("✅ Server is running")
            console.print("Root response:", response.json())
        
        # Check health endpoint
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            console.print("✅ Health endpoint working")
        
        # Check if we have a debug routes endpoint
        try:
            routes_response = requests.get("http://localhost:8000/debug/routes")
            if routes_response.status_code == 200:
                console.print("📋 Available Routes:")
                console.print(JSON(routes_response.json()))
            else:
                console.print("❌ No debug routes endpoint")
        except:
            console.print("❌ No debug routes endpoint")
            
        # Try to access the chat endpoint directly
        try:
            chat_response = requests.get("http://localhost:8000/v1/chat/completion")
            console.print(f"Chat endpoint status: {chat_response.status_code}")
        except Exception as e:
            console.print(f"❌ Chat endpoint error: {e}")
            
    except Exception as e:
        console.print(f"❌ Server connection error: {e}")

if __name__ == "__main__":
    check_routes()