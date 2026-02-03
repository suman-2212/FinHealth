from typing import Dict, List, Optional

class FinancialCalculator:
    """Deterministic financial calculations engine"""
    
    def __init__(self):
        self.industry_benchmarks = {
            'Manufacturing': {
                'avg_gross_profit_margin': 0.25,
                'avg_net_profit_margin': 0.08,
                'avg_current_ratio': 1.5,
                'avg_quick_ratio': 1.0,
                'avg_debt_to_equity': 0.8,
                'avg_interest_coverage': 3.5,
                'avg_asset_turnover': 1.2,
                'avg_inventory_turnover': 6.0,
                'avg_working_capital_days': 45,
                'avg_cash_conversion_cycle': 60
            },
            'Retail': {
                'avg_gross_profit_margin': 0.35,
                'avg_net_profit_margin': 0.05,
                'avg_current_ratio': 1.8,
                'avg_quick_ratio': 0.8,
                'avg_debt_to_equity': 1.0,
                'avg_interest_coverage': 3.0,
                'avg_asset_turnover': 2.0,
                'avg_inventory_turnover': 8.0,
                'avg_working_capital_days': 30,
                'avg_cash_conversion_cycle': 45
            },
            'Agriculture': {
                'avg_gross_profit_margin': 0.20,
                'avg_net_profit_margin': 0.04,
                'avg_current_ratio': 1.3,
                'avg_quick_ratio': 0.7,
                'avg_debt_to_equity': 1.2,
                'avg_interest_coverage': 2.5,
                'avg_asset_turnover': 0.8,
                'avg_inventory_turnover': 4.0,
                'avg_working_capital_days': 60,
                'avg_cash_conversion_cycle': 90
            },
            'Services': {
                'avg_gross_profit_margin': 0.45,
                'avg_net_profit_margin': 0.12,
                'avg_current_ratio': 2.0,
                'avg_quick_ratio': 1.8,
                'avg_debt_to_equity': 0.6,
                'avg_interest_coverage': 5.0,
                'avg_asset_turnover': 1.5,
                'avg_inventory_turnover': 12.0,
                'avg_working_capital_days': 20,
                'avg_cash_conversion_cycle': 30
            },
            'Logistics': {
                'avg_gross_profit_margin': 0.22,
                'avg_net_profit_margin': 0.06,
                'avg_current_ratio': 1.4,
                'avg_quick_ratio': 1.1,
                'avg_debt_to_equity': 1.5,
                'avg_interest_coverage': 2.8,
                'avg_asset_turnover': 1.8,
                'avg_inventory_turnover': 10.0,
                'avg_working_capital_days': 35,
                'avg_cash_conversion_cycle': 50
            },
            'E-commerce': {
                'avg_gross_profit_margin': 0.30,
                'avg_net_profit_margin': 0.07,
                'avg_current_ratio': 1.6,
                'avg_quick_ratio': 1.2,
                'avg_debt_to_equity': 0.9,
                'avg_interest_coverage': 3.2,
                'avg_asset_turnover': 2.5,
                'avg_inventory_turnover': 12.0,
                'avg_working_capital_days': 25,
                'avg_cash_conversion_cycle': 35
            }
        }
    
    def calculate_financial_metrics(self, financial_data: Dict) -> Dict:
        """Calculate all financial metrics from raw financial data"""
        metrics = {}
        
        # Profitability Ratios
        metrics['gross_profit_margin'] = self._calculate_gross_profit_margin(financial_data)
        metrics['net_profit_margin'] = self._calculate_net_profit_margin(financial_data)
        metrics['operating_margin'] = self._calculate_operating_margin(financial_data)
        metrics['return_on_assets'] = self._calculate_return_on_assets(financial_data)
        metrics['return_on_equity'] = self._calculate_return_on_equity(financial_data)
        
        # Liquidity Ratios
        metrics['current_ratio'] = self._calculate_current_ratio(financial_data)
        metrics['quick_ratio'] = self._calculate_quick_ratio(financial_data)
        metrics['cash_ratio'] = self._calculate_cash_ratio(financial_data)
        
        # Leverage Ratios
        metrics['debt_to_equity'] = self._calculate_debt_to_equity(financial_data)
        metrics['debt_to_assets'] = self._calculate_debt_to_assets(financial_data)
        metrics['interest_coverage_ratio'] = self._calculate_interest_coverage_ratio(financial_data)
        
        # Efficiency Ratios
        metrics['asset_turnover'] = self._calculate_asset_turnover(financial_data)
        metrics['inventory_turnover'] = self._calculate_inventory_turnover(financial_data)
        metrics['accounts_receivable_turnover'] = self._calculate_ar_turnover(financial_data)
        metrics['accounts_payable_turnover'] = self._calculate_ap_turnover(financial_data)
        
        # Working Capital Metrics
        metrics['working_capital'] = self._calculate_working_capital(financial_data)
        metrics['cash_conversion_cycle'] = self._calculate_cash_conversion_cycle(financial_data)
        
        return metrics
    
    def _calculate_gross_profit_margin(self, data: Dict) -> Optional[float]:
        """Gross Profit Margin = Gross Profit / Revenue"""
        if data.get('gross_profit') and data.get('revenue'):
            return data['gross_profit'] / data['revenue']
        return None
    
    def _calculate_net_profit_margin(self, data: Dict) -> Optional[float]:
        """Net Profit Margin = Net Income / Revenue"""
        if data.get('net_income') and data.get('revenue'):
            return data['net_income'] / data['revenue']
        return None
    
    def _calculate_operating_margin(self, data: Dict) -> Optional[float]:
        """Operating Margin = Operating Income / Revenue"""
        if data.get('operating_income') and data.get('revenue'):
            return data['operating_income'] / data['revenue']
        return None
    
    def _calculate_return_on_assets(self, data: Dict) -> Optional[float]:
        """Return on Assets = Net Income / Total Assets"""
        if data.get('net_income') and data.get('total_assets'):
            return data['net_income'] / data['total_assets']
        return None
    
    def _calculate_return_on_equity(self, data: Dict) -> Optional[float]:
        """Return on Equity = Net Income / Equity"""
        if data.get('net_income') and data.get('equity'):
            return data['net_income'] / data['equity']
        return None
    
    def _calculate_current_ratio(self, data: Dict) -> Optional[float]:
        # Current ratio = current_assets / current_liabilities
        current_assets = data.get('current_assets', 0)
        current_liabilities = data.get('current_liabilities', 0)
        if current_liabilities:
            return current_assets / current_liabilities
        else:
            return None
    
    def _calculate_quick_ratio(self, data: Dict) -> Optional[float]:
        """Quick Ratio = (Current Assets - Inventory) / Current Liabilities"""
        if (data.get('current_assets') and data.get('current_liabilities') and 
            data.get('inventory') is not None):
            return (data['current_assets'] - data['inventory']) / data['current_liabilities']
        elif data.get('current_assets') and data.get('current_liabilities'):
            # If inventory not available, use current ratio as approximation
            return data['current_assets'] / data['current_liabilities']
        return None
    
    def _calculate_cash_ratio(self, data: Dict) -> Optional[float]:
        """Cash Ratio = Cash / Current Liabilities"""
        if data.get('cash') and data.get('current_liabilities'):
            return data['cash'] / data['current_liabilities']
        return None
    
    def _calculate_debt_to_equity(self, data: Dict) -> Optional[float]:
        """Debt to Equity = Total Debt / Equity"""
        total_debt = (data.get('short_term_debt', 0) + data.get('long_term_debt', 0))
        if total_debt and data.get('equity'):
            return total_debt / data['equity']
        return None
    
    def _calculate_debt_to_assets(self, data: Dict) -> Optional[float]:
        """Debt to Assets = Total Debt / Total Assets"""
        total_debt = (data.get('short_term_debt', 0) + data.get('long_term_debt', 0))
        if total_debt and data.get('total_assets'):
            return total_debt / data['total_assets']
        return None
    
    def _calculate_interest_coverage_ratio(self, data: Dict) -> Optional[float]:
        """Interest Coverage = Operating Income / Interest Expense"""
        if (data.get('operating_income') and data.get('interest_expense') and 
            data['interest_expense'] != 0):
            return data['operating_income'] / data['interest_expense']
        return None
    
    def _calculate_asset_turnover(self, data: Dict) -> Optional[float]:
        """Asset Turnover = Revenue / Total Assets"""
        if data.get('revenue') and data.get('total_assets'):
            return data['revenue'] / data['total_assets']
        return None
    
    def _calculate_inventory_turnover(self, data: Dict) -> Optional[float]:
        """Inventory Turnover = Cost of Goods Sold / Inventory"""
        if data.get('cost_of_goods_sold') and data.get('inventory'):
            return data['cost_of_goods_sold'] / data['inventory']
        return None
    
    def _calculate_ar_turnover(self, data: Dict) -> Optional[float]:
        """Accounts Receivable Turnover = Revenue / Accounts Receivable"""
        if data.get('revenue') and data.get('accounts_receivable'):
            return data['revenue'] / data['accounts_receivable']
        return None
    
    def _calculate_ap_turnover(self, data: Dict) -> Optional[float]:
        """Accounts Payable Turnover = Cost of Goods Sold / Accounts Payable"""
        if data.get('cost_of_goods_sold') and data.get('accounts_payable'):
            return data['cost_of_goods_sold'] / data['accounts_payable']
        return None
    
    def _calculate_working_capital(self, data: Dict) -> Optional[float]:
        """Working Capital = Current Assets - Current Liabilities"""
        if data.get('current_assets') and data.get('current_liabilities'):
            return data['current_assets'] - data['current_liabilities']
        return None
    
    def _calculate_cash_conversion_cycle(self, data: Dict) -> Optional[float]:
        """Cash Conversion Cycle = DIO + DSO - DPO"""
        if (data.get('inventory_turnover') and data.get('accounts_receivable_turnover') and 
            data.get('accounts_payable_turnover')):
            
            # Days Inventory Outstanding
            dio = 365 / data['inventory_turnover'] if data['inventory_turnover'] != 0 else 0
            
            # Days Sales Outstanding
            dso = 365 / data['accounts_receivable_turnover'] if data['accounts_receivable_turnover'] != 0 else 0
            
            # Days Payable Outstanding
            dpo = 365 / data['accounts_payable_turnover'] if data['accounts_payable_turnover'] != 0 else 0
            
            return dio + dso - dpo
        
        return None
    
    def calculate_credit_score(self, metrics: Dict, industry: str) -> Dict:
        """Calculate creditworthiness score using deterministic weighted scoring"""
        
        # Component scores (0-100)
        profitability_score = self._score_profitability(metrics)
        liquidity_score = self._score_liquidity(metrics)
        leverage_score = self._score_leverage(metrics)
        cash_stability_score = self._score_cash_stability(metrics)
        tax_compliance_score = 85  # Default assumption, can be updated with actual data
        industry_risk_modifier = self._get_industry_risk_modifier(industry)
        
        # Weighted scoring
        weights = {
            'profitability': 0.30,
            'liquidity': 0.20,
            'leverage': 0.20,
            'cash_stability': 0.15,
            'tax_compliance': 0.10,
            'industry_risk': 0.05
        }
        
        final_score = (
            profitability_score * weights['profitability'] +
            liquidity_score * weights['liquidity'] +
            leverage_score * weights['leverage'] +
            cash_stability_score * weights['cash_stability'] +
            tax_compliance_score * weights['tax_compliance'] +
            industry_risk_modifier * weights['industry_risk']
        )
        
        # Grade assignment
        if final_score >= 85:
            grade = "A+"
        elif final_score >= 75:
            grade = "A"
        elif final_score >= 65:
            grade = "B+"
        elif final_score >= 55:
            grade = "B"
        elif final_score >= 45:
            grade = "C"
        else:
            grade = "D"
        
        return {
            'profitability_score': profitability_score,
            'liquidity_score': liquidity_score,
            'leverage_score': leverage_score,
            'cash_stability_score': cash_stability_score,
            'tax_compliance_score': tax_compliance_score,
            'industry_risk_modifier': industry_risk_modifier,
            'credit_score': min(100, max(0, final_score)),
            'credit_grade': grade
        }
    
    def _score_profitability(self, metrics: Dict) -> float:
        """Score profitability metrics (0-100)"""
        score = 50  # Base score
        
        if metrics.get('gross_profit_margin'):
            if metrics['gross_profit_margin'] >= 0.4:
                score += 25
            elif metrics['gross_profit_margin'] >= 0.2:
                score += 15
            elif metrics['gross_profit_margin'] >= 0.1:
                score += 5
        
        if metrics.get('net_profit_margin'):
            if metrics['net_profit_margin'] >= 0.15:
                score += 25
            elif metrics['net_profit_margin'] >= 0.08:
                score += 15
            elif metrics['net_profit_margin'] >= 0.03:
                score += 5
        
        return min(100, max(0, score))
    
    def _score_liquidity(self, metrics: Dict) -> float:
        """Score liquidity metrics (0-100)"""
        score = 50  # Base score
        
        if metrics.get('current_ratio'):
            if metrics['current_ratio'] >= 2.0:
                score += 25
            elif metrics['current_ratio'] >= 1.5:
                score += 15
            elif metrics['current_ratio'] >= 1.0:
                score += 5
        
        if metrics.get('quick_ratio'):
            if metrics['quick_ratio'] >= 1.5:
                score += 25
            elif metrics['quick_ratio'] >= 1.0:
                score += 15
            elif metrics['quick_ratio'] >= 0.8:
                score += 5
        
        return min(100, max(0, score))
    
    def _score_leverage(self, metrics: Dict) -> float:
        """Score leverage metrics (0-100)"""
        score = 50  # Base score
        
        if metrics.get('debt_to_equity'):
            if metrics['debt_to_equity'] <= 0.5:
                score += 25
            elif metrics['debt_to_equity'] <= 1.0:
                score += 15
            elif metrics['debt_to_equity'] <= 1.5:
                score += 5
        
        if metrics.get('interest_coverage_ratio'):
            if metrics['interest_coverage_ratio'] >= 5.0:
                score += 25
            elif metrics['interest_coverage_ratio'] >= 3.0:
                score += 15
            elif metrics['interest_coverage_ratio'] >= 2.0:
                score += 5
        
        return min(100, max(0, score))
    
    def _score_cash_stability(self, metrics: Dict) -> float:
        """Score cash stability metrics (0-100)"""
        score = 50  # Base score
        
        if metrics.get('cash_ratio'):
            if metrics['cash_ratio'] >= 0.5:
                score += 25
            elif metrics['cash_ratio'] >= 0.3:
                score += 15
            elif metrics['cash_ratio'] >= 0.1:
                score += 5
        
        if metrics.get('working_capital'):
            # Positive working capital is good
            if metrics['working_capital'] > 0:
                score += 25
        
        return min(100, max(0, score))
    
    def _get_industry_risk_modifier(self, industry: str) -> float:
        """Get industry risk modifier score (0-100)"""
        industry_risk_scores = {
            'Manufacturing': 75,
            'Retail': 70,
            'Agriculture': 60,
            'Services': 85,
            'Logistics': 72,
            'E-commerce': 68
        }
        
        return industry_risk_scores.get(industry, 70)
    
    def generate_forecast(self, historical_data: List[Dict], periods: int = 12) -> Dict:
        """Generate financial forecast using linear regression"""
        if not historical_data:
            return self._generate_simple_forecast(historical_data, periods)

        data_sorted = sorted(historical_data, key=lambda x: x.get('period', ''))

        forecasts: Dict = {
            'confidence_level': 0.95,
            'upper_bound': [],
            'lower_bound': []
        }

        revenue_series = [d.get('revenue') for d in data_sorted if d.get('revenue') is not None]
        if revenue_series:
            forecasts['revenue_forecast'] = self._linear_regression_forecast(revenue_series, periods)

        expense_series = [d.get('total_expenses') for d in data_sorted if d.get('total_expenses') is not None]
        if not expense_series:
            expense_series = [d.get('cost_of_goods_sold') for d in data_sorted if d.get('cost_of_goods_sold') is not None]
        if expense_series:
            forecasts['expense_forecast'] = self._linear_regression_forecast(expense_series, periods)

        cash_series = [d.get('net_cash_flow') for d in data_sorted if d.get('net_cash_flow') is not None]
        if cash_series:
            forecasts['cash_flow_forecast'] = self._linear_regression_forecast(cash_series, periods)

        if 'revenue_forecast' in forecasts and len(forecasts['revenue_forecast']) >= 2 and forecasts['revenue_forecast'][0] not in (0, None):
            forecasts['growth_rate'] = (forecasts['revenue_forecast'][-1] - forecasts['revenue_forecast'][0]) / forecasts['revenue_forecast'][0]
        else:
            forecasts['growth_rate'] = 0

        return forecasts
    
    def calculate_financial_health_score(self, metrics: Dict) -> Dict:
        """Calculate a composite financial health score (0-100)"""
        score = 0
        weights = {
            'profitability': 0.25,
            'liquidity': 0.20,
            'leverage': 0.20,
            'efficiency': 0.15,
            'cash_stability': 0.20
        }
        components = {}
        # Profitability component
        net_margin = metrics.get('net_profit_margin')
        if net_margin is not None:
            if net_margin >= 0.15:
                components['profitability'] = 100
            elif net_margin >= 0.08:
                components['profitability'] = 80
            elif net_margin >= 0.03:
                components['profitability'] = 60
            elif net_margin >= 0:
                components['profitability'] = 40
            else:
                components['profitability'] = 0
        else:
            components['profitability'] = 50
        # Liquidity component
        current_ratio = metrics.get('current_ratio')
        if current_ratio is not None:
            if current_ratio >= 2.0:
                components['liquidity'] = 100
            elif current_ratio >= 1.5:
                components['liquidity'] = 80
            elif current_ratio >= 1.0:
                components['liquidity'] = 60
            elif current_ratio >= 0.5:
                components['liquidity'] = 40
            else:
                components['liquidity'] = 0
        else:
            components['liquidity'] = 50
        # Leverage component
        debt_to_equity = metrics.get('debt_to_equity')
        if debt_to_equity is not None:
            if debt_to_equity <= 0.5:
                components['leverage'] = 100
            elif debt_to_equity <= 1.0:
                components['leverage'] = 80
            elif debt_to_equity <= 1.5:
                components['leverage'] = 60
            elif debt_to_equity <= 2.0:
                components['leverage'] = 40
            else:
                components['leverage'] = 0
        else:
            components['leverage'] = 50
        # Efficiency component (asset turnover)
        asset_turnover = metrics.get('asset_turnover')
        if asset_turnover is not None:
            if asset_turnover >= 2.0:
                components['efficiency'] = 100
            elif asset_turnover >= 1.5:
                components['efficiency'] = 80
            elif asset_turnover >= 1.0:
                components['efficiency'] = 60
            elif asset_turnover >= 0.5:
                components['efficiency'] = 40
            else:
                components['efficiency'] = 0
        else:
            components['efficiency'] = 50
        # Cash stability component (working capital)
        working_capital = metrics.get('working_capital')
        if working_capital is not None:
            if working_capital > 0:
                components['cash_stability'] = 100
            else:
                components['cash_stability'] = 0
        else:
            components['cash_stability'] = 50
        # Weighted score
        for k, v in components.items():
            score += v * weights[k]
        # Grade
        if score >= 85:
            grade = 'Excellent'
        elif score >= 70:
            grade = 'Good'
        elif score >= 55:
            grade = 'Fair'
        elif score >= 40:
            grade = 'Poor'
        else:
            grade = 'Critical'
        return {
            'financial_health_score': round(score, 1),
            'grade': grade,
            'components': components
        }
    
    def _linear_regression_forecast(self, series: List[float], periods: int) -> List[float]:
        """Generate forecast using linear regression"""
        clean_series = [float(v) for v in series if v is not None]
        if len(clean_series) < 2:
            base = clean_series[0] if clean_series else 0.0
            return [base] * periods

        # Simple OLS: y = a*x + b
        n = len(clean_series)
        xs = list(range(n))
        x_mean = sum(xs) / n
        y_mean = sum(clean_series) / n

        denom = sum((x - x_mean) ** 2 for x in xs)
        if denom == 0:
            a = 0.0
        else:
            a = sum((xs[i] - x_mean) * (clean_series[i] - y_mean) for i in range(n)) / denom
        b = y_mean - a * x_mean

        forecast = []
        for i in range(n, n + periods):
            forecast.append(a * i + b)
        return forecast
    
    def _generate_simple_forecast(self, historical_data: List[Dict], periods: int) -> Dict:
        """Generate simple forecast based on average growth"""
        if not historical_data:
            return {
                'revenue_forecast': [0] * periods,
                'expense_forecast': [0] * periods,
                'cash_flow_forecast': [0] * periods,
                'growth_rate': 0,
                'confidence_level': 0.5
            }
        
        # Use last period values as baseline
        last_period = historical_data[-1]
        
        revenue = last_period.get('revenue', 0)
        expenses = last_period.get('cost_of_goods_sold', 0) + last_period.get('salaries_wages', 0)
        cash_flow = last_period.get('net_cash_flow', 0)
        
        # Apply simple growth assumption
        growth_rate = 0.05  # 5% growth assumption
        
        forecasts = {
            'revenue_forecast': [revenue * (1 + growth_rate) ** i for i in range(periods)],
            'expense_forecast': [expenses * (1 + growth_rate * 0.8) ** i for i in range(periods)],
            'cash_flow_forecast': [cash_flow * (1 + growth_rate * 0.6) ** i for i in range(periods)],
            'growth_rate': growth_rate,
            'confidence_level': 0.5
        }
        
        return forecasts
