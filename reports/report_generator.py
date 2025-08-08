import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import config

class ReportGenerator:
    """
    Generates weekly ROI reports in PDF format
    """
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or config.REPORT_OUTPUT_DIR
        self.styles = getSampleStyleSheet()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_weekly_report(self, betting_data: List[Dict], 
                             start_date: datetime, end_date: datetime) -> str:
        """
        Generate weekly ROI report
        
        Args:
            betting_data: List of betting records
            start_date: Start of reporting period
            end_date: End of reporting period
            
        Returns:
            Path to generated PDF file
        """
        # Create filename
        filename = f"weekly_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        title = Paragraph("Weekly Betting Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Add date range
        date_style = ParagraphStyle(
            'DateRange',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=1
        )
        
        date_range = f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(date_range, date_style))
        story.append(Spacer(1, 30))
        
        # Generate summary statistics
        summary_stats = self._calculate_summary_statistics(betting_data)
        story.extend(self._create_summary_section(summary_stats))
        
        story.append(Spacer(1, 20))
        
        # Generate market breakdown
        market_stats = self._calculate_market_statistics(betting_data)
        story.extend(self._create_market_breakdown_section(market_stats))
        
        story.append(Spacer(1, 20))
        
        # Generate performance charts (if matplotlib is available)
        try:
            chart_path = self._create_performance_chart(betting_data, start_date, end_date)
            if chart_path and os.path.exists(chart_path):
                story.append(Paragraph("Performance Chart", self.styles['Heading2']))
                story.append(Spacer(1, 10))
                # Note: In a real implementation, you'd add the chart image here
        except ImportError:
            pass
        
        # Build PDF
        doc.build(story)
        
        print(f"Weekly report generated: {filepath}")
        return filepath
    
    def _calculate_summary_statistics(self, betting_data: List[Dict]) -> Dict:
        """Calculate summary statistics from betting data"""
        if not betting_data:
            return {
                'total_bets': 0,
                'winning_bets': 0,
                'losing_bets': 0,
                'total_stake': 0.0,
                'total_return': 0.0,
                'roi': 0.0,
                'win_rate': 0.0,
                'average_odds': 0.0,
                'total_edge': 0.0
            }
        
        df = pd.DataFrame(betting_data)
        
        total_bets = len(df)
        winning_bets = len(df[df['result'] == 'win'])
        losing_bets = len(df[df['result'] == 'loss'])
        
        total_stake = df['stake'].sum()
        total_return = df['return'].sum()
        
        roi = ((total_return - total_stake) / total_stake) if total_stake > 0 else 0.0
        win_rate = (winning_bets / total_bets) if total_bets > 0 else 0.0
        
        average_odds = df['odds'].mean()
        total_edge = df['edge'].sum()
        
        return {
            'total_bets': total_bets,
            'winning_bets': winning_bets,
            'losing_bets': losing_bets,
            'total_stake': total_stake,
            'total_return': total_return,
            'roi': roi,
            'win_rate': win_rate,
            'average_odds': average_odds,
            'total_edge': total_edge
        }
    
    def _calculate_market_statistics(self, betting_data: List[Dict]) -> Dict:
        """Calculate statistics by market type"""
        if not betting_data:
            return {}
        
        df = pd.DataFrame(betting_data)
        market_stats = {}
        
        for market in df['market'].unique():
            market_df = df[df['market'] == market]
            
            total_bets = len(market_df)
            winning_bets = len(market_df[market_df['result'] == 'win'])
            total_stake = market_df['stake'].sum()
            total_return = market_df['return'].sum()
            
            roi = ((total_return - total_stake) / total_stake) if total_stake > 0 else 0.0
            win_rate = (winning_bets / total_bets) if total_bets > 0 else 0.0
            
            market_stats[market] = {
                'total_bets': total_bets,
                'winning_bets': winning_bets,
                'win_rate': win_rate,
                'roi': roi,
                'total_stake': total_stake,
                'total_return': total_return
            }
        
        return market_stats
    
    def _create_summary_section(self, summary_stats: Dict) -> List:
        """Create summary statistics section"""
        elements = []
        
        # Add heading
        elements.append(Paragraph("Summary Statistics", self.styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Create summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Bets', str(summary_stats['total_bets'])],
            ['Winning Bets', str(summary_stats['winning_bets'])],
            ['Losing Bets', str(summary_stats['losing_bets'])],
            ['Win Rate', f"{summary_stats['win_rate']:.1%}"],
            ['Total Stake', f"£{summary_stats['total_stake']:.2f}"],
            ['Total Return', f"£{summary_stats['total_return']:.2f}"],
            ['ROI', f"{summary_stats['roi']:.1%}"],
            ['Average Odds', f"{summary_stats['average_odds']:.2f}"],
            ['Total Edge', f"{summary_stats['total_edge']:.1%}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_market_breakdown_section(self, market_stats: Dict) -> List:
        """Create market breakdown section"""
        elements = []
        
        # Add heading
        elements.append(Paragraph("Market Breakdown", self.styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        if not market_stats:
            elements.append(Paragraph("No market data available", self.styles['Normal']))
            return elements
        
        # Create market breakdown table
        market_data = [['Market', 'Bets', 'Win Rate', 'ROI', 'Stake', 'Return']]
        
        for market, stats in market_stats.items():
            market_name = market.replace('_', ' ').title()
            market_data.append([
                market_name,
                str(stats['total_bets']),
                f"{stats['win_rate']:.1%}",
                f"{stats['roi']:.1%}",
                f"£{stats['total_stake']:.2f}",
                f"£{stats['total_return']:.2f}"
            ])
        
        market_table = Table(market_data, colWidths=[1.5*inch, 0.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
        market_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        
        elements.append(market_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_performance_chart(self, betting_data: List[Dict], 
                                start_date: datetime, end_date: datetime) -> Optional[str]:
        """Create performance chart (placeholder for matplotlib integration)"""
        try:
            import matplotlib.pyplot as plt
            
            if not betting_data:
                return None
            
            df = pd.DataFrame(betting_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            
            if df.empty:
                return None
            
            # Create cumulative ROI chart
            df = df.sort_values('date')
            df['cumulative_roi'] = df['roi'].cumsum()
            
            plt.figure(figsize=(10, 6))
            plt.plot(df['date'], df['cumulative_roi'], marker='o')
            plt.title('Cumulative ROI Over Time')
            plt.xlabel('Date')
            plt.ylabel('Cumulative ROI (%)')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            chart_path = os.path.join(self.output_dir, 'performance_chart.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except ImportError:
            print("Matplotlib not available, skipping chart generation")
            return None
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None
