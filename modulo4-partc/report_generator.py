"""
Módulo 4C - Analytics Dashboard
Generador de reportes en PDF, CSV y Excel
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from db import db


class ReportGenerator:
    def __init__(self, output_dir: str = './reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_csv_report(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_{timestamp}.csv'
        
        filepath = os.path.join(self.output_dir, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        print(f"✅ CSV generado: {filepath}")
        return filepath
    
    def generate_excel_report(self, data: Dict[str, List[Dict[str, Any]]], filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_{timestamp}.xlsx'
        
        filepath = os.path.join(self.output_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, sheet_data in data.items():
                df = pd.DataFrame(sheet_data)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        print(f"✅ Excel generado: {filepath}")
        return filepath
    
    def generate_pdf_report(self, title: str, data: List[Dict[str, Any]], 
                          summary: Dict[str, Any] = None, filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'reporte_{timestamp}.pdf'
        
        filepath = os.path.join(self.output_dir, filename)
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a73e8'),
            spaceAfter=30
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        date_text = f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        if summary:
            story.append(Paragraph("Resumen Ejecutivo", styles['Heading2']))
            story.append(Spacer(1, 12))
            for key, value in summary.items():
                summary_text = f"<b>{key}:</b> {value}"
                story.append(Paragraph(summary_text, styles['Normal']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 20))
        
        if data:
            story.append(Paragraph("Datos Detallados", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            df = pd.DataFrame(data)
            table_data = [df.columns.tolist()] + df.values.tolist()
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        doc.build(story)
        print(f"✅ PDF generado: {filepath}")
        return filepath
    
    def generate_platform_comparison_report(self, start_date: str, end_date: str, 
                                          format: str = 'pdf') -> str:
        query = """
            SELECT plataforma, COUNT(*) as total_posts,
                   SUM(vistas) as total_vistas, SUM(likes) as total_likes
            FROM metricas_posts
            WHERE timestamp BETWEEN %s AND %s
            GROUP BY plataforma
            ORDER BY total_vistas DESC
        """ if db.use_postgresql else """
            SELECT plataforma, COUNT(*) as total_posts,
                   SUM(vistas) as total_vistas, SUM(likes) as total_likes
            FROM metricas_posts
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY plataforma
            ORDER BY total_vistas DESC
        """
        
        data = db.execute_query(query, (start_date, end_date))
        
        if not data:
            print("⚠️ No hay datos para el período seleccionado")
            return None
        
        if format == 'pdf':
            total_vistas = sum(row['total_vistas'] or 0 for row in data)
            summary = {
                'Período': f"{start_date} a {end_date}",
                'Total Vistas': f"{total_vistas:,}"
            }
            return self.generate_pdf_report(
                title="Reporte Comparativo entre Plataformas",
                data=data,
                summary=summary
            )
        elif format == 'csv':
            return self.generate_csv_report(data)
        elif format == 'excel':
            return self.generate_excel_report({'Comparativa': data})
        
        return None