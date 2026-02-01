# PostgreSQL Setup Instructions for Windows

## Option 1: Install PostgreSQL Locally

### Step 1: Download and Install PostgreSQL
1. Go to https://www.postgresql.org/download/windows/
2. Download the latest stable version (PostgreSQL 15 or 16)
3. Run the installer with these settings:
   - Password for postgres user: **password** (or choose your own)
   - Port: 5432 (default)
   - Install pgAdmin 4 (included)

### Step 2: Add PostgreSQL to PATH
1. Find PostgreSQL installation directory (usually: `C:\Program Files\PostgreSQL\16\bin`)
2. Add this path to your Windows Environment Variables PATH

### Step 3: Create Database
Open Command Prompt as Administrator and run:
```cmd
cd "C:\Program Files\PostgreSQL\16\bin"
psql -U postgres -c "CREATE DATABASE financial_health_platform;"
```

### Step 4: Test Connection
```cmd
psql -U postgres -d financial_health_platform
```

## Option 2: Use Docker (Easier)

### Step 1: Install Docker Desktop
1. Download from https://www.docker.com/products/docker-desktop/
2. Install and start Docker Desktop

### Step 2: Run PostgreSQL Container
In your project directory:
```cmd
docker-compose up -d postgres
```

### Step 3: Verify Database
```cmd
docker-compose exec postgres psql -U postgres -d financial_health_platform -c "\dt"
```

## Environment Configuration

After setting up PostgreSQL, update your backend/.env file:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/financial_health_platform
```

## Troubleshooting

### If psql command not found:
- Make sure PostgreSQL bin directory is in your PATH
- Or use full path: `"C:\Program Files\PostgreSQL\16\bin\psql.exe"`

### If connection fails:
- Check if PostgreSQL service is running
- Verify password and port settings
- Check firewall settings
