"""
Módulo 4C - Analytics Dashboard
Generador de visualizaciones y gráficos con matplotlib
"""

import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd


class Visualizations:
    def __init__(self, output_dir: str = './charts'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = {
            'instagram': '#E1306C',
            'twitter': '#1DA1F2',
            'linkedin': '#0077B5',
            'tiktok': '#000000',
            'youtube': '#FF0000'
        }
    
    def plot_engagement_over_time(self, data: List[Dict[str, Any]], 
                                  platform: str, filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'engagement_{platform}_{timestamp}.png'
        
        filepath = os.path.join(self.output_dir, filename)
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['timestamp'], df['engagement_rate'], marker='o', 
               linewidth=2, markersize=6, color=self.colors.get(platform, '#1a73e8'))
        
        ax.set_title(f'Evolución de Engagement - {platform.capitalize()}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Engagement Rate (%)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráfico generado: {filepath}")
        return filepath
    
    def plot_platform_comparison(self, data: List[Dict[str, Any]], 
                                metric: str = 'total_vistas', filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'comparison_{metric}_{timestamp}.png'
        
        filepath = os.path.join(self.output_dir, filename)
        
        platforms = [row['plataforma'] for row in data]
        values = [row[metric] for row in data]
        colors = [self.colors.get(p, '#1a73e8') for p in platforms]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(platforms, values, color=colors, alpha=0.8, edgecolor='black')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height, f'{int(height):,}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        metric_name = metric.replace('_', ' ').replace('total', '').strip().capitalize()
        ax.set_title(f'Comparación de {metric_name} por Plataforma',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Plataforma', fontsize=12)
        ax.set_ylabel(metric_name, fontsize=12)
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráfico generado: {filepath}")
        return filepath
    
    def plot_distribution(self, data: List[Dict[str, Any]], 
                         metric: str = 'total_vistas', filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'distribution_{metric}_{timestamp}.png'
        
        filepath = os.path.join(self.output_dir, filename)
        
        platforms = [row['plataforma'] for row in data]
        values = [row[metric] for row in data]
        colors = [self.colors.get(p, '#1a73e8') for p in platforms]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(values, labels=platforms, colors=colors,
                                          autopct='%1.1f%%', startangle=90,
                                          explode=[0.05] * len(platforms))
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        metric_name = metric.replace('_', ' ').replace('total', '').strip().capitalize()
        ax.set_title(f'Distribución de {metric_name}', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Gráfico generado: {filepath}")
        return filepath
        