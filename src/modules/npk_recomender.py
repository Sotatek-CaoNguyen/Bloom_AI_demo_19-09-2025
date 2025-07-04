import pandas as pd
from utils.llm import LLM

class NPKRecommender():
    def __init__(self, target_npk_data_path, system_prompt, user_prompt, api_key):
        self.target_npk_data = pd.read_csv(target_npk_data_path)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLM(api_key = api_key)

    def cal_npk_recommend(self, crop_type, N, P, K):
        data = self.target_npk_data
        instance = data[data["Crop"]==crop_type]
        if instance.empty:
            raise ValueError(f"Crop type '{crop_type}' not found in target_npk_data.")
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
    
    def recommend(self, crop_type, N, P, K, sand, slit, clay, ph, cec, soc):
        NPK_rec = self.cal_npk_recommend(crop_type, N, P, K)
        N_rec, P_rec, K_rec = NPK_rec["N"], NPK_rec["P"], NPK_rec["K"]
        return self.self.llm(self.system_prompt, self.user_prompt, sand, slit, clay, ph, cec, soc, N_rec, P_rec, K_rec)