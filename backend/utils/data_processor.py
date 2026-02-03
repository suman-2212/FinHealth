import io
import re
from PyPDF2 import PdfReader
from typing import Dict, Tuple, List, Optional
import pandas as pd

class DataProcessor:
    def __init__(self):
        self.field_mappings = {
            # Revenue fields
            'revenue': ['revenue', 'sales', 'turnover', 'income', 'total revenue', 'Revenue'],
            'sales_returns': ['sales returns', 'returns', 'sales allowances'],
            'net_sales': ['net sales', 'net revenue', 'net turnover'],
            # Cost fields
            'cost_of_goods_sold': ['cogs', 'cost of goods sold', 'cost of sales', 'COGS'],
            'gross_profit': ['gross profit', 'gross margin'],
            # Expense fields
            'salaries_wages': ['salaries', 'wages', 'salary expenses', 'payroll'],
            'rent_expense': ['rent', 'rental expense', 'lease expense'],
            'utilities': ['utilities', 'electricity', 'water', 'gas'],
            'marketing_expense': ['marketing', 'advertising', 'promotion'],
            'administrative_expense': ['admin', 'administrative', 'office expenses', 'Operating_Expenses'],
            'depreciation': ['depreciation', 'amortization'],
            'other_operating_expense': ['other expenses', 'miscellaneous expenses'],
            # Profit fields
            'operating_income': ['operating income', 'ebit', 'operating profit'],
            'interest_expense': ['interest', 'interest expense', 'finance cost', 'Interest_Expense'],
            'tax_expense': ['tax', 'income tax', 'tax expense', 'Tax'],
            'net_income': ['net income', 'net profit', 'profit after tax'],
            # Balance sheet assets
            'cash': ['cash', 'cash and equivalents', 'bank balance'],
            'accounts_receivable': ['accounts receivable', 'ar', 'debtors', 'Accounts_Receivable'],
            'inventory': ['inventory', 'stock', 'goods in transit', 'Inventory'],
            'current_assets': ['current assets', 'current total assets', 'Current_Assets'],
            'fixed_assets': ['fixed assets', 'property plant equipment', 'ppe'],
            'total_assets': ['total assets', 'assets total', 'Total_Assets'],
            # Balance sheet liabilities
            'accounts_payable': ['accounts payable', 'ap', 'creditors', 'Accounts_Payable'],
            'short_term_debt': ['short term debt', 'current debt', 'short term loans'],
            'current_liabilities': ['current liabilities', 'current total liabilities', 'Current_Liabilities'],
            'long_term_debt': ['long term debt', 'long term loans'],
            'total_liabilities': ['total liabilities', 'liabilities total', 'Total_Liabilities'],
            'equity': ['equity', 'shareholders equity', 'owners equity'],
            # Cash flow
            'operating_cash_flow': ['operating cash flow', 'ocf'],
            'investing_cash_flow': ['investing cash flow', 'icf'],
            'financing_cash_flow': ['financing cash flow', 'fcf'],
            'net_cash_flow': ['net cash flow', 'cash flow change', 'Cash_Flow']
        }

    def process_file(self, content: bytes, filename: str, content_type: str) -> Tuple[Dict, List[str]]:
        """Process uploaded file and extract financial data with schema validation"""
        errors = []
        try:
            if content_type == "text/csv":
                data, file_errors = self._process_csv(content)
            elif content_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                data, file_errors = self._process_excel(content)
            elif content_type == "application/pdf":
                data, file_errors = self._process_pdf(content)
            else:
                return {}, ["Unsupported file type"]
            errors.extend(file_errors)

            # Normalize and validate schema
            cleaned_data = self._normalize_and_validate(data)
            validation_errors = self._validate_required_columns(cleaned_data)
            errors.extend(validation_errors)

            return cleaned_data, errors
        except Exception as e:
            return {}, [f"Error processing file: {str(e)}"]

    def _process_csv(self, content: bytes) -> Tuple[Dict, List[str]]:
        try:
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            return self._extract_data_from_dataframe(df), []
        except Exception as e:
            return {}, [f"Error reading CSV: {str(e)}"]

    def _process_excel(self, content: bytes) -> Tuple[Dict, List[str]]:
        try:
            df = pd.read_excel(io.BytesIO(content))
            return self._extract_data_from_dataframe(df), []
        except Exception as e:
            return {}, [f"Error reading Excel: {str(e)}"]

    def _process_pdf(self, content: bytes) -> Tuple[Dict, List[str]]:
        try:
            pdf_reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return self._extract_data_from_text(text), []
        except Exception as e:
            return {}, [f"Error reading PDF (ensure text-based, not scanned): {str(e)}"]

    def _normalize_and_validate(self, data: Dict) -> Dict:
        """Normalize currency formats and clean numeric values"""
        cleaned = {}
        for key, value in data.items():
            if value is None:
                cleaned[key] = None
                continue
            if isinstance(value, str):
                # Remove currency symbols, commas, and whitespace
                value = re.sub(r'[$,₹€£¥\s]', '', value)
                # Convert to float if possible
                try:
                    cleaned[key] = float(value)
                except ValueError:
                    cleaned[key] = None
            else:
                cleaned[key] = value
        return cleaned

    def _validate_required_columns(self, data: Dict) -> List[str]:
        """Require at least one of revenue, expenses, assets, liabilities, receivables, payables, loans, inventory, tax"""
        required_groups = [
            ['revenue', 'net_sales'],
            ['expenses', 'cost_of_goods_sold'],
            ['assets', 'total_assets', 'current_assets'],
            ['liabilities', 'total_liabilities', 'current_liabilities'],
            ['receivables', 'accounts_receivable'],
            ['payables', 'accounts_payable'],
            ['loans', 'short_term_debt', 'long_term_debt'],
            ['inventory'],
            ['tax', 'tax_expense']
        ]
        missing = []
        for group in required_groups:
            if not any(data.get(k) not in (None, '', 0) for k in group):
                missing.append(f"At least one of {group} is required")
        return missing
    
    def _extract_data_from_dataframe(self, df) -> Dict:
        """Extract financial data from pandas DataFrame, handling category/amount style"""
        data = {}

        try:
            import pandas as pd  # type: ignore

            def _is_na(v):
                return pd.isna(v)

        except Exception:

            def _is_na(v):
                return v is None or (isinstance(v, str) and v.strip() == "")

        # If CSV has 'month'/'Month', 'revenue'/'Revenue', and other financial columns, treat as pre-aggregated monthly data
        required_monthly_cols_lower = {'month', 'revenue'}
        required_monthly_cols_upper = {'Month', 'Revenue'}
        df_columns_lower = set(col.lower() for col in df.columns)
        df_columns_upper = set(df.columns)
        
        if required_monthly_cols_lower.issubset(df_columns_lower) or required_monthly_cols_upper.issubset(df_columns_upper):
            # Pre-aggregated monthly format: map columns directly
            statements = {}
            for _, row in df.iterrows():
                # Handle both 'month' and 'Month' column names
                month = str(row.get('month', row.get('Month', '')))
                
                # Compute debt metrics deterministically
                short_term_debt = row.get('short_term_debt', 0)
                long_term_debt = row.get('long_term_debt', 0)
                total_liabilities = row.get('total_liabilities', row.get('Total_Liabilities', 0))
                total_assets = row.get('total_assets', row.get('Total_Assets', 0))
                
                # Compute total_debt: prefer explicit debt columns, fallback to total_liabilities
                if short_term_debt > 0 or long_term_debt > 0:
                    total_debt = short_term_debt + long_term_debt
                else:
                    total_debt = total_liabilities
                
                # Compute equity
                equity = total_assets - total_liabilities
                
                # Compute debt_to_equity safely
                if equity <= 0:
                    debt_to_equity = 999.99  # Very high value for Critical risk
                    risk_level = 'Critical'
                else:
                    debt_to_equity = total_debt / equity
                    # Map ratio to risk levels
                    if debt_to_equity <= 0.5:
                        risk_level = 'Low'
                    elif debt_to_equity <= 1.5:
                        risk_level = 'Moderate'
                    elif debt_to_equity <= 3:
                        risk_level = 'High'
                    else:
                        risk_level = 'Critical'
                
                # Map CSV columns to standard field names using field_mappings
                month_data = {}
                for field_name, possible_columns in self.field_mappings.items():
                    for col in possible_columns:
                        if col in df.columns:
                            month_data[field_name] = row.get(col, 0)
                            break
                
                # Ensure required fields have default values
                month_data.update({
                    'total_assets': total_assets,
                    'current_liabilities': total_liabilities,
                    'short_term_debt': short_term_debt,
                    'long_term_debt': long_term_debt,
                    'total_debt': total_debt,
                    'equity': equity,
                    'debt_to_equity': debt_to_equity,
                    'risk_level': risk_level
                })
                print(f"[DATA PROCESSOR] month={month} total_assets={total_assets} total_liabilities={total_liabilities} equity={equity} total_debt={total_debt} debt_to_equity={debt_to_equity:.2f} risk_level={risk_level}")
                # Auto-generate derived fields
                revenue = month_data.get('revenue', 0)
                total_expenses = month_data.get('other_operating_expense', 0) + month_data.get('interest_expense', 0) + month_data.get('tax_expense', 0)
                month_data['net_income'] = revenue - total_expenses
                month_data['gross_profit'] = revenue - month_data.get('cost_of_goods_sold', 0)
                month_data['operating_income'] = revenue - month_data.get('other_operating_expense', 0)
                # Balance Sheet
                total_assets = month_data.get('total_assets')
                current_liabilities = month_data.get('current_liabilities')
                if total_assets and current_liabilities:
                    month_data['equity'] = total_assets - current_liabilities
                # Current assets
                cash = month_data.get('cash', 0)
                ar = month_data.get('accounts_receivable', 0)
                inv = month_data.get('inventory', 0)
                if cash or ar or inv:
                    month_data['current_assets'] = cash + ar + inv
                else:
                    month_data['current_assets'] = total_assets * 0.6 if total_assets else 0
                # Cash Flow
                month_data['operating_cash_flow'] = month_data.get('net_income', 0)
                statements[month] = month_data
            # Return the latest month as primary data and include monthly summaries
            latest_month = max(statements.keys()) if statements else None
            if latest_month:
                data = statements[latest_month]
                data['monthly_statements'] = statements
            return data
        if 'date' in df.columns and 'category' in df.columns and 'amount' in df.columns:
            # Parse dates and normalize category names
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['category'] = df['category'].str.lower().str.strip()
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            # Add month column
            df['month'] = df['date'].dt.to_period('M').astype(str)
            # Aggregate by month and category
            agg = df.groupby(['month', 'category'])['amount'].sum().reset_index()
            # Build monthly statements
            statements = {}
            for month, group in agg.groupby('month'):
                month_data = {}
                for _, row in group.iterrows():
                    cat, val = row['category'], row['amount']
                    if 'revenue' in cat or 'sales' in cat or 'income' in cat:
                        month_data['revenue'] = month_data.get('revenue', 0) + val
                    elif 'expense' in cat or 'cost' in cat or 'operating' in cat:
                        month_data['other_operating_expense'] = month_data.get('other_operating_expense', 0) + val
                    elif 'loan' in cat or 'debt' in cat:
                        month_data['interest_expense'] = month_data.get('interest_expense', 0) + val
                    elif 'tax' in cat:
                        month_data['tax_expense'] = month_data.get('tax_expense', 0) + val
                    elif 'asset' in cat:
                        month_data['total_assets'] = month_data.get('total_assets', 0) + val
                    elif 'liability' in cat:
                        month_data['current_liabilities'] = month_data.get('current_liabilities', 0) + val
                    elif 'receivable' in cat:
                        month_data['accounts_receivable'] = month_data.get('accounts_receivable', 0) + val
                    elif 'payable' in cat:
                        month_data['accounts_payable'] = month_data.get('accounts_payable', 0) + val
                    elif 'inventory' in cat:
                        month_data['inventory'] = month_data.get('inventory', 0) + val
                # Auto-generate derived fields for financial statements
                revenue = month_data.get('revenue', 0)
                total_expenses = month_data.get('other_operating_expense', 0) + month_data.get('interest_expense', 0) + month_data.get('tax_expense', 0)
                # Income Statement
                month_data['net_income'] = revenue - total_expenses
                month_data['gross_profit'] = revenue - month_data.get('cost_of_goods_sold', 0)
                month_data['operating_income'] = revenue - month_data.get('other_operating_expense', 0)

                # Balance Sheet: generate sensible defaults if not provided
                total_assets = month_data.get('total_assets')
                current_liabilities = month_data.get('current_liabilities')
                if total_assets is None:
                    # Estimate assets as 3x revenue if not provided
                    total_assets = revenue * 3 if revenue > 0 else 0
                    month_data['total_assets'] = total_assets
                if current_liabilities is None:
                    # Estimate liabilities as 40% of assets if not provided
                    current_liabilities = total_assets * 0.4
                    month_data['current_liabilities'] = current_liabilities
                # Derive equity if possible
                if total_assets and current_liabilities:
                    month_data['equity'] = total_assets - current_liabilities
                # Current assets if cash or receivables present
                cash = month_data.get('cash', 0)
                ar = month_data.get('accounts_receivable', 0)
                inv = month_data.get('inventory', 0)
                if cash or ar or inv:
                    month_data['current_assets'] = cash + ar + inv
                else:
                    # Estimate current assets as 60% of total assets
                    month_data['current_assets'] = total_assets * 0.6

                # Cash Flow (simplified)
                month_data['operating_cash_flow'] = month_data.get('net_income', 0)  # Simplified: net income as proxy

                statements[month] = month_data
            # Return the latest month as primary data and include monthly summaries
            latest_month = max(statements.keys()) if statements else None
            if latest_month:
                data = statements[latest_month]
                data['monthly_statements'] = statements  # Store all months for trend analysis
            return data

        # Fallback: Try to find headers and extract values
        for column in df.columns:
            if _is_na(column):
                continue
                
            column_str = str(column).lower().strip()
            matched_field = self._match_field(column_str)
            
            if matched_field:
                # Get the first non-null value in this column
                values = df[column].dropna()
                if not values.empty:
                    try:
                        value = float(values.iloc[0])
                        data[matched_field] = value
                    except (ValueError, TypeError):
                        continue
        
        # Also check first column for labels and second column for values
        if len(df.columns) >= 2:
            for idx, row in df.iterrows():
                if _is_na(row.iloc[0]) or _is_na(row.iloc[1]):
                    continue
                    
                label = str(row.iloc[0]).lower().strip()
                matched_field = self._match_field(label)
                
                if matched_field:
                    try:
                        value = float(row.iloc[1])
                        data[matched_field] = value
                    except (ValueError, TypeError):
                        continue
        
        return data
    
    def _extract_data_from_text(self, text: str) -> Dict:
        """Extract financial data from text content"""
        data = {}
        
        # Split text into lines
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to find patterns like "Revenue: 1000000" or "Revenue 1000000"
            for field_name, keywords in self.field_mappings.items():
                for keyword in keywords:
                    # Pattern to match keyword followed by number
                    pattern = rf'{keyword}[:\s]*([\d,]+\.?\d*)'
                    match = re.search(pattern, line, re.IGNORECASE)
                    
                    if match:
                        try:
                            value = float(match.group(1).replace(',', ''))
                            data[field_name] = value
                            break
                        except ValueError:
                            continue
        
        return data
    
    def _match_field(self, text: str) -> Optional[str]:
        """Match text to financial field"""
        text = text.lower().strip()
        
        for field_name, keywords in self.field_mappings.items():
            for keyword in keywords:
                if keyword in text:
                    return field_name
        
        return None
    
    def _validate_and_clean_data(self, data: Dict) -> Dict:
        """Validate and clean extracted data"""
        cleaned_data = {}
        
        # Convert all values to float and validate ranges
        for key, value in data.items():
            try:
                float_value = float(value)
                
                # Basic validation - financial values should be reasonable
                if abs(float_value) > 1e15:  # Values over 1 quadrillion are likely errors
                    continue
                
                cleaned_data[key] = float_value
                
            except (ValueError, TypeError):
                continue
        
        # Calculate derived values if not present
        if 'revenue' in cleaned_data and 'sales_returns' in cleaned_data:
            if 'net_sales' not in cleaned_data:
                cleaned_data['net_sales'] = cleaned_data['revenue'] - cleaned_data['sales_returns']
        
        if 'net_sales' in cleaned_data and 'cost_of_goods_sold' in cleaned_data:
            if 'gross_profit' not in cleaned_data:
                cleaned_data['gross_profit'] = cleaned_data['net_sales'] - cleaned_data['cost_of_goods_sold']
        
        # Calculate totals if components are present
        if 'cash' in cleaned_data and 'accounts_receivable' in cleaned_data:
            if 'current_assets' not in cleaned_data:
                cleaned_data['current_assets'] = cleaned_data['cash'] + cleaned_data['accounts_receivable']
        
        return cleaned_data
