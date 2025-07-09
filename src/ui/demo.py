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
    npk_recommender_ = NPKRecommender("src//data/target_npk.csv", npk_recommend_system_prompt, npk_recommend_user_prompt, TOGETHER_API_KEY)
    seed_treatment_recommender_ = SeedTreatmentRecommender("src//data/target_seed_treatment.csv", seed_treatment_system_prompt, seed_treatment_user_prompt, TOGETHER_API_KEY)
    decompaction_recommender = DecompactionRecommender("src//data/target_decompaction.csv", seed_treatment_system_prompt,  decompaction_user_prompt, TOGETHER_API_KEY)
    plant_timing_recommender = PlantTimingRecommender("src//data/target_plant_timing.csv", "src//data/climate.csv", plant_timing_system_prompt, plant_timing_user_prompt, TOGETHER_API_KEY)
    compaction_ranking_recommender = CompactionLevelRanking("src//data/compaction_ranking.csv",compaction_ranking_system_prompt,compaction_ranking_user_prompt,TOGETHER_API_KEY)
    final_recommender_ = FinalRecommeder(final_recommend_system_prompt, final_recommend_user_prompt, TOGETHER_API_KEY)

    st.set_page_config(page_title="Demo AI App", layout="centered")
    st.title("Bloom AI")

    st.subheader("🔢 Enter Input Data")

    col1, col2, col3 = st.columns(3)

    with col1:
        current_cash_crop = st.text_input("🌾 Current Cash Crop", placeholder="e.g., maize").lower().strip()
        N = st.number_input("🟢 Nitrogen (N) (kg/ha)", min_value=0, value=40, step=1)
        ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=5.8, step=0.1)
        sand = st.slider("🌍 Sand (%)", min_value=0, max_value=100, value=65)

    with col2:
        next_cash_crop = st.text_input("🌾 Next Cash Crop", placeholder="e.g., soybean").lower().strip()
        P = st.number_input("🟣 Phosphorus (P) (kg/ha)", min_value=0, value=15, step=1)
        cec = st.number_input("CEC (Cation Exchange Capacity) (cmol/kg)", min_value=0.0, value=12.4, step=0.1)
        silt = st.slider("🌍 Silt (%)", min_value=0, max_value=100, value=20)

    with col3:
        after_next_cash_crop = st.text_input("🌾 After Next Cash Crop", placeholder="e.g., potato").lower().strip()
        K = st.number_input("🟠 Potassium (K) (kg/ha)", min_value=0, value=130, step=1)
        soc = st.number_input("SOC (Soil Organic Carbon) (g/kg)", min_value=0.0, value=1.2, step=0.1)
        clay = st.slider("🌍 Clay (%)", min_value=0, max_value=100, value=15)

    with st.expander("📌 Thông số đất nâng cao", expanded=False):
        soil_moisture = st.number_input("💧 Độ ẩm đất (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1)
        bulk_density = st.number_input("⚖️ Khối lượng riêng đất (g/cm³)", min_value=0.0, max_value=2.5, value=1.3, step=0.01)
        penetration_resistance = st.number_input("🔩 Độ nén xuyên (MPa)", min_value=0.0, max_value=5.0, value=1.2, step=0.1)
        organic_matter = st.number_input("🌱 Chất hữu cơ (%)", min_value=0.0, max_value=20.0, value=2.5, step=0.1)
        soil_depth = st.number_input("📏 Độ sâu đất canh tác (cm)", min_value=0, max_value=200, value=40, step=1)
        traffic_intensity = st.selectbox("🚜 Mức độ đi lại máy móc", options=["Thấp", "Trung bình", "Cao"], index=1)
        compaction_history = st.selectbox("🧱 Lịch sử nén đất", options=["Không có", "Vừa phải", "Nhiều"], index=0)
    with st.expander("🌱 Thông tin giống và khí hậu", expanded=False):
        seed_variety = st.text_input("📘 Tên giống cây trồng", placeholder="e.g., Pioneer 1234").strip()
        
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude = st.number_input("🌍 Vĩ độ (Latitude)", min_value=-90.0, max_value=90.0, value=21.0, step=0.01)
        with col_lon:
            longitude = st.number_input("🌍 Kinh độ (Longitude)", min_value=-180.0, max_value=180.0, value=105.8, step=0.01)

        climate_zone = st.selectbox("🌤 Vùng khí hậu", options=["Tropical", "Subtropical", "Temperate", "Arid", "Other"]) 
        avg_temp_min = st.number_input("🌡 Nhiệt độ trung bình tối thiểu (°C)", min_value=-30.0, max_value=50.0, value=10.0, step=0.1)
        avg_temp_max = st.number_input("🌡 Nhiệt độ trung bình tối đa (°C)", min_value=-30.0, max_value=50.0, value=30.0, step=0.1)
        annual_rainfall = st.number_input("🌧 Lượng mưa hàng năm (mm)", min_value=0, max_value=5000, value=1200, step=1)
        frost_free_start = st.date_input("❄️ Ngày bắt đầu không có sương giá", value=pd.to_datetime("2023-04-01"), help="Thường vào đầu mùa xuân")
        frost_free_end = st.date_input("❄️ Ngày kết thúc không có sương giá", value=pd.to_datetime("2023-10-31"), help="Thường vào cuối mùa thu")
        growing_season_length = st.number_input("🗓 Thời gian sinh trưởng ""yêu cầu (ngày)", min_value=1, max_value=365, value=95, step=1)
        soil_temp = st.number_input("🌡 Nhiệt độ đất", placeholder="e.g., 15°C in March, 20°C in June")
        humidity = st.number_input("💧 Độ ẩm (%)", min_value=0, max_value=100, value=65, step=1)
        weather_pattern = st.text_area("🌦 Mô hình thời tiết", placeholder="e.g., Mưa nhiều từ tháng 5 đến tháng 9, nắng vào mùa hè")
    with st.expander("Compaction Ranking", expanded=False):
        plough_depth = st.number_input("Plough Depth (cm)", min_value=0, max_value=100, value=20, step=1)
        bare_soil_history = st.selectbox("Bare Soil History", options=["No", "Yes"], index=0)
        machine_type = st.selectbox("Machine Type", options=["Tractor", "Manual", "Other"], index=0)

    if st.button("🚀 Recommend"):
        inputs = {
            "current_cash_crop": current_cash_crop,
            "next_cash_crop": next_cash_crop,
            "after_next_cash_crop": after_next_cash_crop,
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
            "soil_moisture" : soil_moisture,
            "bulk_density" : bulk_density,
            "penetration_resistance" : penetration_resistance,
            "organic_matter" : organic_matter,
            "soil_depth" : soil_depth,
            "traffic_intensity" : traffic_intensity,
            "compaction_history" : compaction_history,
            "seed_variety" :seed_variety,
            "latitude": latitude, 
            "longitude": longitude,
            "climate_zone" : climate_zone,
            "avg_temp_min" : avg_temp_min, 
            "avg_temp_max" : avg_temp_max, 
            "annual_rainfall" : annual_rainfall, 
            "frost_free_start" : frost_free_start, 
            "frost_free_end" : frost_free_end,
            "growing_season_length" : growing_season_length, 
            "soil_temp" : soil_temp, 
            "humidity" : humidity, 
            "weather_pattern" : weather_pattern,
            "plough_depth": plough_depth,
            "bare_soil_history": bare_soil_history,
            "machine_type": machine_type
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

            future_plant_timing = executor.submit(
                plant_timing_recommender.recommend,  
                seed_variety= inputs["seed_variety"],
                crop_type= inputs["crop_type"],
                latitude= inputs["latitude"], 
                longitude= inputs["longitude"],
                climate_zone = inputs["climate_zone"],
                avg_temp_min = inputs["avg_temp_min"],
                avg_temp_max = inputs["avg_temp_max"],
                annual_rainfall = inputs["annual_rainfall"],
                frost_free_start = inputs["frost_free_start"],
                frost_free_end = inputs["frost_free_end"],
                soil_temp = inputs["soil_temp"],
                humidity = inputs["humidity"],
                weather_pattern = inputs["weather_pattern"],
                growing_season_length = inputs["growing_season_length"]
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

            future_cover = executor.submit(
                cover_crop_mix_recommender_.recommend,
                current_cash_crop=inputs["current_cash_crop"],
                next_cash_crop=inputs["next_cash_crop"],
                after_next_cash_crop=inputs["after_next_cash_crop"],
                N=inputs["N"],
                P=inputs["P"],
                K=inputs["K"],
                sand=inputs["sand"],
                silt=inputs["silt"],
                clay=inputs["clay"]
            )

            npk_recommend = future_npk.result()
            print("---------------")
            print("NPK Recommendation:")
            print(npk_recommend)
            seed_treatment_recommend = future_seed.result()
            cover_crop_mix_recommend = future_cover.result()
            decompaction_recommend = future_decompaction.result()
            print("---------------")
            print("Decompaction Recommendation:")
            print(decompaction_recommend)
            plant_timing_recommend = future_plant_timing.result()
            print("---------------")
            print("Plant Timing Recommendation:")
            print(plant_timing_recommend)
            compaction_ranking_recommend = future_compaction_ranking.result()
            print("---------------")    
            print("Compaction Ranking Recommendation:")
            print(compaction_ranking_recommend)

        a= inputs["crop_type"]
        b= npk_recommend.split("### Conclusion Section\n")[-1]
        c= seed_treatment_recommend.split("### Conclusion Section\n")[-1]
        d= decompaction_recommend.split("### Conclusion Section\n")[-1]
        e= cover_crop_mix_recommend
        g= plant_timing_recommend.split("### Conclusion Section\n")[-1]
        j = compaction_ranking_recommend.split("### Conclusion Section\n")[-1]
        h = final_recommender_.recommend(a,b,c,d,e,g,j)

        with st.container():
            st.markdown(h)

if __name__ == "__main__":
    main()