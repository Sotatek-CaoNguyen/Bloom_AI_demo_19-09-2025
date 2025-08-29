import streamlit as st
import json
import pandas as pd
from src.modules import CoverCropMixRecommender, FinalRecommeder, NPKRecommender, SeedTreatmentRecommender, DecompactionRecommender, PlantTimingRecommender, CompactionLevelRanking
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
load_dotenv(override=True)
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def main():
    with open("src//prompts//npk_recommend_prompt.json", "r", encoding="utf-8") as f:
        npk_recommend_prompt_data = json.load(f)
    npk_recommend_system_prompt = npk_recommend_prompt_data["system_prompt"]
    npk_recommend_user_prompt = npk_recommend_prompt_data["user_prompt"]

    with open("src//prompts//seed_treatment_prompt.json", "r", encoding="utf-8") as f:
        seed_treatment_prompt_data = json.load(f)
    seed_treatment_system_prompt = seed_treatment_prompt_data["system_prompt"]
    seed_treatment_user_prompt = seed_treatment_prompt_data["user_prompt"]

    with open("src//prompts//decompaction_prompt.json", "r", encoding="utf-8") as f:
        decompaction_prompt_data = json.load(f)
    decompaction_system_prompt = decompaction_prompt_data["system_prompt"]       
    decompaction_user_prompt = decompaction_prompt_data["user_prompt"]

    with open("src//prompts//plant_timing_prompt.json", "r", encoding="utf-8") as f:
        plant_timing_prompt_data = json.load(f)
    plant_timing_system_prompt = plant_timing_prompt_data["system_prompt"]
    plant_timing_user_prompt = plant_timing_prompt_data["user_prompt"]

    with open("src//prompts//compaction_ranking.json", "r", encoding="utf-8") as f:
        compaction_ranking_prompt_data = json.load(f)
    compaction_ranking_system_prompt = compaction_ranking_prompt_data["system_prompt"]
    compaction_ranking_user_prompt = compaction_ranking_prompt_data["user_prompt"]

    with open("src//prompts//final_recommend_prompt.json", "r", encoding="utf-8") as f:
        final_recommend_prompt_data = json.load(f)
    final_recommend_system_prompt = final_recommend_prompt_data["system_prompt"]
    final_recommend_user_prompt = final_recommend_prompt_data["user_prompt"]

    cover_crop_mix_recommender_ = CoverCropMixRecommender("src//data/target_cover_crop.csv", "src//data/cover_crop_goal.json", "src//data/recommend_cover_crop.csv")
    npk_recommender_ = NPKRecommender("src//data/target_npk.csv", npk_recommend_system_prompt, npk_recommend_user_prompt, GROQ_API_KEY)
    seed_treatment_recommender_ = SeedTreatmentRecommender("src//data/target_seed_treatment.csv", seed_treatment_system_prompt, seed_treatment_user_prompt, GROQ_API_KEY)
    decompaction_recommender = DecompactionRecommender("src//data/target_decompaction.csv", seed_treatment_system_prompt,  decompaction_user_prompt, GROQ_API_KEY)
    plant_timing_recommender = PlantTimingRecommender("src//data/target_plant_timing.csv", "src//data/climate.csv", plant_timing_system_prompt, plant_timing_user_prompt, GROQ_API_KEY)
    compaction_ranking_recommender = CompactionLevelRanking("src//data/compaction_ranking.csv",compaction_ranking_system_prompt,compaction_ranking_user_prompt,GROQ_API_KEY)
    final_recommender_ = FinalRecommeder(final_recommend_system_prompt, final_recommend_user_prompt, GROQ_API_KEY)

    st.set_page_config(
    page_title="Bloom AI - Smart Agricultural Recommendations", 
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🌱"
)

    # Custom CSS for better styling
    st.markdown("""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Main container styling */
        .main-container {
            font-family: 'Inter', sans-serif;
            padding: 0rem 1rem;
        }
        
        /* Header styling */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .header-title {
            color: white;
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 1.2rem;
            text-align: center;
            font-weight: 400;
        }
        
        /* Input section styling */
        .input-section {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
            border: 1px solid #e1e8ed;
        }
        
        .section-title {
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* Custom button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            font-weight: 600;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        
        /* Input field styling */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            border-radius: 10px;
            border: 2px solid #e1e8ed;
            padding: 0.75rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Slider styling */
        .stSlider > div > div > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 1rem;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .streamlit-expanderContent {
            background: white;
            border-radius: 0 0 10px 10px;
            padding: 1rem;
            border: 1px solid #e1e8ed;
            border-top: none;
        }
        
        /* Results container */
        .results-container {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2rem;
            border-radius: 20px;
            margin-top: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .results-title {
            color: white;
            font-size: 2rem;
            font-weight: 600;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        /* Card styling for input groups */
        .input-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
            border-left: 4px solid #667eea;
        }
        
        .card-title {
            color: #2c3e50;
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .header-title {
                font-size: 2rem;
            }
            
            .header-subtitle {
                font-size: 1rem;
            }
            
            .input-section {
                padding: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Header Section
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🌱 Bloom AI</div>
        <div class="header-subtitle">Intelligent Agricultural Recommendation System</div>
    </div>
    """, unsafe_allow_html=True)

    # # Main input section
    # st.markdown("""
    # <div class="input-section">
    #     <div class="section-title">
    #         📊 Thông tin đầu vào
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)

    # Basic crop information
    st.markdown('<div class="card-title">🌾 Crop Information</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        current_cash_crop = st.text_input("🌾 Current crop", placeholder="e.g. corn, rice").lower().strip()
        
    with col2:
        next_cash_crop = st.text_input("🌾 Next crop", placeholder="e.g. soybean").lower().strip()
        
    with col3:
        after_next_cash_crop = st.text_input("🌾 Subsequent crop", placeholder="e.g. potato").lower().strip()

    st.markdown("---")

    # Soil nutrients section
    st.markdown('<div class="card-title">🧪 Soil Nutrient Parameterss</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        N = st.number_input("🟢 Nitrogen (N) (kg/ha)", min_value=0, value=40, step=1)
        ph = st.number_input("🎯 Soil pH", min_value=0.0, max_value=14.0, value=5.8, step=0.1)

    with col2:
        P = st.number_input("🟣 Phosphorus (P) (kg/ha)", min_value=0, value=15, step=1)
        cec = st.number_input("⚡ CEC (cmol/kg)", min_value=0.0, value=12.4, step=0.1)

    with col3:
        K = st.number_input("🟠 Potassium (K) (kg/ha)", min_value=0, value=130, step=1)
        soc = st.number_input("🌱 Organic Carbon (g/kg)", min_value=0.0, value=1.2, step=0.1)

    st.markdown("---")

    # Soil composition section
    st.markdown('<div class="card-title">🏔️ Soil Composition</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        sand = st.slider("🏖️ Sand (%)", min_value=0, max_value=100, value=65)

    with col2:
        silt = st.slider("🏔️ Silt (%)", min_value=0, max_value=100, value=20)

    with col3:
        clay = st.slider("🧱 Clay (%)", min_value=0, max_value=100, value=15)

    # Advanced soil parameters
    with st.expander("🔬 Advanced Soil Parameters", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            soil_moisture = st.number_input("💧 Soil Moisture (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
            bulk_density = st.number_input("⚖️ Bulk Density (g/cm³)", min_value=0.0, max_value=2.5, value=1.3, step=0.01)
            penetration_resistance = st.number_input("🔩 Penetration Resistance (MPa)", min_value=0.0, max_value=5.0, value=1.2, step=0.1)
            organic_matter = st.number_input("🌱 Organic Matter (%)", min_value=0.0, max_value=20.0, value=2.5, step=0.1)
        
        with col2:
            soil_depth = st.number_input("📏 Cultivation Soil Depth (cm)", min_value=0, max_value=200, value=40, step=1)
            traffic_intensity = st.selectbox("🚜 Machinery Traffic Intensity", options=["Low", "Medium", "High"], index=1)
            compaction_history = st.selectbox("🧱 Compaction History", options=["None", "Moderate", "Severe"], index=0)


    # Climate and seed information
    with st.expander("🌤️ Climate and Seed Information", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            seed_variety = st.text_input("📘 Crop Variety Name", placeholder="e.g. Pioneer 1234").strip()
            climate_zone = st.selectbox("🌤 Climate Zone", options=["Tropical", "Subtropical", "Temperate", "Arid", "Other"])
            latitude = st.number_input("🌍 Latitude", min_value=-90.0, max_value=90.0, value=21.0, step=0.01)
            longitude = st.number_input("🌍 Longitude", min_value=-180.0, max_value=180.0, value=105.8, step=0.01)
            avg_temp_min = st.number_input("🌡️ Minimum Temperature (°C)", min_value=-30.0, max_value=50.0, value=10.0, step=0.1)
            avg_temp_max = st.number_input("🌡️ Maximum Temperature (°C)", min_value=-30.0, max_value=50.0, value=30.0, step=0.1)
        
        with col2:
            annual_rainfall = st.number_input("🌧️ Annual Rainfall (mm)", min_value=0, max_value=5000, value=1200, step=1)
            frost_free_start = st.date_input("❄️ Frost-Free Start Date", value=pd.to_datetime("2023-04-01"))
            frost_free_end = st.date_input("❄️ Frost-Free End Date", value=pd.to_datetime("2023-10-31"))
            growing_season_length = st.number_input("🗓️ Growing Season Length (days)", min_value=1, max_value=365, value=95, step=1)
            soil_temp = st.number_input("🌡️ Soil Temperature (°C)", min_value=0.0, max_value=50.0, value=20.0, step=0.1)
            humidity = st.number_input("💧 Humidity (%)", min_value=0, max_value=100, value=65, step=1)
        
        weather_pattern = st.text_area("🌦️ Weather Pattern", placeholder="e.g. Heavy rain from May to September, sunny in summer")

    # Compaction parameters
    with st.expander("🏗️ Soil Compaction Parameters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            plough_depth = st.number_input("📏 Plough Depth (cm)", min_value=0, max_value=100, value=20, step=1)
        with col2:
            bare_soil_history = st.selectbox("🌱 Bare Soil History", options=["No", "Yes"], index=0)
        with col3:
            machine_type = st.selectbox("🚜 Machinery Type", options=["Tractor", "Manual", "Other"], index=0)

    # Recommendation button
    st.markdown("---")
    # col1, col2, col3 = st.columns([1, 1, 1])
    # with col2:
    #     if st.button("🚀 Generate Recommendation of NPK", key="seed_recommend"):
    #         with st.spinner("🔄 Analyzing and generating recommendations..."):
    #             # Collect all inputs
    #             inputs = {
    #                 "current_cash_crop": current_cash_crop,
    #                 "next_cash_crop": next_cash_crop,
    #                 "after_next_cash_crop": after_next_cash_crop,
    #                 "crop_type": current_cash_crop,
    #                 "N": N,      
    #                 "P": P,       
    #                 "K": K,      
    #                 "pH": ph,
    #                 "CEC": cec,
    #                 "SOC": soc,
    #                 "sand": sand,  
    #                 "silt": silt,
    #                 "clay": clay,
    #                 "soil_moisture": soil_moisture,
    #                 "bulk_density": bulk_density,
    #                 "penetration_resistance": penetration_resistance,
    #                 "organic_matter": organic_matter,
    #                 "soil_depth": soil_depth,
    #                 "traffic_intensity": traffic_intensity,
    #                 "compaction_history": compaction_history,
    #                 "seed_variety": seed_variety,
    #                 "latitude": latitude, 
    #                 "longitude": longitude,
    #                 "climate_zone": climate_zone,
    #                 "avg_temp_min": avg_temp_min, 
    #                 "avg_temp_max": avg_temp_max, 
    #                 "annual_rainfall": annual_rainfall, 
    #                 "frost_free_start": frost_free_start, 
    #                 "frost_free_end": frost_free_end,
    #                 "growing_season_length": growing_season_length, 
    #                 "soil_temp": soil_temp, 
    #                 "humidity": humidity, 
    #                 "weather_pattern": weather_pattern,
    #                 "plough_depth": plough_depth,
    #                 "bare_soil_history": bare_soil_history,
    #                 "machine_type": machine_type
    #             }


    #         with ThreadPoolExecutor() as executor:
    #             future_npk = executor.submit(
    #                 npk_recommender_.recommend,
    #                 crop_type=inputs["crop_type"],
    #                 N=inputs["N"],
    #                 P=inputs["P"],
    #                 K=inputs["K"],
    #                 sand=inputs["sand"],
    #                 silt=inputs["silt"],
    #                 clay=inputs["clay"],
    #                 ph=inputs["pH"],
    #                 cec=inputs["CEC"],
    #                 soc=inputs["SOC"]
    #             )

    #             future_seed = executor.submit(
    #                 seed_treatment_recommender_.recommend,
    #                 crop_type=inputs["crop_type"],
    #                 N=inputs["N"],
    #                 P=inputs["P"],
    #                 K=inputs["K"],
    #                 sand=inputs["sand"],
    #                 silt=inputs["silt"],
    #                 clay=inputs["clay"],
    #                 ph=inputs["pH"],
    #                 cec=inputs["CEC"],
    #                 soc=inputs["SOC"]
    #             )
                
    #             future_decompaction = executor.submit(
    #                 decompaction_recommender.recommend,
    #                 crop_type=inputs["crop_type"],
    #                 sand=inputs["sand"],
    #                 silt=inputs["silt"],
    #                 clay=inputs["clay"],
    #                 soil_moisture=inputs["soil_moisture"],  # Assuming N as a proxy for soil moisture
    #                 bulk_density=inputs["bulk_density"],  # Placeholder value, adjust as needed
    #                 penetration_resistance=inputs["penetration_resistance"],  # Placeholder value, adjust as needed
    #                 organic_matter=inputs["organic_matter"],  # Assuming SOC as a proxy for organic matter
    #                 soil_depth=inputs["soil_depth"],  # Placeholder value, adjust as needed
    #                 traffic_intensity=inputs["traffic_intensity"],  # Placeholder value, adjust as needed
    #                 compaction_history=inputs["compaction_history"]  # Placeholder value, adjust as needed
    #             )

    #             future_plant_timing = executor.submit(
    #                 plant_timing_recommender.recommend,  
    #                 seed_variety= inputs["seed_variety"],
    #                 crop_type= inputs["crop_type"],
    #                 latitude= inputs["latitude"], 
    #                 longitude= inputs["longitude"],
    #                 climate_zone = inputs["climate_zone"],
    #                 avg_temp_min = inputs["avg_temp_min"],
    #                 avg_temp_max = inputs["avg_temp_max"],
    #                 annual_rainfall = inputs["annual_rainfall"],
    #                 frost_free_start = inputs["frost_free_start"],
    #                 frost_free_end = inputs["frost_free_end"],
    #                 soil_temp = inputs["soil_temp"],
    #                 humidity = inputs["humidity"],
    #                 weather_pattern = inputs["weather_pattern"],
    #                 growing_season_length = inputs["growing_season_length"]
    #             )

    #             future_compaction_ranking = executor.submit(
    #                 compaction_ranking_recommender.recommend,
    #                 sand=inputs["sand"],   
    #                 silt=inputs["silt"],
    #                 clay=inputs["clay"],
    #                 plough_depth = inputs["plough_depth"],
    #                 bare_soil_history = inputs["bare_soil_history"],
    #                 machine_type = inputs["machine_type"]
    #             )

    #             future_cover = executor.submit(
    #                 cover_crop_mix_recommender_.recommend,
    #                 current_cash_crop=inputs["current_cash_crop"],
    #                 next_cash_crop=inputs["next_cash_crop"],
    #                 after_next_cash_crop=inputs["after_next_cash_crop"],
    #                 N=inputs["N"],
    #                 P=inputs["P"],
    #                 K=inputs["K"],
    #                 sand=inputs["sand"],
    #                 silt=inputs["silt"],
    #                 clay=inputs["clay"]
    #             )

    #             npk_recommend = future_npk.result()
    #             print("---------------")
    #             print("NPK Recommendation:")
    #             print(npk_recommend)
    #             seed_treatment_recommend = future_seed.result()
    #             cover_crop_mix_recommend = future_cover.result()
    #             decompaction_recommend = future_decompaction.result()
    #             print("---------------")
    #             print("Decompaction Recommendation:")
    #             print(decompaction_recommend)
    #             plant_timing_recommend = future_plant_timing.result()
    #             print("---------------")
    #             print("Plant Timing Recommendation:")
    #             print(plant_timing_recommend)
    #             compaction_ranking_recommend = future_compaction_ranking.result()
    #             print("---------------")    
    #             print("Compaction Ranking Recommendation:")
    #             print(compaction_ranking_recommend)

    #         a= inputs["crop_type"]
    #         b= npk_recommend.split("### Conclusion Section\n")[-1]
    #         c= seed_treatment_recommend.split("### Conclusion Section\n")[-1]
    #         d= decompaction_recommend.split("### Reasoning Section\n")[-1]
    #         e= cover_crop_mix_recommend
    #         g= plant_timing_recommend.split("### Reasoning Section\n")[-1]
    #         j = compaction_ranking_recommend.split("### Reasoning Section\n")[-1]
    #         h = final_recommender_.recommend(a,b,c,d,e,g,j)

    #         with st.container():
    #             st.markdown("### 1)NPK Recommendation")
    #             st.markdown(npk_recommend)
    #             st.markdown("### 2)Seed Treatment Recommendation")
    #             st.markdown(seed_treatment_recommend)
    #             st.markdown("### 3)Decompaction Recommendation")
    #             st.markdown(decompaction_recommend)
    #             st.markdown("### 4)Cover Crop Mix Recommendation")
    #             st.markdown(cover_crop_mix_recommend)
    #             st.markdown("### 5)Plant Timing Recommendation")
    #             st.markdown(plant_timing_recommend)
    #             st.markdown("### 6)Compaction Ranking Recommendation")
    #             st.markdown(compaction_ranking_recommend)
    #             st.markdown("### 7)Final Recommendation")
                # st.markdown(h)
    

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🚀 Generate Recommendation of NPK", key="npk_recommend_button"):
            with st.spinner("🔄 Analyzing and generating recommendations..."):
                # Collect all inputs
                inputs = {
                    "crop_type": current_cash_crop,
                    "N": N,      
                    "P": P,       
                    "K": K,      
                    "pH": ph,
                    "CEC": cec,
                    "SOC": soc,
                    "sand": sand,  
                    "silt": silt,
                    "clay": clay,
                }


            with ThreadPoolExecutor() as executor:
                future_npk = executor.submit(
                    npk_recommender_.recommend,
                    crop_type=inputs["crop_type"],
                    N=inputs["N"],
                    P=inputs["P"],
                    K=inputs["K"],
                    sand=inputs["sand"],
                    silt=inputs["silt"],
                    clay=inputs["clay"],
                    ph=inputs["pH"],
                    cec=inputs["CEC"],
                    soc=inputs["SOC"]
                )

                npk_recommend = future_npk.result()

            with st.container():
                st.markdown("### 1)NPK Recommendation")
                st.markdown(npk_recommend.split("### Conclusion Section\n")[-1])
                
    with col2:
        if st.button("🚀 Generate Recommendation of Seed", key="seed_recommend"):
            with st.spinner("🔄 Analyzing and generating recommendations..."):
                # Collect all inputs
                inputs = {
                    "crop_type": current_cash_crop,
                    "N": N,
                    "P": P,
                    "K": K,
                    "pH": ph,
                    "CEC": cec,
                    "SOC": soc,
                    "sand": sand,
                    "silt": silt,
                    "clay": clay,
                }

                with ThreadPoolExecutor() as executor:
                    future_seed = executor.submit(
                        seed_treatment_recommender_.recommend,
                        crop_type=inputs["crop_type"],
                        N=inputs["N"],
                        P=inputs["P"],
                        K=inputs["K"],
                        sand=inputs["sand"],
                        silt=inputs["silt"],
                        clay=inputs["clay"],
                        ph=inputs["pH"],
                        cec=inputs["CEC"],
                        soc=inputs["SOC"]
                    )
                    seed_treatment_recommend = future_seed.result()

            # Use a container for better layout control
            with st.container():
                st.markdown("### 2) Seed Treatment Recommendation", unsafe_allow_html=True)
                
                # Check if the output is a string or a list of dictionaries
                if isinstance(seed_treatment_recommend, str):
                    # If it's a string, split and process it
                    recommendations = seed_treatment_recommend.split("### Conclusion Section\n")[-1].strip()
                    st.markdown(recommendations)
                else:
                    # Assuming seed_treatment_recommend is a list of dictionaries
                    for idx, recommendation in enumerate(seed_treatment_recommend, 1):
                        with st.expander(f"Recommendation {idx}: {recommendation.get('Recommended Inoculant Mix', 'Unknown Mix')}"):
                            st.markdown(f"**Description**: {recommendation.get('Description', 'No description available')}")
                            st.markdown(f"**Recommended Quantity**: {recommendation.get('Recommended Quantity', 'N/A')} kg/ha")
                            st.markdown(f"**Recommended Date**: {recommendation.get('Recommended Date', 'N/A')}")
                            st.markdown(f"**Application Instruction**: {recommendation.get('Application Instruction', 'N/A')}")
                            st.markdown("---")  # Separator line for visual distinction


    with col3:
        if st.button("🚀 Generate Recommendation of Decompaction/Compation", key="cover_recommend"):
            with st.spinner("🔄 Analyzing and generating recommendations..."):
                # Collect all inputs
                inputs = {
                    "crop_type": current_cash_crop,
    
                    "sand": sand,  
                    "silt": silt,
                    "clay": clay,
                    "soil_moisture": soil_moisture,
                    "bulk_density": bulk_density,
                    "penetration_resistance": penetration_resistance,
                    "organic_matter": organic_matter,
                    "soil_depth": soil_depth,
                    "traffic_intensity": traffic_intensity,
                    "compaction_history": compaction_history,
                    "seed_variety": seed_variety,
                    "plough_depth": plough_depth,
                    "bare_soil_history": bare_soil_history,
                    "machine_type": machine_type
                }


            with ThreadPoolExecutor() as executor:
                future_decompaction = executor.submit(
                    decompaction_recommender.recommend,
                    crop_type=inputs["crop_type"],
                    sand=inputs["sand"],
                    silt=inputs["silt"],
                    clay=inputs["clay"],
                    soil_moisture=inputs["soil_moisture"],  # Assuming N as a proxy for soil moisture
                    bulk_density=inputs["bulk_density"],  # Placeholder value, adjust as needed
                    penetration_resistance=inputs["penetration_resistance"],  # Placeholder value, adjust as needed
                    organic_matter=inputs["organic_matter"],  # Assuming SOC as a proxy for organic matter
                    soil_depth=inputs["soil_depth"],  # Placeholder value, adjust as needed
                    traffic_intensity=inputs["traffic_intensity"],  # Placeholder value, adjust as needed
                    compaction_history=inputs["compaction_history"]  # Placeholder value, adjust as needed
                )

                future_compaction_ranking = executor.submit(
                    compaction_ranking_recommender.recommend,
                    sand=inputs["sand"],   
                    silt=inputs["silt"],
                    clay=inputs["clay"],
                    plough_depth = inputs["plough_depth"],
                    bare_soil_history = inputs["bare_soil_history"],
                    machine_type = inputs["machine_type"]
                )
           
                decompaction_recommend = future_decompaction.result()
                
                compaction_ranking_recommend = future_compaction_ranking.result()
         

            with st.container():
                st.markdown("### 3)Decompaction Recommendation")
                st.markdown(decompaction_recommend.split("### Conclusion Section\n")[-1])
                st.markdown("### 4)Compaction Ranking Recommendation")
                st.markdown(compaction_ranking_recommend.split("### Conclusion Section\n")[-1])

    st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌱 Bloom AI - Intelligent Agricultural Recommendation System</p>
    <p>Developed with ❤️ to support Vietnamese farmers</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()