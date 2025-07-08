import pandas as pd
from src.utils import LLM

class FinalRecommeder():
    def __init__(self, system_prompt, user_prompt, api_key):
        self.llm = LLM(api_key = api_key)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    def recommend(self, crop_type, NPK_recs, inoculant_methods, cover_crops, decompaction):
        inputs = {
            "crop_type": crop_type,
            "NPK_recs": NPK_recs,
            "inoculant_methods": inoculant_methods,
            "decompaction": decompaction,
            "cover_crops": cover_crops
        }
        self.user_prompt = self.user_prompt.format(**inputs)
        return self.llm.generate(self.system_prompt, self.user_prompt)