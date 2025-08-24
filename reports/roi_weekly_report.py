#!/usr/bin/env python3
"""
Weekly ROI Report Generator for FIXORA PRO
Generates comprehensive PDF reports with ROI tracking by market
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import config

logger = logging.getLogger(__name__)

class ROIWeeklyReportGenerator:
    """
    Generates weekly ROI reports in PDF format with charts and market breakdowns
    """
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or config.REPORT_OUTPUT_DIR
        self.styles = getSampleStyleSheet()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkgreen
        )
        
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkred
        )
    
    def generate_weekly_roi_report(self, roi_data: Dict, start_date: datetime, end_date: datetime) -> str:
        """
        Generate comprehensive weekly ROI report
        
        Args:
            roi_data: Dictionary containing ROI tracking data
            start_date: Start of reporting period
            end_date: End of reporting period
            
        Returns:
            Path to generated PDF file
        """
        try:
            # Create filename
            filename = f"weekly_roi_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            story = []
            
            # Add title page
            story.extend(self._create_title_page(start_date, end_date))
            story.append(PageBreak())
            
            # Add executive summary
            story.extend(self._create_executive_summary(roi_data))
            story.append(PageBreak())
            
            # Add market performance breakdown
            story.extend(self._create_market_breakdown(roi_data))
            story.append(PageBreak())
            
            # Add league performance
            story.extend(self._create_league_performance(roi_data))
            story.append(PageBreak())
            
            # Add detailed bet analysis
            story.extend(self._create_detailed_analysis(roi_data))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Weekly ROI report generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate weekly ROI report: {e}")
            return None
    
    def _create_title_page(self, start_date: datetime, end_date: datetime) -> List:
        """Create the title page"""
        story = []
        
        # Main title
        title = Paragraph("FIXORA PRO - Weekly ROI Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 40))
        
        # Date range
        date_style = ParagraphStyle(
            'DateRange',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=1,
            textColor=colors.grey
        )
        
        date_range = f"Period: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
        story.append(Paragraph(date_range, date_style))
        story.append(Spacer(1, 30))
        
        # Generated timestamp
        timestamp_style = ParagraphStyle(
            'Timestamp',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.lightgrey
        )
        
        timestamp = f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(timestamp, timestamp_style))
        
        return story
    
    def _create_executive_summary(self, roi_data: Dict) -> List:
        """Create executive summary section"""
        story = []
        
        # Section title
        story.append(Paragraph("Executive Summary", self.subtitle_style))
        story.append(Spacer(1, 20))
        
        # Overall performance
        overall = roi_data.get('overall_performance', {})
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Bets', f"{overall.get('total_bets', 0)}"],
            ['Winning Bets', f"{overall.get('winning_bets', 0)}"],
            ['Win Rate', f"{overall.get('win_rate', 0):.1f}%"],
            ['Total Stake', f"${overall.get('total_stake', 0):.2f}"],
            ['Total Return', f"${overall.get('total_return', 0):.2f}"],
            ['Total Profit/Loss', f"${overall.get('total_profit_loss', 0):.2f}"],
            ['Overall ROI', f"{overall.get('overall_roi', 0):.2f}%"]
        ]
        
        # Create summary table
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
        story.append(Spacer(1, 30))
        
        # Key insights
        story.append(Paragraph("Key Insights", self.header_style))
        story.append(Spacer(1, 10))
        
        insights = []
        roi = overall.get('overall_roi', 0)
        win_rate = overall.get('win_rate', 0)
        
        if roi > 0:
            insights.append(f"Positive ROI of {roi:.2f}% indicates profitable betting strategy")
        else:
            insights.append(f"Negative ROI of {roi:.2f}% suggests strategy needs review")
        
        if win_rate > 50:
            insights.append(f"Strong win rate of {win_rate:.1f}% shows good selection criteria")
        else:
            insights.append(f"Win rate of {win_rate:.1f}% below 50% - consider adjusting selection criteria")
        
        for insight in insights:
            story.append(Paragraph(f"• {insight}", self.styles['Normal']))
            story.append(Spacer(1, 5))
        
        return story
    
    def _create_market_breakdown(self, roi_data: Dict) -> List:
        """Create market performance breakdown section"""
        story = []
        
        # Section title
        story.append(Paragraph("Market Performance Breakdown", self.subtitle_style))
        story.append(Spacer(1, 20))
        
        # Market performance data
        market_performance = roi_data.get('market_performance', [])
        
        if market_performance:
            # Create market breakdown table
            market_headers = ['Market', 'Bets', 'Wins', 'Win Rate', 'Stake', 'Return', 'P/L', 'ROI']
            market_data = [market_headers]
            
            for market in market_performance:
                market_data.append([
                    market.get('market_type', 'Unknown'),
                    str(market.get('total_bets', 0)),
                    str(market.get('winning_bets', 0)),
                    f"{market.get('win_rate', 0):.1f}%",
                    f"${market.get('total_stake', 0):.2f}",
                    f"${market.get('total_return', 0):.2f}",
                    f"${market.get('total_profit_loss', 0):.2f}",
                    f"{market.get('roi', 0):.2f}%"
                ])
            
            market_table = Table(market_data, colWidths=[1.2*inch, 0.5*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch])
            market_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(market_table)
            story.append(Spacer(1, 20))
            
            # Market insights
            story.append(Paragraph("Market Insights", self.header_style))
            story.append(Spacer(1, 10))
            
            best_market = max(market_performance, key=lambda x: x.get('roi', 0))
            worst_market = min(market_performance, key=lambda x: x.get('roi', 0))
            
            story.append(Paragraph(f"Best Performing Market: {best_market.get('market_type', 'Unknown')} with {best_market.get('roi', 0):.2f}% ROI", self.styles['Normal']))
            story.append(Paragraph(f"Worst Performing Market: {worst_market.get('market_type', 'Unknown')} with {worst_market.get('roi', 0):.2f}% ROI", self.styles['Normal']))
            
        else:
            story.append(Paragraph("No market performance data available for this period", self.styles['Normal']))
        
        return story
    
    def _create_league_performance(self, roi_data: Dict) -> List:
        """Create league performance section"""
        story = []
        
        # Section title
        story.append(Paragraph("League Performance Analysis", self.subtitle_style))
        story.append(Spacer(1, 20))
        
        # League performance data
        league_performance = roi_data.get('league_performance', [])
        
        if league_performance:
            # Create league breakdown table
            league_headers = ['League', 'Bets', 'Wins', 'Win Rate', 'Stake', 'Return', 'P/L', 'ROI']
            league_data = [league_headers]
            
            for league in league_performance:
                league_data.append([
                    league.get('league_name', 'Unknown')[:25],  # Truncate long names
                    str(league.get('total_bets', 0)),
                    str(league.get('winning_bets', 0)),
                    f"{league.get('win_rate', 0):.1f}%",
                    f"${league.get('total_stake', 0):.2f}",
                    f"${league.get('total_return', 0):.2f}",
                    f"${league.get('total_profit_loss', 0):.2f}",
                    f"{league.get('roi', 0):.2f}%"
                ])
            
            league_table = Table(league_data, colWidths=[1.5*inch, 0.5*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch])
            league_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(league_table)
            story.append(Spacer(1, 20))
            
            # League insights
            story.append(Paragraph("League Insights", self.header_style))
            story.append(Spacer(1, 10))
            
            best_league = max(league_performance, key=lambda x: x.get('roi', 0))
            worst_league = min(league_performance, key=lambda x: x.get('roi', 0))
            
            story.append(Paragraph(f"Best Performing League: {best_league.get('league_name', 'Unknown')} with {best_league.get('roi', 0):.2f}% ROI", self.styles['Normal']))
            story.append(Paragraph(f"Worst Performing League: {worst_league.get('league_name', 'Unknown')} with {worst_league.get('roi', 0):.2f}% ROI", self.styles['Normal']))
            
        else:
            story.append(Paragraph("No league performance data available for this period", self.styles['Normal']))
        
        return story
    
    def _create_detailed_analysis(self, roi_data: Dict) -> List:
        """Create detailed bet analysis section"""
        story = []
        
        # Section title
        story.append(Paragraph("Detailed Bet Analysis", self.subtitle_style))
        story.append(Spacer(1, 20))
        
        # Weekly performance
        weekly_performance = roi_data.get('weekly_performance', {})
        
        if weekly_performance:
            story.append(Paragraph("Weekly Performance by Market", self.header_style))
            story.append(Spacer(1, 10))
            
            # Create weekly breakdown table
            weekly_headers = ['Market', 'Bets', 'Wins', 'Win Rate', 'Stake', 'Return', 'P/L', 'ROI']
            weekly_data = [weekly_headers]
            
            for market_type, data in weekly_performance.items():
                weekly_data.append([
                    market_type,
                    str(data.get('total_bets', 0)),
                    str(data.get('winning_bets', 0)),
                    f"{data.get('win_rate', 0):.1f}%",
                    f"${data.get('total_stake', 0):.2f}",
                    f"${data.get('total_return', 0):.2f}",
                    f"${data.get('total_profit_loss', 0):.2f}",
                    f"{data.get('roi', 0):.2f}%"
                ])
            
            weekly_table = Table(weekly_data, colWidths=[1.2*inch, 0.5*inch, 0.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.6*inch])
            weekly_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(weekly_table)
            story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Recommendations", self.header_style))
        story.append(Spacer(1, 10))
        
        recommendations = [
            "Continue betting on markets with positive ROI",
            "Review and adjust strategy for markets with negative ROI",
            "Focus on leagues showing consistent positive performance",
            "Consider reducing stakes on underperforming markets",
            "Monitor win rates and adjust selection criteria if needed"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['Normal']))
            story.append(Spacer(1, 5))
        
        return story
    
    def create_performance_chart(self, roi_data: Dict, start_date: datetime, end_date: datetime) -> Optional[str]:
        """Create performance chart and save as image"""
        try:
            # Create matplotlib figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Market performance chart
            market_performance = roi_data.get('market_performance', [])
            if market_performance:
                markets = [m.get('market_type', 'Unknown') for m in market_performance]
                rois = [m.get('overall_roi', 0) for m in market_performance]
                
                bars1 = ax1.bar(markets, rois, color=['green' if r > 0 else 'red' for r in rois])
                ax1.set_title('ROI by Market Type')
                ax1.set_ylabel('ROI (%)')
                ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                
                # Add value labels on bars
                for bar, roi in zip(bars1, rois):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                            f'{roi:.1f}%', ha='center', va='bottom' if roi > 0 else 'top')
            
            # League performance chart
            league_performance = roi_data.get('league_performance', [])
            if league_performance:
                # Take top 10 leagues by ROI
                top_leagues = sorted(league_performance, key=lambda x: x.get('overall_roi', 0), reverse=True)[:10]
                leagues = [l.get('league_name', 'Unknown')[:20] for l in top_leagues]
                rois = [l.get('overall_roi', 0) for l in top_leagues]
                
                bars2 = ax2.barh(leagues, rois, color=['green' if r > 0 else 'red' for r in rois])
                ax2.set_title('Top 10 Leagues by ROI')
                ax2.set_xlabel('ROI (%)')
                ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)
            
            plt.tight_layout()
            
            # Save chart
            chart_filename = f"performance_chart_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.png"
            chart_path = os.path.join(self.output_dir, chart_filename)
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            logger.error(f"Failed to create performance chart: {e}")
            return None
