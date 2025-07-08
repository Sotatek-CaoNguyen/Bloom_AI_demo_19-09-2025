import streamlit as st
import json
import pandas as pd
from src.modules import CoverCropMixRecommender, FinalRecommeder, NPKRecommender, SeedTreatmentRecommender, DecompactionRecommender
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

    with open("src//prompts//final_recommend_prompt.json", "r", encoding="utf-8") as f:
        final_recommend_prompt_data = json.load(f)
    final_recommend_system_prompt = final_recommend_prompt_data["system_prompt"]
    final_recommend_user_prompt = final_recommend_prompt_data["user_prompt"]

    cover_crop_mix_recommender_ = CoverCropMixRecommender("src//data/target_cover_crop.csv", "src//data/cover_crop_goal.json", "src//data/recommend_cover_crop.csv")
    npk_recommender_ = NPKRecommender("src//data/target_npk.csv", npk_recommend_system_prompt, npk_recommend_user_prompt, TOGETHER_API_KEY)
    seed_treatment_recommender_ = SeedTreatmentRecommender("src//data/target_seed_treatment.csv", seed_treatment_system_prompt, seed_treatment_user_prompt, TOGETHER_API_KEY)
    decompaction_recommender = DecompactionRecommender("src//data/target_decompaction.csv", seed_treatment_system_prompt,  decompaction_user_prompt, TOGETHER_API_KEY)
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
            "clay": clay
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
                soil_moisture=0.8,  # Assuming N as a proxy for soil moisture
                bulk_density=1.2,  # Placeholder value, adjust as needed
                penetration_resistance=1.5,  # Placeholder value, adjust as needed
                organic_matter=inputs["SOC"],  # Assuming SOC as a proxy for organic matter
                soil_depth=30,  # Placeholder value, adjust as needed
                traffic_intensity="low",  # Placeholder value, adjust as needed
                compaction_history="none"  # Placeholder value, adjust as needed
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
            print("NPK Recommendation:")
            print(npk_recommend)
            seed_treatment_recommend = future_seed.result()
            cover_crop_mix_recommend = future_cover.result()
            decompaction_recommend = future_decompaction.result()
            print("decompaction Recommendation:")
            print(decompaction_recommend)

        a= inputs["crop_type"]
        b= npk_recommend.split("### Conclusion Section\n")[-1]
        c= seed_treatment_recommend.split("### Conclusion Section\n")[-1]
        d= decompaction_recommend.split("### Conclusion Section\n")[-1]
        e= cover_crop_mix_recommend
        g = final_recommender_.recommend(a,b,c,d,e)

        with st.container():
            st.markdown(g)

if __name__ == "__main__":
    main()