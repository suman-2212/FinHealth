import numpy as np
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
from models import MonthlySummary, ForecastSummary

class FinancialForecaster:
    """Deterministic financial forecasting engine"""
    
    def generate_forecast(self, company_id: str, db: Session, months_ahead: int = 6, 
                         forecast_type: str = 'Base') -> Dict[str, Any]:
        """Generate financial forecast for specified months ahead"""
        
        # Get historical data (last 3-6 months)
        summaries = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).limit(6).all()
        
        if len(summaries) < 3:
            return self._empty_forecast_response()
        
        # Prepare historical data
        historical_data = self._prepare_historical_data(summaries)
        
        # Calculate growth rates and volatility
        revenue_growth_rate = self._calculate_growth_rate(historical_data['revenues'])
        expense_growth_rate = self._calculate_growth_rate(historical_data['expenses'])
        cash_flow_volatility = self._calculate_volatility(historical_data['cash_flows'])
        
        # Apply forecast type adjustments
        revenue_growth_rate, expense_growth_rate = self._apply_forecast_type_adjustments(
            revenue_growth_rate, expense_growth_rate, forecast_type, cash_flow_volatility
        )
        
        # Generate projections
        projections = self._generate_projections(
            historical_data, revenue_growth_rate, expense_growth_rate, months_ahead
        )
        
        # Calculate runway
        runway_months = self._calculate_runway(historical_data, projections)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            len(summaries), cash_flow_volatility, forecast_type
        )
        
        # Store projections in database
        self._store_projections(company_id, db, projections, forecast_type, 
                              revenue_growth_rate, expense_growth_rate, 
                              cash_flow_volatility, confidence_score)
        
        return {
            'forecast_type': forecast_type,
            'months_ahead': months_ahead,
            'historical_months_used': len(summaries),
            'projections': projections,
            'runway_months': runway_months,
            'confidence_score': confidence_score,
            'revenue_growth_rate': float(revenue_growth_rate),
            'expense_growth_rate': float(expense_growth_rate),
            'cash_flow_volatility': float(cash_flow_volatility),
            'historical_data': {
                'revenues': [float(r) for r in reversed(historical_data['revenues'])],
                'expenses': [float(e) for e in reversed(historical_data['expenses'])],
                'cash_flows': [float(c) for c in reversed(historical_data['cash_flows'])],
                'months': list(reversed(historical_data['months']))
            }
        }
    
    def _prepare_historical_data(self, summaries: List) -> Dict[str, List]:
        """Prepare historical data arrays"""
        data = {
            'revenues': [],
            'expenses': [],
            'cash_flows': [],
            'months': []
        }
        
        for summary in reversed(summaries):  # Oldest to newest
            data['revenues'].append(float(summary.revenue or 0))
            data['expenses'].append(float(summary.operating_expense or 0))
            data['cash_flows'].append(float(summary.operating_cash_flow or 0))
            data['months'].append(summary.month)
        
        return data
    
    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate compound monthly growth rate"""
        if len(values) < 2 or values[0] == 0:
            return 0
        
        start_value = values[0]
        end_value = values[-1]
        periods = len(values) - 1
        
        return (end_value / start_value) ** (1/periods) - 1
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate coefficient of variation"""
        if len(values) < 2 or not any(values):
            return 1.0
        
        values_array = np.array(values)
        mean = np.mean(values_array)
        if mean == 0:
            return 1.0
        
        std_dev = np.std(values_array)
        return std_dev / abs(mean)
    
    def _apply_forecast_type_adjustments(self, revenue_growth: float, expense_growth: float,
                                        forecast_type: str, volatility: float) -> Tuple[float, float]:
        """Apply forecast type adjustments based on volatility"""
        volatility_factor = min(1.5, max(0.5, 1 - volatility))
        
        if forecast_type == 'Optimistic':
            # More optimistic revenue growth, conservative expense growth
            adjusted_revenue_growth = revenue_growth * (1 + (0.2 * volatility_factor))
            adjusted_expense_growth = expense_growth * (1 - (0.1 * volatility_factor))
        elif forecast_type == 'Conservative':
            # Conservative revenue growth, higher expense growth
            adjusted_revenue_growth = revenue_growth * (1 - (0.2 * volatility_factor))
            adjusted_expense_growth = expense_growth * (1 + (0.1 * volatility_factor))
        else:  # Base
            adjusted_revenue_growth = revenue_growth
            adjusted_expense_growth = expense_growth
        
        return adjusted_revenue_growth, adjusted_expense_growth
    
    def _generate_projections(self, historical_data: Dict, revenue_growth: float,
                            expense_growth: float, months_ahead: int) -> List[Dict]:
        """Generate month-by-month projections"""
        projections = []
        
        # Get last actual values
        last_revenue = historical_data['revenues'][-1]
        last_expense = historical_data['expenses'][-1]
        last_cash_flow = historical_data['cash_flows'][-1]
        last_month = historical_data['months'][-1]
        
        # Parse last month to get date
        year, month = map(int, last_month.split('-'))
        last_date = datetime(year, month, 1)
        
        for i in range(1, months_ahead + 1):
            # Project next month
            projected_revenue = last_revenue * (1 + revenue_growth) ** i
            projected_expense = last_expense * (1 + expense_growth) ** i
            projected_net_income = projected_revenue - projected_expense
            
            # Estimate cash flow (typically 70-90% of net income for stable businesses)
            cash_flow_ratio = 0.8  # Can be adjusted based on historical patterns
            projected_cash_flow = projected_net_income * cash_flow_ratio
            
            # Calculate projection month
            projection_date = last_date + timedelta(days=30 * i)
            projection_month = projection_date.strftime('%Y-%m')
            
            projections.append({
                'projection_month': projection_month,
                'projected_revenue': round(projected_revenue, 2),
                'projected_expenses': round(projected_expense, 2),
                'projected_net_income': round(projected_net_income, 2),
                'projected_cash_flow': round(projected_cash_flow, 2)
            })
        
        return projections
    
    def _calculate_runway(self, historical_data: Dict, projections: List[Dict]) -> float:
        """Calculate cash runway in months"""
        # Get current cash balance (use last cash flow as proxy)
        current_cash = max(0, historical_data['cash_flows'][-1])
        
        # Calculate average monthly burn (negative cash flow)
        avg_burn = 0
        negative_months = [cf for cf in historical_data['cash_flows'] if cf < 0]
        
        if negative_months:
            avg_burn = abs(sum(negative_months) / len(negative_months))
        
        # Include projected negative cash flows
        projected_negative = [p['projected_cash_flow'] for p in projections if p['projected_cash_flow'] < 0]
        if projected_negative:
            avg_burn = (avg_burn * len(negative_months) + abs(sum(projected_negative))) / (len(negative_months) + len(projected_negative))
        
        if avg_burn == 0:
            return 999.99  # Infinite runway
        
        return current_cash / avg_burn
    
    def _calculate_confidence_score(self, data_months: int, volatility: float, forecast_type: str) -> float:
        """Calculate forecast confidence score (0-100)"""
        # Base confidence from data availability
        if data_months >= 6:
            base_confidence = 80
        elif data_months >= 4:
            base_confidence = 60
        else:
            base_confidence = 40
        
        # Adjust for volatility
        volatility_penalty = min(30, volatility * 30)
        adjusted_confidence = base_confidence - volatility_penalty
        
        # Adjust for forecast type
        if forecast_type == 'Base':
            type_multiplier = 1.0
        elif forecast_type == 'Optimistic':
            type_multiplier = 0.8
        else:  # Conservative
            type_multiplier = 0.9
        
        final_confidence = adjusted_confidence * type_multiplier
        return max(0, min(100, final_confidence))
    
    def _store_projections(self, company_id: str, db: Session, projections: List[Dict],
                          forecast_type: str, revenue_growth: float, expense_growth: float,
                          volatility: float, confidence: float):
        """Store projections in database"""
        # Delete existing forecasts for this company and type
        db.query(ForecastSummary).filter(
            ForecastSummary.company_id == company_id,
            ForecastSummary.forecast_type == forecast_type
        ).delete()
        
        # Insert new projections
        for projection in projections:
            forecast = ForecastSummary(
                company_id=company_id,
                projection_month=projection['projection_month'],
                projected_revenue=projection['projected_revenue'],
                projected_expenses=projection['projected_expenses'],
                projected_net_income=projection['projected_net_income'],
                projected_cash_flow=projection['projected_cash_flow'],
                forecast_type=forecast_type,
                months_used=len(projections),
                revenue_growth_rate=revenue_growth,
                expense_growth_rate=expense_growth,
                cash_flow_volatility=volatility,
                confidence_score=confidence
            )
            db.add(forecast)
        
        db.commit()
    
    def _empty_forecast_response(self) -> Dict[str, Any]:
        """Return empty response when insufficient data"""
        return {
            'forecast_type': 'Base',
            'months_ahead': 0,
            'historical_months_used': 0,
            'projections': [],
            'runway_months': None,
            'confidence_score': None,
            'revenue_growth_rate': None,
            'expense_growth_rate': None,
            'cash_flow_volatility': None,
            'historical_data': {
                'revenues': [],
                'expenses': [],
                'cash_flows': [],
                'months': []
            }
        }
