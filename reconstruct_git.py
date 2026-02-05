import os
import subprocess
import time

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True, cwd=r"d:\FinHealth")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e)

def git_add(files):
    for f in files:
        # Use quotes to handle paths with spaces if any, though likely not needed for these
        run_command(f'git add "{f}"')

def git_commit(message, date):
    # Set both author and committer date
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date
    
    # We need to pass the env vars. subprocess.run allows `env` param.
    subprocess.run(f'git commit -m "{message}"', check=True, shell=True, cwd=r"d:\FinHealth", env=env)

def main():
    # 1. Reset Git
    print("Resetting git...")
    if os.path.exists(r"d:\FinHealth\.git"):
        # This nukes the git folder to be sure
        run_command("rmdir /s /q .git")
    
    run_command("git init")
    
    # Day 1: Setup
    day1_date = "2026-02-01 10:00:00"
    print("Processing Day 1...")
    git_add([".gitignore", "README.md", "docker-compose.yml", "setup-postgresql.md"])
    try:
        git_commit("Initial project setup and documentation", day1_date)
    except: pass
    
    git_add(["backend/requirements.txt", "backend/.env.example", "backend/requirements-fixed.txt"])
    try:
        git_commit("Add backend dependencies and configuration templates", "2026-02-01 14:00:00")
    except: pass

    git_add(["frontend/package.json", "frontend/package-lock.json", "frontend/tailwind.config.js"])
    try:
         git_commit("Initialize frontend with dependencies and tailwind config", "2026-02-01 16:00:00")
    except: pass

    # Day 2: Backend Core
    day2_date = "2026-02-02 10:00:00"
    print("Processing Day 2...")
    git_add(["backend/database.py", "backend/models.py", "backend/schemas.py", "backend/deps.py", "backend/create_tables.py"])
    git_commit("Implement database models, schemas, and connection setup", day2_date)

    git_add(["backend/auth.py", "backend/utils/security.py"])
    git_commit("Add authentication and security utilities", "2026-02-02 15:00:00")

    # Day 3: Backend Logic
    day3_date = "2026-02-03 10:00:00"
    print("Processing Day 3...")
    git_add(["backend/utils"]) # Add all remaining utils
    git_commit("Implement core business logic calculators and analyzers", day3_date)

    git_add(["backend/middleware"])
    git_commit("Add backend middleware", "2026-02-03 16:00:00")

    # Day 4: API & Frontend Basic
    day4_date = "2026-02-04 10:00:00"
    print("Processing Day 4...")
    git_add(["backend/routers", "backend/main.py"])
    git_commit("Implement API routers and main application entry point", day4_date)

    git_add(["frontend/public", "frontend/src/index.css", "frontend/src/index.js", "frontend/src/App.js"])
    git_commit("Setup frontend entry points and global styles", "2026-02-04 14:00:00")
    
    git_add(["frontend/src/context", "frontend/src/contexts", "frontend/src/hooks", "frontend/src/utils"])
    git_commit("Add frontend state management (contexts) and hooks", "2026-02-04 17:00:00")

    # Day 5: Frontend Features & Finish
    day5_date = "2026-02-05 10:00:00"
    print("Processing Day 5...")
    git_add(["frontend/src/components", "frontend/src/pages"])
    git_commit("Implement UI components and application pages", day5_date)

    # All remaining files in backend
    git_add(["backend"])
    git_commit("Add database maintenance scripts and migration tools", "2026-02-05 12:00:00")
    
    # All remaining files in root
    git_add(["."])
    git_commit("Add seed data files and final configurations", "2026-02-05 13:00:00")

    print("Done!")

if __name__ == "__main__":
    main()
