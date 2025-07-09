import pandas as pd
import requests
from datetime import datetime, timedelta
from src.utils import LLM

class PlantTimingRecommender:
    def __init__(self, seed_variety_path, climate_data_path, system_prompt, user_prompt, api_key, weather_api_key='50f31358bcd0a89ffd161a25a5256572'):
        self.seed_variety_data = pd.read_csv(seed_variety_path)
        self.climate_data = pd.read_csv(climate_data_path) if climate_data_path else None
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLM(api_key=api_key)
        self.weather_api_key = weather_api_key
    
    def get_seed_variety_info(self, seed_variety):
        """Get seed variety characteristics from database"""
        data = self.seed_variety_data
        variety_info = data[data["Variety"] == seed_variety]
        
        if variety_info.empty:
            # Fallback to crop type if specific variety not found
            crop_type = seed_variety.split()[0]  # Assume first word is crop type
            variety_info = data[data["Crop_Type"] == crop_type]
        
        if variety_info.empty:
            variety_info = data[data["Crop_Type"] == "General"]
        
        return variety_info.iloc[0].to_dict()
    
    def get_climate_data(self, latitude, longitude):
        """Get climate data for the given coordinates"""
        if self.weather_api_key:
            return self._fetch_weather_api_data(latitude, longitude)
        else:
            return self._get_climate_from_database(latitude, longitude)
    
    def _fetch_weather_api_data(self, latitude, longitude):
        """Fetch real-time climate data from weather API"""
        try:
            # Example using OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            # Also get historical/seasonal data
            historical_url = f"http://api.openweathermap.org/data/2.5/onecall"
            hist_params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.weather_api_key,
                'exclude': 'current,minutely,hourly,alerts'
            }
            
            hist_response = requests.get(historical_url, params=hist_params)
            hist_data = hist_response.json()
            
            return {
                'avg_temp_min': data['main']['temp_min'],
                'avg_temp_max': data['main']['temp_max'],
                'humidity': data['main']['humidity'],
                'climate_zone': self._determine_climate_zone(latitude, longitude),
                'annual_rainfall': self._estimate_annual_rainfall(hist_data),
                'frost_free_start': self._calculate_frost_free_period(hist_data)[0],
                'frost_free_end': self._calculate_frost_free_period(hist_data)[1],
                'growing_season_length': self._calculate_growing_season(hist_data),
                'soil_temp': data['main']['temp'] - 2,  # Approximation
                'weather_pattern': self._analyze_weather_pattern(hist_data)
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_climate_from_database(latitude, longitude)
    
    def _get_climate_from_database(self, latitude, longitude):
        """Get climate data from local database based on coordinates"""
        if self.climate_data is None:
            # Return default values if no climate database
            return {
                'avg_temp_min': 10,
                'avg_temp_max': 25,
                'humidity': 65,
                'climate_zone': 'Temperate',
                'annual_rainfall': 800,
                'frost_free_start': 90,  # April 1st
                'frost_free_end': 300,   # October 27th
                'growing_season_length': 180,
                'soil_temp': 15,
                'weather_pattern': 'Moderate seasonal variation'
            }
        
        # Find closest climate zone in database
        climate_info = self.climate_data.iloc[0]  # Simplified - should use proper matching
        return climate_info.to_dict()
    
    def _determine_climate_zone(self, latitude, longitude):
        """Determine climate zone based on coordinates"""
        if abs(latitude) < 23.5:
            return "Tropical"
        elif abs(latitude) < 40:
            return "Subtropical"
        elif abs(latitude) < 60:
            return "Temperate"
        else:
            return "Continental"
    
    def _calculate_frost_free_period(self, hist_data):
        """Calculate frost-free period from historical data"""
        # Simplified calculation - should use actual temperature data
        return (90, 300)  # April 1st to October 27th
    
    def _calculate_growing_season(self, hist_data):
        """Calculate growing season length"""
        # Simplified calculation
        return 180  # 6 months
    
    def _estimate_annual_rainfall(self, hist_data):
        """Estimate annual rainfall from historical data"""
        # Simplified calculation
        return 800  # mm
    
    def _analyze_weather_pattern(self, hist_data):
        """Analyze weather patterns"""
        return "Moderate seasonal variation with wet spring and dry summer"
    
    def day_of_year_to_date(self, day_of_year, year=None):
        """Convert day of year to actual date"""
        if year is None:
            year = datetime.now().year
        
        date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
        return date.strftime("%B %d")
    
    def recommend(self, seed_variety,crop_type, latitude, longitude,climate_zone,avg_temp_min, avg_temp_max, annual_rainfall, frost_free_start, frost_free_end, growing_season_length, soil_temp, humidity, weather_pattern):
        """Generate planting timing recommendation"""
        # Get seed variety characteristics
        variety_info = self.get_seed_variety_info(seed_variety)
        
        # Get climate data
        climate_data = self.get_climate_data(latitude, longitude)
        
        # Prepare inputs for LLM
        inputs = {
            "seed_variety": seed_variety,
            "crop_type": crop_type,
            "latitude": latitude,
            "longitude": longitude,
            "climate_zone": climate_zone,
            "avg_temp_min": avg_temp_min,
            "avg_temp_max": avg_temp_max,
            "annual_rainfall": annual_rainfall,
            "frost_free_start": frost_free_start,
            "frost_free_end": frost_free_end,
            "growing_season_length": growing_season_length,
            "soil_temp": soil_temp,
            "humidity": humidity,
            "weather_pattern": weather_pattern
        }
        
        # Format user prompt
        formatted_prompt = self.user_prompt.format(**inputs)
        
        # Generate recommendation
        return self.llm.generate(self.system_prompt, formatted_prompt)
    
    def get_planting_calendar(self, recommendations):
        """Convert recommendations to calendar format"""
        # Parse the LLM response and extract day ranges
        # This would need to be implemented based on the actual LLM response format
        pass