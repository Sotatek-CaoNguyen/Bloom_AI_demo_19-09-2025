import pandas as pd
from src.utils import LLM

class SeedTreatmentRecommender():
    def __init__(self, target_seed_treatment_path, system_prompt, user_prompt, api_key):
        self.target_seed_treatment_data = pd.read_csv(target_seed_treatment_path)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLM(api_key = api_key)

    def inoculant_method_filter(self, crop_type):
        data = self.target_seed_treatment_data
        instance = data[data["Crop"]==crop_type]
        if instance.empty:
            instance = data[data["Crop"]=="General"]
        return instance[['Inoculant', 'Method']].to_dict(orient='records')
    
    def recommend(self, crop_type, N, P, K, sand, silt, clay, ph, cec, soc):
        inoculant_method_list = self.inoculant_method_filter(crop_type)
        inputs = {
            "crop_type": crop_type,
            "inoculant_method_list": inoculant_method_list,
            "N": N,
            "P": P,
            "K": K,
            "sand": sand,
            "silt": silt,
            "clay": clay,
            "ph": ph,
            "cec": cec,
            "soc": soc
        }
        self.user_prompt = self.user_prompt.format(**inputs)
        return self.llm.generate(self.system_prompt, self.user_prompt)