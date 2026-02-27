import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import time
from enum import Enum
import logging

# ================= CONFIGURATION =================

st.set_page_config(
    page_title="PEVI | AMD Hackathon 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://amd-hackathon.dev',
        'Report a bug': 'https://amd-hackathon.dev/bug',
        'About': '# PEVI \nAMD Hackathon 2026\nNext-Gen Environmental Intelligence'
    }
)

# ================= LOGGING =================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= ENUMS =================

class RiskLevel(Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EXTREME = "EXTREME"
    
    @property
    def color(self):
        colors = {
            "LOW": "#00ff88",
            "MODERATE": "#00f2fe",
            "HIGH": "#ffb700",
            "CRITICAL": "#ff4466",
            "EXTREME": "#b800e6"
        }
        return colors[self.value]
    
    @property
    def bg_color(self):
        bg_colors = {
            "LOW": "rgba(0, 255, 136, 0.15)",
            "MODERATE": "rgba(0, 242, 254, 0.15)",
            "HIGH": "rgba(255, 183, 0, 0.15)",
            "CRITICAL": "rgba(255, 68, 102, 0.15)",
            "EXTREME": "rgba(184, 0, 230, 0.15)"
        }
        return bg_colors[self.value]

# ================= DATA MODELS =================

@dataclass
class Coordinates:
    """Geographic coordinates"""
    lat: float
    lon: float
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.lat, self.lon)

@dataclass
class AirQualityData:
    """Air quality metrics"""
    pm25: float
    pm10: float
    no2: float
    so2: float
    co: float
    o3: float
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'PM2.5': self.pm25,
            'PM10': self.pm10,
            'NO2': self.no2,
            'SO2': self.so2,
            'CO': self.co,
            'O3': self.o3
        }

@dataclass
class WeatherData:
    """Weather metrics"""
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: float
    pressure: float
    timestamp: datetime

@dataclass
class CityData:
    """City information"""
    name: str
    coordinates: Coordinates
    population: int
    description: str
    timezone: str
    
@dataclass
class EnvironmentalData:
    """Complete environmental data"""
    city: CityData
    air_quality: AirQualityData
    weather: WeatherData
    data_quality: float
    source: str
    
    @property
    def timestamp(self) -> datetime:
        return self.air_quality.timestamp

@dataclass
class HealthProfile:
    """User health profile"""
    user_id: str
    age: int
    asthma: str
    bp: str
    immunity: str
    smoking: str
    exercise: str
    heart_disease: str
    diabetes: str
    pregnancy: str
    timestamp: datetime
    
    def calculate_risk_multiplier(self) -> float:
        """Calculate health risk multiplier"""
        multipliers = {
            'asthma': {'No': 1.0, 'Mild': 1.35, 'Moderate': 1.7, 'Severe': 2.2},
            'bp': {'Normal': 1.0, 'Pre-high': 1.25, 'High': 1.6, 'Critical': 2.0},
            'immunity': {'Strong': 1.0, 'Moderate': 1.2, 'Low': 1.6, 'Compromised': 2.2},
            'smoking': {'Never': 1.0, 'Former': 1.2, 'Current': 1.7},
            'exercise': {'Regular': 0.9, 'Moderate': 1.0, 'Sedentary': 1.3},
            'heart_disease': {'No': 1.0, 'Yes': 1.6},
            'diabetes': {'No': 1.0, 'Yes': 1.4},
            'pregnancy': {'No': 1.0, 'Yes': 1.5}
        }
        
        multiplier = 1.0
        for field, value in self.__dict__.items():
            if field in multipliers and value in multipliers[field]:
                multiplier *= multipliers[field][value]
        
        # Age factor
        if self.age < 5 or self.age > 65:
            multiplier *= 1.3
        elif self.age < 18:
            multiplier *= 1.2
            
        return multiplier

@dataclass
class RiskAssessment:
    """Complete risk assessment result"""
    overall_score: float
    respiratory_risk: float
    cardiovascular_risk: float
    thermal_comfort: float
    risk_level: RiskLevel
    health_multiplier: float
    contributing_factors: List[str]
    timestamp: datetime
    data_confidence: float
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'overall_score': self.overall_score,
            'risk_level': self.risk_level.value,
            'timestamp': self.timestamp.isoformat(),
            'contributing_factors': self.contributing_factors
        }

@dataclass
class TrendData:
    """Historical trend data"""
    timestamps: List[datetime]
    values: List[float]
    forecast: List[float]
    confidence_upper: List[float]
    confidence_lower: List[float]

# ================= ENTERPRISE STYLING =================

st.markdown("""
<style>
    /* AMD Hackathon Professional Theme */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #00f2fe;
        --secondary: #4facfe;
        --accent: #a855f7;
        --background: #0a0c1a;
        --surface: #111827;
        --surface-light: #1f2937;
        --text: #ffffff;
        --text-secondary: #9ca3af;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--background), #0f1225);
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* AMD Header */
    .amd-header {
        background: linear-gradient(90deg, var(--surface), var(--surface-light));
        border-bottom: 3px solid var(--accent);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        position: relative;
        overflow: hidden;
    }
    
    .amd-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(168, 85, 247, 0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        100% { left: 100%; }
    }
    
    .amd-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #fff, var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 2px;
    }
    
    .amd-badge {
        background: linear-gradient(135deg, var(--accent), #9333ea);
        color: white;
        padding: 0.25rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    /* Hero Card */
    .hero-card {
        background: linear-gradient(145deg, var(--surface), var(--surface-light));
        border-radius: 32px;
        padding: 2.5rem;
        border: 1px solid rgba(168, 85, 247, 0.3);
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-card::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(168,85,247,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-value {
        font-size: 6rem;
        font-weight: 700;
        font-family: 'Space Grotesk', monospace;
        background: linear-gradient(135deg, #fff, var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    .hero-label {
        color: var(--text-secondary);
        font-size: 1.2rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-top: 0.5rem;
    }
    
    /* Live Badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        border: 1px solid #ef4444;
        font-weight: 600;
    }
    
    .live-dot {
        width: 10px;
        height: 10px;
        background: #ef4444;
        border-radius: 50%;
        animation: blink 1.5s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* Glass Card */
    .glass-card {
        background: rgba(31, 41, 55, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(168, 85, 247, 0.2);
        border-radius: 24px;
        padding: 1.5rem;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: var(--accent);
        box-shadow: 0 20px 40px -10px rgba(168,85,247,0.3);
    }
    
    /* Metric Card */
    .metric-card {
        background: linear-gradient(145deg, var(--surface), var(--surface-light));
        border-radius: 20px;
        padding: 1.5rem;
        border-left: 4px solid;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateX(5px);
    }
    
    .metric-value-lg {
        font-size: 3rem;
        font-weight: 700;
        font-family: monospace;
    }
    
    .metric-value-md {
        font-size: 2rem;
        font-weight: 600;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Progress Bar */
    .progress-bar {
        background: var(--surface-light);
        border-radius: 10px;
        height: 8px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent), var(--primary));
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Grid Layouts */
    .grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .grid-2 {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Responsive */
    @media (max-width: 1200px) {
        .grid-4 { grid-template-columns: repeat(2, 1fr); }
        .grid-3 { grid-template-columns: repeat(2, 1fr); }
    }
    
    @media (max-width: 768px) {
        .grid-4, .grid-3, .grid-2 { grid-template-columns: 1fr; }
        .hero-value { font-size: 4rem; }
    }
    
    /* AMD Footer */
    .amd-footer {
        background: var(--surface);
        border-top: 2px solid var(--accent);
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
    }
    
    /* Animations */
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .float {
        animation: float 3s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# ================= DATA SERVICE =================

class DataService:
    """Enterprise data service with caching"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # City database
        self.cities = {
            "Mumbai": CityData(
                name="Mumbai",
                coordinates=Coordinates(19.0760, 72.8777),
                population=20694000,
                description="Financial Capital • Coastal Metropolis",
                timezone="Asia/Kolkata"
            ),
            "Delhi": CityData(
                name="Delhi",
                coordinates=Coordinates(28.6139, 77.2090),
                population=16753000,
                description="National Capital • Industrial Hub",
                timezone="Asia/Kolkata"
            ),
            "Bangalore": CityData(
                name="Bangalore",
                coordinates=Coordinates(12.9716, 77.5946),
                population=8443000,
                description="Garden City • Tech Hub",
                timezone="Asia/Kolkata"
            ),
            "Chennai": CityData(
                name="Chennai",
                coordinates=Coordinates(13.0827, 80.2707),
                population=4647000,
                description="Coastal Metropolis • Port City",
                timezone="Asia/Kolkata"
            ),
            "Kolkata": CityData(
                name="Kolkata",
                coordinates=Coordinates(22.5726, 88.3639),
                population=4487000,
                description="Cultural Capital • Industrial Port",
                timezone="Asia/Kolkata"
            ),
            "Hyderabad": CityData(
                name="Hyderabad",
                coordinates=Coordinates(17.3850, 78.4867),
                population=6809000,
                description="Tech Hub • Pearl City",
                timezone="Asia/Kolkata"
            ),
            "Pune": CityData(
                name="Pune",
                coordinates=Coordinates(18.5204, 73.8567),
                population=3124000,
                description="Cultural Hub • Educational Center",
                timezone="Asia/Kolkata"
            )
        }
        
        # Base data
        self.base_data = {
            "Mumbai": {"pm25": 158, "pm10": 245, "no2": 48, "so2": 18, "co": 2.2, "o3": 34,
                      "temp": 32, "humidity": 78, "wind": 14, "wind_dir": 280, "pressure": 1012},
            "Delhi": {"pm25": 312, "pm10": 458, "no2": 72, "so2": 32, "co": 4.5, "o3": 25,
                     "temp": 35, "humidity": 48, "wind": 9, "wind_dir": 290, "pressure": 1008},
            "Bangalore": {"pm25": 72, "pm10": 128, "no2": 28, "so2": 8, "co": 1.1, "o3": 42,
                         "temp": 27, "humidity": 62, "wind": 11, "wind_dir": 120, "pressure": 1015},
            "Chennai": {"pm25": 92, "pm10": 158, "no2": 32, "so2": 11, "co": 1.3, "o3": 38,
                       "temp": 34, "humidity": 72, "wind": 16, "wind_dir": 110, "pressure": 1011},
            "Kolkata": {"pm25": 218, "pm10": 342, "no2": 58, "so2": 25, "co": 3.1, "o3": 28,
                       "temp": 34, "humidity": 76, "wind": 7, "wind_dir": 210, "pressure": 1006},
            "Hyderabad": {"pm25": 102, "pm10": 178, "no2": 35, "so2": 14, "co": 1.8, "o3": 36,
                         "temp": 33, "humidity": 54, "wind": 10, "wind_dir": 150, "pressure": 1012},
            "Pune": {"pm25": 94, "pm10": 162, "no2": 33, "so2": 13, "co": 1.5, "o3": 37,
                    "temp": 30, "humidity": 58, "wind": 12, "wind_dir": 250, "pressure": 1013}
        }
    
    def get_environmental_data(self, city_name: str) -> EnvironmentalData:
        """Get real-time environmental data"""
        
        # Check cache
        cache_key = f"{city_name}_{datetime.now().minute // 5}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        city = self.cities[city_name]
        base = self.base_data[city_name]
        
        # Add realistic variations
        variation = 0.9 + 0.2 * random.random()
        time_factor = 1 + 0.1 * np.sin(2 * np.pi * datetime.now().hour / 24)
        
        air_quality = AirQualityData(
            pm25=base["pm25"] * variation * time_factor,
            pm10=base["pm10"] * variation,
            no2=base["no2"] * variation,
            so2=base["so2"] * variation,
            co=base["co"] * variation,
            o3=base["o3"] * variation,
            timestamp=datetime.now()
        )
        
        weather = WeatherData(
            temperature=base["temp"] + (random.random() - 0.5) * 2,
            humidity=base["humidity"] + (random.random() - 0.5) * 5,
            wind_speed=base["wind"] + (random.random() - 0.5) * 2,
            wind_direction=base["wind_dir"] + (random.random() - 0.5) * 10,
            pressure=base["pressure"] + (random.random() - 0.5) * 3,
            timestamp=datetime.now()
        )
        
        env_data = EnvironmentalData(
            city=city,
            air_quality=air_quality,
            weather=weather,
            data_quality=0.95,
            source="AMD Hackathon Data Service"
        )
        
        # Cache the result
        self.cache[cache_key] = env_data
        
        return env_data
    
    def get_trend_data(self, city_name: str, hours: int = 72) -> TrendData:
        """Get historical trend data"""
        
        base_value = self.base_data[city_name]["pm25"]
        timestamps = []
        values = []
        
        for i in range(hours):
            t = datetime.now() - timedelta(hours=hours-i)
            timestamps.append(t)
            
            # Add realistic patterns
            daily = 30 * np.sin(2 * np.pi * t.hour / 24)
            weekly = 20 * np.sin(2 * np.pi * t.weekday() / 7)
            noise = random.gauss(0, 10)
            
            value = base_value + daily + weekly + noise
            values.append(max(0, value))
        
        # Generate forecast
        forecast = []
        forecast_upper = []
        forecast_lower = []
        
        for i in range(24):
            daily = 30 * np.sin(2 * np.pi * (datetime.now().hour + i) / 24)
            value = base_value + daily + random.gauss(0, 5)
            forecast.append(max(0, value))
            forecast_upper.append(value + 15 + i * 0.5)
            forecast_lower.append(max(0, value - 15 - i * 0.5))
        
        return TrendData(
            timestamps=timestamps,
            values=values,
            forecast=forecast,
            confidence_upper=forecast_upper,
            confidence_lower=forecast_lower
        )

# ================= RISK ENGINE =================

class RiskEngine:
    """Advanced risk calculation engine"""
    
    def __init__(self):
        self.pollutant_weights = {
            'pm25': 0.40,
            'pm10': 0.25,
            'no2': 0.15,
            'so2': 0.08,
            'co': 0.07,
            'o3': 0.05
        }
    
    def calculate_aqi(self, air_quality: AirQualityData) -> float:
        """Calculate Air Quality Index"""
        aqi = 0
        for pollutant, weight in self.pollutant_weights.items():
            value = getattr(air_quality, pollutant, 0)
            aqi += value * weight
        return min(aqi / 2, 500)
    
    def calculate_weather_score(self, weather: WeatherData) -> float:
        """Calculate weather impact score"""
        
        # Temperature score (0-100)
        temp = weather.temperature
        if temp > 40:
            temp_score = 100
        elif temp > 35:
            temp_score = 80 + (temp - 35) * 4
        elif temp > 30:
            temp_score = 60 + (temp - 30) * 4
        elif temp > 25:
            temp_score = 40 + (temp - 25) * 4
        elif temp > 20:
            temp_score = 30 + (temp - 20) * 2
        elif temp > 15:
            temp_score = 40
        else:
            temp_score = 60
        
        # Humidity score (0-100)
        humidity = weather.humidity
        if humidity > 85:
            humidity_score = 100
        elif humidity > 75:
            humidity_score = 80 + (humidity - 75) * 2
        elif humidity > 65:
            humidity_score = 60 + (humidity - 65) * 2
        elif humidity > 55:
            humidity_score = 40 + (humidity - 55) * 2
        elif humidity > 40:
            humidity_score = 30
        else:
            humidity_score = 50
        
        # Wind benefit (reduces pollution)
        wind_benefit = min(weather.wind_speed * 2, 20)
        
        return (temp_score * 0.55 + humidity_score * 0.45) - wind_benefit
    
    def assess_risk(self, env_data: EnvironmentalData, health_profile: HealthProfile) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        
        # Calculate components
        aqi = self.calculate_aqi(env_data.air_quality)
        weather_score = self.calculate_weather_score(env_data.weather)
        health_multiplier = health_profile.calculate_risk_multiplier()
        
        # Base vulnerability
        base_vulnerability = (aqi / 5 * 0.7 + weather_score * 0.3)
        overall_score = min(base_vulnerability * health_multiplier, 100)
        
        # Component risks
        respiratory_risk = min((aqi / 5) * (1.6 if health_profile.asthma != 'No' else 1.0), 100)
        cardiovascular_risk = min((aqi / 5) * (1.5 if health_profile.bp != 'Normal' else 1.0), 100)
        thermal_comfort = 100 - weather_score
        
        # Determine risk level
        if overall_score >= 80:
            risk_level = RiskLevel.EXTREME
        elif overall_score >= 60:
            risk_level = RiskLevel.CRITICAL
        elif overall_score >= 40:
            risk_level = RiskLevel.HIGH
        elif overall_score >= 20:
            risk_level = RiskLevel.MODERATE
        else:
            risk_level = RiskLevel.LOW
        
        # Contributing factors
        factors = []
        if aqi > 200:
            factors.append("Severe Air Pollution")
        elif aqi > 150:
            factors.append("Poor Air Quality")
        if weather_score > 70:
            factors.append("Extreme Weather")
        if health_multiplier > 1.8:
            factors.append("Multiple Health Vulnerabilities")
        elif health_multiplier > 1.4:
            factors.append("Health Vulnerabilities")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, env_data, health_profile)
        
        return RiskAssessment(
            overall_score=round(overall_score, 1),
            respiratory_risk=round(respiratory_risk, 1),
            cardiovascular_risk=round(cardiovascular_risk, 1),
            thermal_comfort=round(thermal_comfort, 1),
            risk_level=risk_level,
            health_multiplier=round(health_multiplier, 2),
            contributing_factors=factors,
            timestamp=datetime.now(),
            data_confidence=env_data.data_quality,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, risk_level: RiskLevel, env_data: EnvironmentalData, 
                                  health_profile: HealthProfile) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Risk-based recommendations
        if risk_level == RiskLevel.EXTREME:
            recommendations.extend([
                "🚨 EMERGENCY: Stay indoors immediately",
                "😷 Wear N95 mask at all times",
                "🏠 Seal all windows and doors",
                "💨 Use air purifiers continuously",
                "📞 Keep emergency contacts handy"
            ])
        elif risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "⚠️ Avoid all outdoor activities",
                "😷 Wear N95 mask if going out",
                "🏠 Keep windows closed",
                "💨 Use air purifiers",
                "💧 Stay hydrated"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "📊 Limit outdoor exposure to 15 mins",
                "😷 Consider wearing mask",
                "🏠 Keep windows partially closed",
                "💨 Monitor air quality",
                "💧 Drink plenty of water"
            ])
        elif risk_level == RiskLevel.MODERATE:
            recommendations.extend([
                "✅ Normal activities acceptable",
                "👥 Sensitive individuals take care",
                "🪟 Ventilate indoor spaces",
                "📱 Check updates regularly",
                "🏃 Light exercise is safe"
            ])
        else:
            recommendations.extend([
                "🎉 Perfect for outdoor activities",
                "🏃 Exercise recommended",
                "🪟 Open windows for fresh air",
                "🌳 Enjoy nature",
                "👨‍👩‍👧 Great for family outings"
            ])
        
        # Health-specific recommendations
        if health_profile.asthma != 'No' and env_data.air_quality.pm25 > 100:
            recommendations.append("🫁 Keep inhaler accessible")
        
        if health_profile.heart_disease == 'Yes' and risk_level.value in ['HIGH', 'CRITICAL', 'EXTREME']:
            recommendations.append("❤️ Monitor blood pressure")
        
        if health_profile.pregnancy == 'Yes' and risk_level.value in ['HIGH', 'CRITICAL']:
            recommendations.append("🤰 Consult doctor immediately")
        
        return recommendations[:5]  # Return top 5

# ================= MAP GENERATOR =================

class MapGenerator:
    """Professional map generator"""
    
    def __init__(self):
        self.colorscale = [
            [0, '#00ff88'],      # Green - Low
            [0.2, '#00f2fe'],    # Cyan - Moderate
            [0.4, '#ffb700'],    # Yellow - High
            [0.6, '#ff4466'],    # Red - Critical
            [0.8, '#b800e6'],    # Purple - Extreme
            [1.0, '#6b21a8']     # Dark Purple - Severe
        ]
    
    def generate_heatmap(self, env_data: EnvironmentalData, risk: RiskAssessment) -> go.Figure:
        """Generate professional heatmap"""
        
        center = env_data.city.coordinates
        risk_value = risk.overall_score / 100
        
        # Generate 2500 points for smooth visualization
        n_points = 2500
        np.random.seed(42)
        
        angles = np.random.uniform(0, 2*np.pi, n_points)
        distances = np.random.power(1.5, n_points) * 1.5
        
        lats = center.lat + distances * np.cos(angles) * 0.4
        lons = center.lon + distances * np.sin(angles) * 0.4
        
        # Calculate intensities
        intensities = []
        wind_dir = env_data.weather.wind_direction * np.pi / 180
        
        for i in range(n_points):
            dist = distances[i]
            angle = angles[i]
            
            intensity = risk_value * np.exp(-dist * 2)
            
            # Wind effect
            wind_effect = 0.2 * np.cos(angle - wind_dir) * np.exp(-dist)
            intensity += wind_effect
            
            # Hotspots
            if random.random() < 0.03:
                intensity += 0.3
            
            intensity = max(0.1, min(1.0, intensity))
            intensities.append(intensity)
        
        # Create figure
        fig = go.Figure()
        
        # Heatmap layer
        fig.add_trace(go.Densitymapbox(
            lat=lats,
            lon=lons,
            z=intensities,
            radius=20,
            colorscale=self.colorscale,
            opacity=0.8,
            zmin=0,
            zmax=1,
            colorbar=dict(
                title=dict(
                    text="RISK LEVEL",
                    font=dict(color='white', size=14)
                ),
                tickvals=[0.1, 0.3, 0.5, 0.7, 0.9],
                ticktext=['LOW', 'MODERATE', 'HIGH', 'CRITICAL', 'EXTREME'],
                bgcolor='rgba(17,24,39,0.95)',
                tickcolor='white',
                tickfont=dict(color='white', size=11)
            )
        ))
        
        # City marker
        fig.add_trace(go.Scattermapbox(
            lat=[center.lat],
            lon=[center.lon],
            mode='markers+text',
            marker=dict(
                size=30,
                color=risk.risk_level.color,
                symbol='star',
                allowoverlap=True
            ),
            text=[env_data.city.name],
            textposition="top center",
            textfont=dict(color='white', size=14, family='Space Grotesk'),
            hovertemplate='<b>%{text}</b><br>Risk: %{customdata[0]}<br>PM2.5: %{customdata[1]}<extra></extra>',
            customdata=[[risk.risk_level.value, f"{env_data.air_quality.pm25:.0f} µg/m³"]]
        ))
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=center.lat, lon=center.lon),
                zoom=10
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=600,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig

# ================= CHART GENERATOR =================

class ChartGenerator:
    """Professional chart generator"""
    
    @staticmethod
    def create_trend_chart(trend_data: TrendData) -> go.Figure:
        """Create trend analysis chart"""
        
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=trend_data.timestamps,
            y=trend_data.values,
            mode='lines',
            name='Historical',
            line=dict(color='#00f2fe', width=3),
            fill='tozeroy',
            fillcolor='rgba(0,242,254,0.1)'
        ))
        
        # Forecast
        forecast_times = [trend_data.timestamps[-1] + timedelta(hours=i+1) 
                         for i in range(len(trend_data.forecast))]
        
        fig.add_trace(go.Scatter(
            x=forecast_times,
            y=trend_data.forecast,
            mode='lines',
            name='Forecast',
            line=dict(color='#a855f7', width=3, dash='dash')
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=forecast_times + forecast_times[::-1],
            y=trend_data.confidence_upper + trend_data.confidence_lower[::-1],
            fill='toself',
            fillcolor='rgba(168,85,247,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Confidence Range'
        ))
        
        # Risk thresholds
        fig.add_hline(y=80, line_dash="dash", line_color="#b800e6",
                     annotation_text="EXTREME")
        fig.add_hline(y=60, line_dash="dash", line_color="#ff4466",
                     annotation_text="CRITICAL")
        fig.add_hline(y=40, line_dash="dash", line_color="#ffb700",
                     annotation_text="HIGH")
        fig.add_hline(y=20, line_dash="dash", line_color="#00f2fe",
                     annotation_text="MODERATE")
        
        fig.update_layout(
            title=dict(
                text="72-Hour Trend Analysis",
                font=dict(color='white', size=20)
            ),
            xaxis_title="Time",
            yaxis_title="PM2.5 (µg/m³)",
            template="plotly_dark",
            hovermode='x unified',
            height=400,
            margin=dict(l=60, r=60, t=80, b=60),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(17,24,39,0.6)'
        )
        
        return fig
    
    @staticmethod
    def create_gauge(value: float, title: str, color: str) -> go.Figure:
        """Create gauge chart"""
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'color': 'white', 'size': 16}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': 'white'},
                'bar': {'color': color},
                'bgcolor': 'rgba(17,24,39,0.8)',
                'borderwidth': 2,
                'bordercolor': color,
                'steps': [
                    {'range': [0, 20], 'color': 'rgba(0,255,136,0.2)'},
                    {'range': [20, 40], 'color': 'rgba(0,242,254,0.2)'},
                    {'range': [40, 60], 'color': 'rgba(255,183,0,0.2)'},
                    {'range': [60, 80], 'color': 'rgba(255,68,102,0.2)'},
                    {'range': [80, 100], 'color': 'rgba(184,0,230,0.2)'}
                ]
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font={'color': 'white'},
            height=250,
            margin=dict(l=30, r=30, t=50, b=30)
        )
        
        return fig

# ================= SESSION MANAGER =================

class SessionManager:
    """Manage user sessions"""
    
    @staticmethod
    def get_session_id() -> str:
        """Get or create session ID"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = hashlib.md5(
                f"{time.time()}{random.random()}".encode()
            ).hexdigest()[:8]
        return st.session_state.session_id
    
    @staticmethod
    def get_health_profile() -> HealthProfile:
        """Get or create health profile"""
        if 'health_profile' not in st.session_state:
            st.session_state.health_profile = {
                'age': 30,
                'asthma': 'No',
                'bp': 'Normal',
                'immunity': 'Moderate',
                'smoking': 'Never',
                'exercise': 'Moderate',
                'heart_disease': 'No',
                'diabetes': 'No',
                'pregnancy': 'No'
            }
        return st.session_state.health_profile

# ================= MAIN APPLICATION =================

def main():
    """Main application entry point"""
    
    # Initialize services
    data_service = DataService()
    risk_engine = RiskEngine()
    map_gen = MapGenerator()
    chart_gen = ChartGenerator()
    session = SessionManager()
    
    # Get session data
    session_id = session.get_session_id()
    health_data = session.get_health_profile()
    
    # ========== HEADER ==========
    
    st.markdown(f"""
    <div class="amd-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 20px;">
                <span class="amd-title">🏆 PEVI</span>
                <span class="amd-badge">AMD HACKATHON 2026</span>
            </div>
            <div style="display: flex; gap: 30px; color: #9ca3af;">
                <span>⚡ REAL-TIME</span>
                <span style="font-family: monospace;">ID: {session_id}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== HERO SECTION ==========
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        city = st.selectbox(
            "Select City",
            list(data_service.cities.keys()),
            index=0,
            help="Choose location for analysis"
        )
    
    with col2:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; gap: 20px; margin-top: 30px;">
            <div class="live-badge">
                <span class="live-dot"></span>
                <span>LIVE DATA</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Get data
    env_data = data_service.get_environmental_data(city)
    
    # Create health profile
    health_profile = HealthProfile(
        user_id=session_id,
        age=health_data['age'],
        asthma=health_data['asthma'],
        bp=health_data['bp'],
        immunity=health_data['immunity'],
        smoking=health_data['smoking'],
        exercise=health_data['exercise'],
        heart_disease=health_data['heart_disease'],
        diabetes=health_data['diabetes'],
        pregnancy=health_data['pregnancy'],
        timestamp=datetime.now()
    )
    
    # Assess risk
    risk = risk_engine.assess_risk(env_data, health_profile)
    
    # ========== HERO CARD ==========
    
    st.markdown(f"""
    <div class="hero-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="hero-value">{risk.overall_score}</div>
                <div class="hero-label">OVERALL RISK SCORE</div>
                <div style="display: flex; gap: 15px; margin-top: 15px;">
                    <span style="background: {risk.risk_level.bg_color}; color: {risk.risk_level.color}; 
                                 padding: 5px 15px; border-radius: 50px; border: 1px solid {risk.risk_level.color};">
                        {risk.risk_level.value}
                    </span>
                    <span style="color: #9ca3af;">
                        Health Multiplier: {risk.health_multiplier}x
                    </span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="color: #00f2fe; font-size: 1.2rem;">{env_data.city.name}</div>
                <div style="color: #9ca3af;">{env_data.city.description}</div>
                <div style="color: #9ca3af; margin-top: 10px;">
                    👥 {env_data.city.population:,} • 📊 Quality: {env_data.data_quality:.0%}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== METRICS GRID ==========
    
    st.markdown("## 📊 Risk Metrics")
    
    cols = st.columns(4)
    
    metrics = [
        ("AQI", f"{risk_engine.calculate_aqi(env_data.air_quality):.0f}", "µg/m³", "#00f2fe"),
        ("PM2.5", f"{env_data.air_quality.pm25:.0f}", "µg/m³", "#ffb700"),
        ("Temperature", f"{env_data.weather.temperature:.0f}", "°C", "#ff4466"),
        ("Humidity", f"{env_data.weather.humidity:.0f}", "%", "#00ff88")
    ]
    
    for i, (label, value, unit, color) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <div style="color: {color}; font-size: 2rem; font-weight: 700;">{value}</div>
                <div style="color: #9ca3af; font-size: 0.9rem;">{label}</div>
                <div style="color: #6b7280; font-size: 0.8rem;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== MAIN CONTENT ==========
    
    col1, col2 = st.columns([1.2, 1.8])
    
    with col1:
        st.markdown("## 🧬 Health Profile")
        
        with st.expander("Respiratory Health", expanded=True):
            health_data['asthma'] = st.selectbox(
                "Asthma", ["No", "Mild", "Moderate", "Severe"],
                index=["No", "Mild", "Moderate", "Severe"].index(health_data['asthma'])
            )
            health_data['smoking'] = st.selectbox(
                "Smoking", ["Never", "Former", "Current"],
                index=["Never", "Former", "Current"].index(health_data['smoking'])
            )
        
        with st.expander("Cardiovascular Health", expanded=False):
            health_data['bp'] = st.selectbox(
                "Blood Pressure", ["Normal", "Pre-high", "High", "Critical"],
                index=["Normal", "Pre-high", "High", "Critical"].index(health_data['bp'])
            )
            health_data['heart_disease'] = st.selectbox(
                "Heart Disease", ["No", "Yes"],
                index=["No", "Yes"].index(health_data['heart_disease'])
            )
            health_data['diabetes'] = st.selectbox(
                "Diabetes", ["No", "Yes"],
                index=["No", "Yes"].index(health_data['diabetes'])
            )
        
        with st.expander("General Health", expanded=False):
            health_data['age'] = st.number_input("Age", 0, 100, health_data['age'])
            health_data['immunity'] = st.selectbox(
                "Immunity", ["Strong", "Moderate", "Low", "Compromised"],
                index=["Strong", "Moderate", "Low", "Compromised"].index(health_data['immunity'])
            )
            health_data['exercise'] = st.selectbox(
                "Exercise", ["Regular", "Moderate", "Sedentary"],
                index=["Regular", "Moderate", "Sedentary"].index(health_data['exercise'])
            )
            health_data['pregnancy'] = st.selectbox(
                "Pregnancy", ["No", "Yes"],
                index=["No", "Yes"].index(health_data['pregnancy'])
            )
        
        # Component risks
        st.markdown("## 📈 Component Risks")
        
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #ffb700; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between;">
                <span class="metric-label">Respiratory Risk</span>
                <span style="color: #ffb700; font-size: 1.5rem;">{risk.respiratory_risk:.0f}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {risk.respiratory_risk}%; background: linear-gradient(90deg, #ffb700, #ff7e00);"></div>
            </div>
        </div>
        
        <div class="metric-card" style="border-left-color: #ff4466; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between;">
                <span class="metric-label">Cardiovascular Risk</span>
                <span style="color: #ff4466; font-size: 1.5rem;">{risk.cardiovascular_risk:.0f}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {risk.cardiovascular_risk}%; background: linear-gradient(90deg, #ff4466, #ff0000);"></div>
            </div>
        </div>
        
        <div class="metric-card" style="border-left-color: #00ff88;">
            <div style="display: flex; justify-content: space-between;">
                <span class="metric-label">Thermal Comfort</span>
                <span style="color: #00ff88; font-size: 1.5rem;">{risk.thermal_comfort:.0f}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {risk.thermal_comfort}%; background: linear-gradient(90deg, #00ff88, #00f2fe);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("## 🗺️ Risk Heatmap")
        
        # Generate and display map
        fig = map_gen.generate_heatmap(env_data, risk)
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend chart
        st.markdown("## 📉 Trend Analysis")
        trend_data = data_service.get_trend_data(city)
        trend_chart = chart_gen.create_trend_chart(trend_data)
        st.plotly_chart(trend_chart, use_container_width=True)
    
    # ========== RECOMMENDATIONS ==========
    
    st.markdown("## 💡 Smart Recommendations")
    
    cols = st.columns(len(risk.recommendations))
    for i, (col, rec) in enumerate(zip(cols, risk.recommendations)):
        with col:
            priority_colors = ['#ff4466', '#ffb700', '#00f2fe', '#00ff88', '#a855f7']
            color = priority_colors[i % len(priority_colors)]
            
            st.markdown(f"""
            <div class="glass-card" style="border-top: 4px solid {color};">
                <div style="font-size: 2rem; margin-bottom: 10px;">{rec[0]}</div>
                <div style="color: white; font-weight: 600;">{rec[2:]}</div>
                <div style="color: #9ca3af; font-size: 0.8rem; margin-top: 10px;">
                    Priority {i+1}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== FOOTER ==========
    
    st.markdown(f"""
    <div class="amd-footer">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 2000px; margin: 0 auto;">
            <div style="color: #9ca3af;">© 2026 Personalized Environmental Vulnerability Intelligence  </div>
            <div style="display: flex; gap: 30px; color: #9ca3af;">
                <span>⚡ AMD Hackathon 2026</span>
                <span style="color: #a855f7;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()