import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
from models import MonthlySummary, IndustryBenchmarks, BenchmarkSummary

class BenchmarkAnalyzer:
    """Industry benchmarking and comparison engine"""
    
    # Default industry type (can be extended with company classification)
    DEFAULT_INDUSTRY = 'General'
    
    # Industry types and their typical characteristics
    INDUSTRY_TYPES = {
        'Retail': {
            'description': 'Retail and consumer goods',
            'typical_metrics': ['gross_margin', 'net_profit_margin', 'current_ratio', 'inventory_turnover']
        },
        'Manufacturing': {
            'description': 'Manufacturing and industrial',
            'typical_metrics': ['gross_margin', 'operating_margin', 'debt_to_equity', 'cash_conversion_cycle']
        },
        'Services': {
            'description': 'Professional services and consulting',
            'typical_metrics': ['net_profit_margin', 'operating_margin', 'revenue_growth_rate', 'quick_ratio']
        },
        'Technology': {
            'description': 'Technology and software',
            'typical_metrics': ['net_profit_margin', 'revenue_growth_rate', 'debt_to_equity', 'current_ratio']
        },
        'General': {
            'description': 'General business across industries',
            'typical_metrics': ['net_profit_margin', 'debt_to_equity', 'current_ratio', 'revenue_growth_rate']
        }
    }
    
    def analyze_benchmarks(self, company_id: str, db: Session, industry_type: Optional[str] = None) -> Dict[str, Any]:
        """Perform comprehensive benchmark analysis"""
        
        # Get latest financial data
        latest_summary = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).first()
        
        if not latest_summary:
            return self._empty_benchmark_response()
        
        # Get historical data for growth calculations
        summaries = db.query(MonthlySummary).filter(
            MonthlySummary.company_id == company_id
        ).order_by(MonthlySummary.month.desc()).limit(12).all()
        
        # Determine industry type
        if not industry_type:
            industry_type = self._classify_industry(latest_summary, summaries)
        
        # Calculate company metrics
        company_metrics = self._calculate_company_metrics(latest_summary, summaries)
        
        # Get industry benchmarks
        industry_benchmarks = self._get_industry_benchmarks(db, industry_type)
        
        # Compare against benchmarks
        benchmark_results = self._compare_with_benchmarks(company_metrics, industry_benchmarks)
        
        # Calculate overall summary
        overall_summary = self._calculate_overall_summary(benchmark_results)
        
        # Store results
        self._store_benchmark_summary(company_id, db, industry_type, benchmark_results, overall_summary)
        
        return {
            'industry_type': industry_type,
            'industry_description': self.INDUSTRY_TYPES[industry_type]['description'],
            'company_metrics': company_metrics,
            'benchmark_results': benchmark_results,
            'overall_summary': overall_summary,
            'last_updated': latest_summary.month
        }
    
    def _classify_industry(self, latest: MonthlySummary, summaries: List) -> str:
        """Simple industry classification based on financial characteristics"""
        # This is a simplified classification - in production, use more sophisticated methods
        gross_margin = float(latest.gross_margin or 0)
        revenue = float(latest.revenue or 0)
        total_assets = float(latest.total_assets or 0)
        
        # Simple heuristics for industry classification
        if gross_margin > 0.4 and revenue > 1000000:
            return 'Technology'
        elif gross_margin > 0.3 and total_assets > 500000:
            return 'Manufacturing'
        elif gross_margin > 0.2 and revenue < 1000000:
            return 'Services'
        elif gross_margin < 0.3:
            return 'Retail'
        else:
            return 'General'
    
    def _calculate_company_metrics(self, latest: MonthlySummary, summaries: List) -> Dict[str, float]:
        """Calculate company's financial metrics"""
        metrics = {}
        
        # Profitability metrics
        metrics['net_profit_margin'] = float(latest.net_margin or 0)
        metrics['gross_margin'] = float(latest.gross_margin or 0)
        
        # Calculate operating margin if we have operating expense
        if latest.operating_expense and latest.revenue:
            operating_income = float(latest.revenue) - float(latest.operating_expense)
            metrics['operating_margin'] = operating_income / float(latest.revenue)
        else:
            metrics['operating_margin'] = 0
        
        # Liquidity metrics
        metrics['current_ratio'] = float(latest.current_ratio or 0)
        
        # Estimate quick ratio (assuming 60% of current assets are quick assets)
        if latest.current_ratio:
            metrics['quick_ratio'] = float(latest.current_ratio) * 0.6
        else:
            metrics['quick_ratio'] = 0
        
        # Leverage metrics
        metrics['debt_to_equity'] = float(latest.debt_to_equity or 0)
        
        # Growth metrics
        if len(summaries) > 1:
            revenues = [float(s.revenue or 0) for s in reversed(summaries)]
            if revenues[0] > 0:
                growth_rate = (revenues[-1] / revenues[0]) ** (1/(len(revenues)-1)) - 1
                metrics['revenue_growth_rate'] = growth_rate
            else:
                metrics['revenue_growth_rate'] = 0
        else:
            metrics['revenue_growth_rate'] = 0
        
        # Cash conversion cycle (simplified calculation - skip if insufficient data)
        # Note: This requires receivables, inventory, and payables which aren't in MonthlySummary
        # Setting to 0 for now, can be enhanced with additional data sources
        metrics['cash_conversion_cycle'] = 0
        
        return metrics
    
    def _get_industry_benchmarks(self, db: Session, industry_type: str) -> Dict[str, Dict]:
        """Get industry benchmarks from database or use defaults"""
        benchmarks = {}
        
        # Try to get from database first
        stored_benchmarks = db.query(IndustryBenchmarks).filter(
            IndustryBenchmarks.industry_type == industry_type
        ).all()
        
        if stored_benchmarks:
            for benchmark in stored_benchmarks:
                benchmarks[benchmark.metric_name] = {
                    'industry_avg': float(benchmark.industry_avg or 0),
                    'top_quartile': float(benchmark.top_quartile or 0),
                    'bottom_quartile': float(benchmark.bottom_quartile or 0),
                    'percentile_distribution': benchmark.percentile_distribution or []
                }
        else:
            # Use default benchmarks if not stored
            benchmarks = self._get_default_benchmarks(industry_type)
        
        return benchmarks
    
    def _get_default_benchmarks(self, industry_type: str) -> Dict[str, Dict]:
        """Get default industry benchmarks"""
        defaults = {
            'Retail': {
                'net_profit_margin': {'industry_avg': 0.03, 'top_quartile': 0.06, 'bottom_quartile': 0.01},
                'gross_margin': {'industry_avg': 0.35, 'top_quartile': 0.45, 'bottom_quartile': 0.25},
                'current_ratio': {'industry_avg': 1.5, 'top_quartile': 2.0, 'bottom_quartile': 1.0},
                'debt_to_equity': {'industry_avg': 1.2, 'top_quartile': 0.8, 'bottom_quartile': 2.0},
                'revenue_growth_rate': {'industry_avg': 0.08, 'top_quartile': 0.15, 'bottom_quartile': 0.02},
                'operating_margin': {'industry_avg': 0.06, 'top_quartile': 0.10, 'bottom_quartile': 0.03},
                'quick_ratio': {'industry_avg': 0.8, 'top_quartile': 1.2, 'bottom_quartile': 0.5},
                'cash_conversion_cycle': {'industry_avg': 45, 'top_quartile': 30, 'bottom_quartile': 60}
            },
            'Manufacturing': {
                'net_profit_margin': {'industry_avg': 0.05, 'top_quartile': 0.08, 'bottom_quartile': 0.02},
                'gross_margin': {'industry_avg': 0.30, 'top_quartile': 0.40, 'bottom_quartile': 0.20},
                'current_ratio': {'industry_avg': 1.8, 'top_quartile': 2.5, 'bottom_quartile': 1.2},
                'debt_to_equity': {'industry_avg': 1.5, 'top_quartile': 1.0, 'bottom_quartile': 2.5},
                'revenue_growth_rate': {'industry_avg': 0.06, 'top_quartile': 0.12, 'bottom_quartile': 0.01},
                'operating_margin': {'industry_avg': 0.10, 'top_quartile': 0.15, 'bottom_quartile': 0.05},
                'quick_ratio': {'industry_avg': 1.0, 'top_quartile': 1.5, 'bottom_quartile': 0.7},
                'cash_conversion_cycle': {'industry_avg': 60, 'top_quartile': 45, 'bottom_quartile': 90}
            },
            'Services': {
                'net_profit_margin': {'industry_avg': 0.12, 'top_quartile': 0.18, 'bottom_quartile': 0.06},
                'gross_margin': {'industry_avg': 0.55, 'top_quartile': 0.65, 'bottom_quartile': 0.45},
                'current_ratio': {'industry_avg': 1.6, 'top_quartile': 2.2, 'bottom_quartile': 1.1},
                'debt_to_equity': {'industry_avg': 0.8, 'top_quartile': 0.5, 'bottom_quartile': 1.5},
                'revenue_growth_rate': {'industry_avg': 0.10, 'top_quartile': 0.20, 'bottom_quartile': 0.03},
                'operating_margin': {'industry_avg': 0.15, 'top_quartile': 0.22, 'bottom_quartile': 0.08},
                'quick_ratio': {'industry_avg': 1.2, 'top_quartile': 1.8, 'bottom_quartile': 0.8},
                'cash_conversion_cycle': {'industry_avg': 30, 'top_quartile': 20, 'bottom_quartile': 45}
            },
            'Technology': {
                'net_profit_margin': {'industry_avg': 0.15, 'top_quartile': 0.25, 'bottom_quartile': 0.08},
                'gross_margin': {'industry_avg': 0.65, 'top_quartile': 0.75, 'bottom_quartile': 0.55},
                'current_ratio': {'industry_avg': 2.0, 'top_quartile': 3.0, 'bottom_quartile': 1.3},
                'debt_to_equity': {'industry_avg': 0.6, 'top_quartile': 0.3, 'bottom_quartile': 1.2},
                'revenue_growth_rate': {'industry_avg': 0.25, 'top_quartile': 0.40, 'bottom_quartile': 0.10},
                'operating_margin': {'industry_avg': 0.20, 'top_quartile': 0.30, 'bottom_quartile': 0.10},
                'quick_ratio': {'industry_avg': 1.5, 'top_quartile': 2.5, 'bottom_quartile': 1.0},
                'cash_conversion_cycle': {'industry_avg': 25, 'top_quartile': 15, 'bottom_quartile': 40}
            },
            'General': {
                'net_profit_margin': {'industry_avg': 0.08, 'top_quartile': 0.12, 'bottom_quartile': 0.04},
                'gross_margin': {'industry_avg': 0.40, 'top_quartile': 0.50, 'bottom_quartile': 0.30},
                'current_ratio': {'industry_avg': 1.7, 'top_quartile': 2.3, 'bottom_quartile': 1.2},
                'debt_to_equity': {'industry_avg': 1.0, 'top_quartile': 0.7, 'bottom_quartile': 1.8},
                'revenue_growth_rate': {'industry_avg': 0.08, 'top_quartile': 0.15, 'bottom_quartile': 0.02},
                'operating_margin': {'industry_avg': 0.12, 'top_quartile': 0.18, 'bottom_quartile': 0.06},
                'quick_ratio': {'industry_avg': 1.0, 'top_quartile': 1.5, 'bottom_quartile': 0.7},
                'cash_conversion_cycle': {'industry_avg': 40, 'top_quartile': 30, 'bottom_quartile': 60}
            }
        }
        
        return defaults.get(industry_type, defaults['General'])
    
    def _compare_with_benchmarks(self, company_metrics: Dict, industry_benchmarks: Dict) -> Dict[str, Dict]:
        """Compare company metrics against industry benchmarks"""
        results = {}
        
        for metric_name, company_value in company_metrics.items():
            if metric_name in industry_benchmarks:
                benchmark = industry_benchmarks[metric_name]
                
                # Calculate percentile rank (simplified)
                percentile = self._calculate_percentile(company_value, benchmark)
                
                # Determine status
                status = self._determine_status(company_value, benchmark, percentile)
                
                # Calculate deviation from industry average
                deviation = self._calculate_deviation(company_value, benchmark['industry_avg'])
                
                results[metric_name] = {
                    'value': company_value,
                    'industry_avg': benchmark['industry_avg'],
                    'percentile': percentile,
                    'status': status,
                    'deviation_percent': deviation,
                    'top_quartile': benchmark['top_quartile'],
                    'bottom_quartile': benchmark['bottom_quartile']
                }
        
        return results
    
    def _calculate_percentile(self, value: float, benchmark: Dict) -> float:
        """Calculate percentile rank for a value"""
        # Simplified percentile calculation
        if value >= benchmark['top_quartile']:
            return 75 + min(25, (value - benchmark['top_quartile']) / benchmark['top_quartile'] * 25)
        elif value >= benchmark['industry_avg']:
            return 50 + ((value - benchmark['industry_avg']) / (benchmark['top_quartile'] - benchmark['industry_avg'])) * 25
        elif value >= benchmark['bottom_quartile']:
            return 25 + ((value - benchmark['bottom_quartile']) / (benchmark['industry_avg'] - benchmark['bottom_quartile'])) * 25
        else:
            return max(0, (value / benchmark['bottom_quartile']) * 25)
    
    def _determine_status(self, value: float, benchmark: Dict, percentile: float) -> str:
        """Determine performance status"""
        if percentile >= 75:
            return 'Top 25%'
        elif percentile >= 60:
            return 'Above Average'
        elif percentile >= 40:
            return 'Near Average'
        elif percentile >= 25:
            return 'Below Average'
        else:
            return 'Bottom 25%'
    
    def _calculate_deviation(self, value: float, industry_avg: float) -> float:
        """Calculate percentage deviation from industry average"""
        if industry_avg == 0:
            return 0
        return ((value - industry_avg) / industry_avg) * 100
    
    def _calculate_overall_summary(self, benchmark_results: Dict) -> Dict:
        """Calculate overall performance summary"""
        if not benchmark_results:
            return {
                'overall_percentile': 0,
                'metrics_above_avg': 0,
                'total_metrics': 0,
                'summary_text': 'No data available'
            }
        
        percentiles = [result['percentile'] for result in benchmark_results.values()]
        overall_percentile = sum(percentiles) / len(percentiles)
        
        metrics_above_avg = sum(1 for result in benchmark_results.values() if result['percentile'] > 50)
        total_metrics = len(benchmark_results)
        
        # Generate summary text
        if overall_percentile >= 75:
            summary_text = 'Excellent performance - significantly above industry standards'
        elif overall_percentile >= 60:
            summary_text = 'Strong performance - above industry average'
        elif overall_percentile >= 40:
            summary_text = 'Average performance - near industry standards'
        elif overall_percentile >= 25:
            summary_text = 'Below average performance - room for improvement'
        else:
            summary_text = 'Poor performance - significantly below industry standards'
        
        return {
            'overall_percentile': overall_percentile,
            'metrics_above_avg': metrics_above_avg,
            'total_metrics': total_metrics,
            'summary_text': summary_text
        }
    
    def _store_benchmark_summary(self, company_id: str, db: Session, industry_type: str,
                                benchmark_results: Dict, overall_summary: Dict):
        """Store benchmark summary in database"""
        existing = db.query(BenchmarkSummary).filter(
            BenchmarkSummary.company_id == company_id
        ).first()
        
        if existing:
            existing.industry_type = industry_type
            existing.net_profit_margin = benchmark_results.get('net_profit_margin')
            existing.gross_margin = benchmark_results.get('gross_margin')
            existing.debt_to_equity = benchmark_results.get('debt_to_equity')
            existing.current_ratio = benchmark_results.get('current_ratio')
            existing.quick_ratio = benchmark_results.get('quick_ratio')
            existing.revenue_growth_rate = benchmark_results.get('revenue_growth_rate')
            existing.operating_margin = benchmark_results.get('operating_margin')
            existing.cash_conversion_cycle = benchmark_results.get('cash_conversion_cycle')
            existing.overall_percentile = overall_summary['overall_percentile']
            existing.metrics_above_avg = overall_summary['metrics_above_avg']
            existing.total_metrics = overall_summary['total_metrics']
            existing.last_updated = func.now()
        else:
            new_summary = BenchmarkSummary(
                company_id=company_id,
                industry_type=industry_type,
                net_profit_margin=benchmark_results.get('net_profit_margin'),
                gross_margin=benchmark_results.get('gross_margin'),
                debt_to_equity=benchmark_results.get('debt_to_equity'),
                current_ratio=benchmark_results.get('current_ratio'),
                quick_ratio=benchmark_results.get('quick_ratio'),
                revenue_growth_rate=benchmark_results.get('revenue_growth_rate'),
                operating_margin=benchmark_results.get('operating_margin'),
                cash_conversion_cycle=benchmark_results.get('cash_conversion_cycle'),
                overall_percentile=overall_summary['overall_percentile'],
                metrics_above_avg=overall_summary['metrics_above_avg'],
                total_metrics=overall_summary['total_metrics']
            )
            db.add(new_summary)
        
        db.commit()
    
    def _empty_benchmark_response(self) -> Dict[str, Any]:
        """Return empty response when insufficient data"""
        return {
            'industry_type': 'Unknown',
            'industry_description': 'No data available',
            'company_metrics': {},
            'benchmark_results': {},
            'overall_summary': {
                'overall_percentile': 0,
                'metrics_above_avg': 0,
                'total_metrics': 0,
                'summary_text': 'Upload financial data to generate benchmarking analysis'
            },
            'last_updated': None
        }
