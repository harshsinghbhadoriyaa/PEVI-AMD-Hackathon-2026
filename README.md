# PEVI-AMD-Hackathon-2026
Personalized Environmental Vulnerability Intelligence - AMD Hackathon 2026


# 🌍 PEVI - Personalized Environmental Vulnerability Intelligence

### 🏆 AMD Hackathon 2026 Submission

![PEVI Dashboard](assets/screenshot1.png)

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture](#architecture)
- [Screenshots](#screenshots)
- [Team](#team)

## 🎯 Overview
PEVI is a real-time environmental risk assessment platform that combines air quality data, weather conditions, and personalized health profiles to provide vulnerability scores and actionable recommendations.

**Problem Statement:** People need personalized, real-time information about how environmental conditions affect their health.

**Solution:** A web application that calculates personalized risk scores based on:
- Real-time air quality (PM2.5, PM10, NO2, etc.)
- Weather conditions (temperature, humidity, wind)
- Individual health profiles (asthma, BP, immunity, etc.)

## ✨ Features

### 🗺️ Real-time Risk Mapping
- Dynamic heatmap showing vulnerability distribution
- City center markers with risk indicators
- Industrial hotspot detection
- Wind dispersion modeling

### 📊 Comprehensive Analytics
- 72-hour trend analysis with confidence intervals
- Real-time AQI, PM2.5, temperature, humidity monitoring
- Multiple risk components:
  - Respiratory Risk
  - Cardiovascular Risk  
  - Thermal Comfort

### 🧬 Personalized Health Integration
- 8+ health factors including:
  - Asthma severity
  - Blood pressure
  - Immunity level
  - Smoking status
  - Exercise frequency
  - Heart disease
  - Diabetes
  - Pregnancy

### 💡 Smart Recommendations
- Personalized safety guidelines
- Real-time alerts based on risk level
- Health-specific advisories
- Priority-based action items

## 🛠️ Tech Stack
- **Frontend/Backend:** Streamlit
- **Data Processing:** NumPy, Pandas
- **Visualizations:** Plotly
- **Maps:** Plotly Mapbox
- **Styling:** Custom CSS with glass morphism

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/harshsinghbhadoriyaa/PEVI-AMD-Hackathon-2026.git
cd PEVI-AMD-Hackathon-2026

# Install dependencies
pip install -r requirements.txt

# Run application
python -m streamlit run app.py

# Note
Before executing above commands don't forget to install Git.
