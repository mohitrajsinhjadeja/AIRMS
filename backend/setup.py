import os
import sys
import subprocess
from pathlib import Path
import secrets
from setuptools import setup, find_packages

setup(
    name="airms-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.103.0",
        "uvicorn[standard]>=0.23.0",
        "motor>=3.3.1",
        "pydantic>=2.3.0",
        "python-multipart>=0.0.6",
    ]
)

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print("✅ Python version OK")
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("✅ Docker is available")
        docker_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Docker not found (optional for local development)")
        docker_available = False
    
    return docker_available

def create_env_file():
    """Create .env file from template"""
    print("\n📝 Creating environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    if env_file.exists():
        response = input("⚠️ .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("✅ Using existing .env file")
            return True
    
    # Read template
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Generate JWT secret
    jwt_secret = secrets.token_urlsafe(32)
    content = content.replace(
        "your-super-secret-jwt-key-change-in-production-use-openssl-rand-hex-32",
        jwt_secret
    )
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ .env file created with secure JWT secret")
    return True

def setup_local_development():
    """Set up local development environment"""
    print("\n🔧 Setting up local development...")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        pip_path = venv_path / "Scripts" / "pip"
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/Mac
        pip_path = venv_path / "bin" / "pip"
        activate_cmd = "source venv/bin/activate"
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed")
    
    print(f"\n🎉 Local development setup complete!")
    print(f"To activate the virtual environment, run:")
    print(f"   {activate_cmd}")
    print(f"\nTo start the development server, run:")
    print(f"   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

def setup_docker():
    """Set up Docker environment"""
    print("\n🐳 Setting up Docker environment...")
    
    # Check if docker-compose.yml exists
    if not Path("docker-compose.yml").exists():
        print("❌ docker-compose.yml not found")
        return False
    
    print("🔧 Starting Docker services...")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Docker services started successfully")
        
        print("\n🌐 Services available at:")
        print("   • Backend API: http://localhost:8000")
        print("   • API Docs: http://localhost:8000/api/v1/docs")
        print("   • MongoDB: localhost:27017")
        print("   • Mongo Express: http://localhost:8081 (admin/airms_admin)")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Docker services: {e}")
        return False

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is responding")
            return True
        else:
            print(f"⚠️ Backend returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException:
        print("⚠️ Backend not responding (may need to start manually)")
        return False
    except ImportError:
        print("ℹ️ Requests not available for testing")
        return True

def print_banner():
    """Print setup banner"""
    print("=" * 50)
    print("       AIRMS MongoDB Backend Setup")
    print("=" * 50)

def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    docker_available = check_requirements()
    
    # Create .env file
    if not create_env_file():
        print("❌ Failed to create .env file")
        return False
    
    # Ask user for setup type
    print("\n🛠️ Setup Options:")
    print("1. Docker (Recommended - includes MongoDB)")
    print("2. Local Development (requires MongoDB separately)")
    
    if docker_available:
        choice = input("\nChoose setup type (1/2): ").strip()
    else:
        print("\nDocker not available, using local development setup...")
        choice = "2"
    
    if choice == "1" and docker_available:
        success = setup_docker()
        if success:
            test_setup()
    elif choice == "2":
        setup_local_development()
        print("\n⚠️ Note: You need to install and start MongoDB separately")
        print("   Local: brew install mongodb (Mac) or apt-get install mongodb (Ubuntu)")
        print("   Cloud: Use MongoDB Atlas (https://cloud.mongodb.com)")
    else:
        print("❌ Invalid choice")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 AIRMS MongoDB Backend Setup Complete!")
    print("\nNext steps:")
    print("1. Visit http://localhost:8000/api/v1/docs for API documentation")
    print("2. Test registration: POST /api/v1/auth/register")
    print("3. Test login: POST /api/v1/auth/login")
    print("4. Use JWT tokens for authenticated endpoints")
    print("\nDefault admin user:")
    print("   Email: admin@airms.com")
    print("   Password: admin123")
    print("\n🚀 Happy coding!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
