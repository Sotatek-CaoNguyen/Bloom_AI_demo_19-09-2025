import pandas as pd
from src.utils import LLM

class NPKRecommender():
    def __init__(self, target_npk_path, system_prompt, user_prompt, api_key):
        self.target_npk_data = pd.read_csv(target_npk_path)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLM(api_key = api_key)

    def cal_npk_recommend(self, crop_type, N, P, K):
        data = self.target_npk_data
        instance = data[data["Crop"]==crop_type]
        if instance.empty:
            instance = data[data["Crop"]=="general"]
        instance = instance.iloc[0] 
        current_npk = {"N": N, "P": P, "K": K}
        recommend_npk = {}
        for nutrient in ["N", "P", "K"]:
            val = current_npk[nutrient]
            min_val = instance[f"{nutrient}_min"]
            max_val = instance[f"{nutrient}_max"]
            if val < min_val:
                recommend_npk[nutrient] = (min_val + max_val) / 2 - val
            else:
                recommend_npk[nutrient] = 0
        return recommend_npk
    
    def recommend(self, crop_type, N, P, K, sand, silt, clay, ph, cec, soc):
        NPK_rec = self.cal_npk_recommend(crop_type, N, P, K)
        N_rec, P_rec, K_rec = NPK_rec["N"], NPK_rec["P"], NPK_rec["K"]
        inputs = {
            "crop_type": crop_type,
            "N": N,
            "P": P,
            "K": K,
            "sand": sand,
            "silt": silt,
            "clay": clay,
            "ph": ph,
            "cec": cec,
            "soc": soc,
            "N_rec": N_rec,
            "P_rec": P_rec,
            "K_rec": K_rec
        }
        self.user_prompt = self.user_prompt.format(**inputs)
        return self.llm.generate(self.system_prompt, self.user_prompt)