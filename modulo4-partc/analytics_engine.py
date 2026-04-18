"""
Módulo 4C - Analytics Dashboard
Engine para obtener métricas de APIs de redes sociales
"""

import os
import requests
from datetime import datetime
from typing import Dict, Optional, Any
from dotenv import load_dotenv
from db import insert_metrics

load_dotenv()


class AnalyticsEngine:
    def __init__(self):
        self.instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.twitter_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.linkedin_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.tiktok_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        self.youtube_key = os.getenv('YOUTUBE_API_KEY')
        
        self.instagram_base_url = 'https://graph.instagram.com'
        self.twitter_base_url = 'https://api.twitter.com/2'
        self.linkedin_base_url = 'https://api.linkedin.com/v2'
        self.tiktok_base_url = 'https://open-api.tiktok.com'
        self.youtube_base_url = 'https://www.googleapis.com/youtube/v3'
    
    def get_instagram_metrics(self, post_id: str) -> Optional[Dict[str, Any]]:
        if not self.instagram_token:
            print("⚠️ Instagram token no configurado")
            return None
        
        try:
            url = f"{self.instagram_base_url}/{post_id}/insights"
            params = {
                'metric': 'impressions,reach,likes,comments,shares,saved',
                'access_token': self.instagram_token
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            metrics = {
                'vistas': 0,
                'likes': 0,
                'comentarios': 0,
                'shares': 0,
                'reach': 0,
                'impressions': 0,
                'saves': 0,
                'engagement_rate': 0.0
            }
            # TODO: Parsear data['data'] y extraer valores reales
            return metrics
        except requests.exceptions.RequestException as e:
            print(f"❌ Error obteniendo métricas de Instagram: {e}")
            return None
    
    def get_twitter_metrics(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        if not self.twitter_token:
            print("⚠️ Twitter token no configurado")
            return None
        
        try:
            url = f"{self.twitter_base_url}/tweets/{tweet_id}"
            headers = {'Authorization': f'Bearer {self.twitter_token}'}
            params = {'tweet.fields': 'public_metrics,created_at'}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            public_metrics = data.get('data', {}).get('public_metrics', {})
            
            metrics = {
                'vistas': public_metrics.get('impression_count', 0),
                'likes': public_metrics.get('like_count', 0),
                'comentarios': public_metrics.get('reply_count', 0),
                'shares': public_metrics.get('retweet_count', 0),
                'reach': public_metrics.get('impression_count', 0),
                'impressions': public_metrics.get('impression_count', 0),
                'engagement_rate': 0.0
            }
            
            total_engagement = metrics['likes'] + metrics['comentarios'] + metrics['shares']
            if metrics['impressions'] > 0:
                metrics['engagement_rate'] = round((total_engagement / metrics['impressions']) * 100, 2)
            
            return metrics
        except requests.exceptions.RequestException as e:
            print(f"❌ Error obteniendo métricas de Twitter: {e}")
            return None
    
    def get_youtube_metrics(self, video_id: str) -> Optional[Dict[str, Any]]:
        if not self.youtube_key:
            print("⚠️ YouTube API key no configurada")
            return None
        
        try:
            url = f"{self.youtube_base_url}/videos"
            params = {
                'part': 'statistics',
                'id': video_id,
                'key': self.youtube_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('items'):
                stats = data['items'][0].get('statistics', {})
                metrics = {
                    'vistas': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comentarios': int(stats.get('commentCount', 0)),
                    'shares': 0,
                    'reach': int(stats.get('viewCount', 0)),
                    'impressions': int(stats.get('viewCount', 0)),
                    'engagement_rate': 0.0
                }
                
                total_engagement = metrics['likes'] + metrics['comentarios']
                if metrics['vistas'] > 0:
                    metrics['engagement_rate'] = round((total_engagement / metrics['vistas']) * 100, 2)
                
                return metrics
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error obteniendo métricas de YouTube: {e}")
            return None
    
    def fetch_and_store_metrics(self, post_id: str, platform: str) -> bool:
        methods = {
            'instagram': self.get_instagram_metrics,
            'twitter': self.get_twitter_metrics,
            'youtube': self.get_youtube_metrics
        }
        
        if platform not in methods:
            print(f"❌ Plataforma no soportada: {platform}")
            return False
        
        metrics = methods[platform](post_id)
        if not metrics:
            return False
        
        try:
            insert_metrics(post_id, platform, metrics)
            print(f"✅ Métricas guardadas: {platform} - {post_id}")
            return True
        except Exception as e:
            print(f"❌ Error guardando métricas: {e}")
            return False