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
            ['Win Rate', f"{summary_stats['win_rate']:.1f}%"],
            ['Total Stake', f"£{summary_stats['total_stake']:.2f}"],
            ['Total Return', f"£{summary_stats['total_return']:.2f}"],
            ['ROI', f"{summary_stats['roi']:.1f}%"],
            ['Average Odds', f"{summary_stats['average_odds']:.2f}"],
            ['Total Edge', f"{summary_stats['total_edge']:.1f}%"]
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
                f"{stats['win_rate']:.1f}%",
                f"{stats['roi']:.1f}%",
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
    
    async def generate_betting_performance_report(self) -> Dict:
        """
        Generate a comprehensive betting performance report using real database data
        
        Returns:
            Dictionary with report data and success status
        """
        try:
            # Import ROI tracker to get real data
            from betting.roi_tracker import ROITracker
            
            # Initialize ROI tracker
            roi_tracker = ROITracker()
            
            # Get real-time performance data
            overall_performance = roi_tracker.get_overall_performance()
            market_performance = roi_tracker.get_market_performance()
            league_performance = roi_tracker.get_league_performance()
            
            # Calculate current date for period
            from datetime import datetime
            current_date = datetime.now()
            
            # Generate a comprehensive PDF report
            filename = f"betting_performance_report_{current_date.strftime('%Y%m%d_%H%M%S')}.pdf"
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
            
            title = Paragraph("FIXORA PRO - Betting Performance Report", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add timestamp
            timestamp_style = ParagraphStyle(
                'Timestamp',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=1,
                textColor=colors.grey
            )
            
            timestamp = f"Report Generated: {current_date.strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(timestamp, timestamp_style))
            story.append(Spacer(1, 30))
            
            # Add overall performance summary
            story.append(Paragraph("Overall Performance Summary", self.styles['Heading2']))
            story.append(Spacer(1, 10))
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Bets', str(overall_performance.get('total_bets', 0))],
                ['Winning Bets', str(overall_performance.get('winning_bets', 0))],
                ['Win Rate', f"{overall_performance.get('win_rate', 0):.1f}%"],
                ['Total Stake', f"{overall_performance.get('total_stake', 0):.2f} units"],
                ['Total Return', f"{overall_performance.get('total_return', 0):.2f} units"],
                ['Total Profit/Loss', f"{overall_performance.get('total_profit_loss', 0):.2f} units"],
                ['Overall ROI', f"{overall_performance.get('overall_roi', 0):.1f}%"]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
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
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Add market performance breakdown
            if market_performance:
                story.append(Paragraph("Market Performance Breakdown", self.styles['Heading2']))
                story.append(Spacer(1, 10))
                
                market_data = [['Market', 'Bets', 'Win Rate', 'ROI', 'Stake', 'Return']]
                for market_stats in market_performance:
                    market_name = market_stats.get('market_type', 'Unknown').replace('_', ' ').title()
                    market_data.append([
                        market_name,
                        str(market_stats.get('total_bets', 0)),
                        f"{market_stats.get('overall_roi', 0):.1f}%",
                        f"{market_stats.get('overall_roi', 0):.1f}%",
                        f"{market_stats.get('total_stake', 0):.2f}",
                        f"{market_stats.get('total_return', 0):.2f}"
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
                
                story.append(market_table)
                story.append(Spacer(1, 20))
            
            # Add league performance
            if league_performance:
                story.append(Paragraph("League Performance", self.styles['Heading2']))
                story.append(Spacer(1, 10))
                
                league_data = [['League', 'Bets', 'Win Rate', 'ROI', 'Stake', 'Return']]
                for league in league_performance:
                    league_data.append([
                        league.get('league_name', 'Unknown'),
                        str(league.get('total_bets', 0)),
                        f"{league.get('overall_roi', 0):.1f}%",
                        f"{league.get('overall_roi', 0):.1f}%",
                        f"{league.get('total_stake', 0):.2f}",
                        f"{league.get('total_return', 0):.2f}"
                    ])
                
                league_table = Table(league_data, colWidths=[2*inch, 0.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
                league_table.setStyle(TableStyle([
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
                
                story.append(league_table)
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            
            # Prepare report data with real values
            report_data = {
                'success': True,
                'total_bets': overall_performance.get('total_bets', 0),
                'winning_bets': overall_performance.get('winning_bets', 0),
                'losing_bets': overall_performance.get('total_bets', 0) - overall_performance.get('winning_bets', 0),
                'overall_roi': overall_performance.get('overall_roi', 0),
                'total_pnl': overall_performance.get('total_profit_loss', 0),
                'file_path': filepath,
                'period': f"All time (as of {current_date.strftime('%B %d, %Y')})"
            }
            
            print(f"Betting performance report generated: {filepath}")
            return report_data
            
        except Exception as e:
            print(f"Error generating betting performance report: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_weekly_roi_report(self, betting_data: List[Dict], 
                                       start_date: datetime, end_date: datetime) -> str:
        """
        Generate weekly ROI performance report using real database data
        
        Args:
            betting_data: List of betting records for the week (can be empty, will fetch from DB)
            start_date: Start of the week
            end_date: End of the week
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Import ROI tracker to get real data if betting_data is empty
            from betting.roi_tracker import ROITracker
            
            # Initialize ROI tracker
            roi_tracker = ROITracker()
            
            # Get real-time weekly performance data
            weekly_performance = roi_tracker.get_weekly_performance(7)  # Last 7 days
            overall_performance = roi_tracker.get_overall_performance()
            
            # Create filename for weekly report
            filename = f"weekly_roi_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
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
            
            title = Paragraph("FIXORA PRO - Weekly ROI Report", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add date range
            date_style = ParagraphStyle(
                'DateRange',
                parent=self.styles['Normal'],
                fontSize=16,
                alignment=1,
                textColor=colors.grey
            )
            
            date_range = f"Week: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
            story.append(Paragraph(date_range, date_style))
            story.append(Spacer(1, 20))
            
            # Add timestamp
            timestamp_style = ParagraphStyle(
                'Timestamp',
                parent=self.styles['Normal'],
                fontSize=12,
                alignment=1,
                textColor=colors.lightgrey
            )
            
            timestamp = f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            story.append(Paragraph(timestamp, timestamp_style))
            story.append(Spacer(1, 30))
            
            # Add weekly performance summary
            story.append(Paragraph("Weekly Performance Summary", self.styles['Heading2']))
            story.append(Spacer(1, 10))
            
            if weekly_performance:
                weekly_data = [['Market', 'Bets', 'Win Rate', 'ROI', 'Stake', 'Return', 'P&L']]
                total_weekly_bets = 0
                total_weekly_stake = 0
                total_weekly_return = 0
                total_weekly_pnl = 0
                
                for market, stats in weekly_performance.items():
                    weekly_data.append([
                        market.replace('_', ' ').title(),
                        str(stats.get('total_bets', 0)),
                        f"{stats.get('win_rate', 0):.1f}%",
                        f"{stats.get('roi', 0):.1f}%",
                        f"{stats.get('total_stake', 0):.2f}",
                        f"{stats.get('total_return', 0):.2f}",
                        f"{stats.get('total_profit_loss', 0):.2f}"
                    ])
                    
                    total_weekly_bets += stats.get('total_bets', 0)
                    total_weekly_stake += stats.get('total_stake', 0)
                    total_weekly_return += stats.get('total_return', 0)
                    total_weekly_pnl += stats.get('total_profit_loss', 0)
                
                # Add weekly totals row
                weekly_roi = (total_weekly_pnl / total_weekly_stake) * 100 if total_weekly_stake > 0 else 0
                weekly_data.append([
                    'TOTAL',
                    str(total_weekly_bets),
                    f"{(total_weekly_bets - (total_weekly_bets - sum(1 for s in weekly_performance.values() if s.get('winning_bets', 0) > 0)) / total_weekly_bets * 100):.1f}%" if total_weekly_bets > 0 else "0.0%",
                    f"{weekly_roi:.1f}%",
                    f"{total_weekly_stake:.2f}",
                    f"{total_weekly_return:.2f}",
                    f"{total_weekly_pnl:.2f}"
                ])
                
                weekly_table = Table(weekly_data, colWidths=[1.5*inch, 0.5*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.8*inch])
                weekly_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
                ]))
                
                story.append(weekly_table)
            else:
                story.append(Paragraph("No betting activity in the last 7 days", self.styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Add overall performance context
            story.append(Paragraph("Overall Performance Context", self.styles['Heading2']))
            story.append(Spacer(1, 10))
            
            context_data = [
                ['Metric', 'All Time', 'This Week'],
                ['Total Bets', str(overall_performance.get('total_bets', 0)), str(total_weekly_bets if weekly_performance else 0)],
                ['Win Rate', f"{overall_performance.get('win_rate', 0):.1f}%", f"{weekly_performance.get('match_result', {}).get('win_rate', 0):.1f}%" if weekly_performance and 'match_result' in weekly_performance else "0.0%"],
                ['Overall ROI', f"{overall_performance.get('overall_roi', 0):.1f}%", f"{weekly_roi:.1f}%" if weekly_performance else "0.0%"],
                ['Total Stake', f"{overall_performance.get('total_stake', 0):.2f}", f"{total_weekly_stake:.2f}" if weekly_performance else "0.00"],
                ['Total P&L', f"{overall_performance.get('total_profit_loss', 0):.2f}", f"{total_weekly_pnl:.2f}" if weekly_performance else "0.00"]
            ]
            
            context_table = Table(context_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            context_table.setStyle(TableStyle([
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
            
            story.append(context_table)
            
            # Build PDF
            doc.build(story)
            
            print(f"Weekly ROI report generated: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error generating weekly ROI report: {e}")
            return None
