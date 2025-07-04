import pandas as pd
from utils.llm import LLM

class SeedTreatmentRecommender():
    def __init__(self, target_npk_data_path, system_prompt, user_prompt, api_key):
        self.target_npk_data = pd.read_csv(target_npk_data_path)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLM(api_key = api_key)

    def inoculant_method_filter(self, crop_type):
        data = self.target_npk_data
        instance = data[data["Crop"]==crop_type]
        if instance.empty:
            raise ValueError(f"Crop type '{crop_type}' not found in target_npk_data.")
        return instance[['Inoculant', 'Method']].to_dict(orient='records')
    
    def recommend(self, crop_type, N, P, K, sand, slit, clay, ph, cec, soc):
        inoculant_method_list = self.inoculant_method_filter(crop_type)
        return self.llm.generate(self.system_prompt, self.user_prompt, inoculant_method_list, N, P, K, sand, slit, clay, ph, cec, soc)