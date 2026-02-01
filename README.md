# AI-Powered Financial Health Intelligence Platform for SMEs

A production-ready, secure, AI-powered financial health assessment web application for Small and Medium Enterprises (SMEs).

## Features

- **Financial Health Assessment**: Comprehensive analysis of financial statements and cash flow patterns
- **Creditworthiness Evaluation**: Deterministic scoring system with AI-generated insights
- **Risk Detection**: Identify financial risks and provide actionable recommendations
- **Cost Optimization**: AI-powered strategies for expense reduction
- **Financial Product Recommendations**: Match with suitable loans from banks and NBFCs
- **Financial Forecasting**: Linear regression-based projections
- **Industry Benchmarking**: Compare against industry standards
- **Investor-Ready Reports**: Generate professional financial reports
- **Multilingual Support**: English and Hindi languages

## Architecture

### Frontend
- **Framework**: React.js with TypeScript
- **UI Library**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts for data visualization
- **State Management**: React Context + useReducer

### Backend
- **Framework**: Python FastAPI
- **Data Processing**: pandas for financial calculations
- **Database**: PostgreSQL with encryption
- **AI Integration**: OpenAI GPT-5 for narrative insights

### Security
- TLS encryption in transit
- AES encryption for financial data at rest
- JWT authentication
- Role-based access control
- Audit logging

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL 14+
- Redis (for caching)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd financial-health-platform
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Database Setup**
```bash
createdb financial_health_platform
psql -d financial_health_platform -f schema.sql
```

4. **Frontend Setup**
```bash
cd frontend
npm install
```

5. **Environment Configuration**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost/financial_health_platform
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Frontend (.env)
REACT_APP_API_URL=http://localhost:8000
```

6. **Run the Application**
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
npm start
```

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration

### Company Management
- `POST /company/create` - Create company profile
- `GET /company/{id}` - Get company details

### Data Management
- `POST /data/upload` - Upload financial data (CSV/XLSX/PDF)
- `GET /data/list` - List uploaded files

### Financial Analysis
- `POST /metrics/calculate` - Calculate financial metrics
- `GET /risk/evaluate` - Get risk assessment
- `GET /credit/score` - Get creditworthiness score
- `POST /forecast/generate` - Generate financial forecast
- `GET /loan/match` - Get loan recommendations
- `GET /benchmark/compare` - Industry benchmarking
- `GET /report/export` - Export financial report

## Supported Industries

- Manufacturing
- Retail
- Agriculture
- Services
- Logistics
- E-commerce

## Data Sources

- **File Upload**: CSV, XLSX, PDF (text-based)
- **API Integrations**: Banking APIs (max 2)
- **GST Data**: Optional GST filing import

## Financial Metrics Calculated

- Profitability Ratios (Gross/Net Profit Margin)
- Liquidity Ratios (Current/Quick Ratio)
- Leverage Ratios (Debt-to-Equity)
- Efficiency Ratios (Working Capital, Cash Conversion Cycle)
- Coverage Ratios (Interest Coverage)

## Security Features

- End-to-end encryption
- Row-level data isolation
- Secure file upload sandboxing
- Rate limiting
- Audit trails
- GDPR compliance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and inquiries, contact [support@financialhealth.com](mailto:support@financialhealth.com)
