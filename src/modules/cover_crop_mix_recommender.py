import pandas as pd
import json
import operator

class CoverCropMixRecommender():
    def __init__(self, target_cover_crop_mix_data_path, cover_crop_goal_path, final_cover_crop_mix_path):
        self.target_cover_crop_mix_data = pd.read_csv(target_cover_crop_mix_data_path)
        with open(cover_crop_goal_path, "r") as f:
            self.cover_crop_goal_data = json.load(f)
        self.final_cover_crop_mix_data = pd.read_csv(final_cover_crop_mix_path)

    def target_cover_crop_filter(self, current_cash_crop, next_cash_crop, after_next_cash_crop, top_k=5):
        scores = {}
        for _, row in self.target_cover_crop_mix_data.iterrows():
            cash_crop = row['Cash Crop']
            cover_crop = row['Cover Crop']
            timing = row['Timing']
            if cover_crop not in scores:
                scores[cover_crop] = 0
            if cash_crop == current_cash_crop and timing in ['after', 'both']:
                scores[cover_crop] += 1
            if cash_crop == next_cash_crop and timing in ['before', 'both']:
                scores[cover_crop] += 1
            if cash_crop == next_cash_crop and timing in ['after', 'both']:
                scores[cover_crop] += 1
            if cash_crop == after_next_cash_crop and timing in ['before', 'both']:
                scores[cover_crop] += 1
        cover_crop_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        cover_crop_scores = cover_crop_scores[:top_k]
        return [cover_crop[0] for cover_crop in cover_crop_scores]
    
    def classify_cover_crop_goal(self, N, P, K, sand, silt, clay):
        soil_data = {"N": N, "P": P, "K": K, "sand": sand, "silt": silt, "clay": clay}
        ops = {"<": operator.lt, ">": operator.gt}
        rules = self.cover_crop_goal_data
        matched_goals = []
        for goal, conditions in rules.items():
            check = True
            for cond in conditions:
                key = cond["key"]
                op = cond["op"]
                val = cond["value"]
                if key in soil_data and not ops[op](soil_data[key], val):
                    check = False
            if check:
                matched_goals.append(goal)
        if matched_goals == []:
            for goal, conditions in rules.items():
                for cond in conditions:
                    key = cond["key"]
                    op = cond["op"]
                    val = cond["value"]
                    if key in soil_data and ops[op](soil_data[key], val):
                        matched_goals.append(goal)
        return list(set(matched_goals))
    
    def final_cover_crop_filter(self, cover_crops, cover_crop_goals, top_k=3):
        results = []
        data = self.final_cover_crop_mix_data
        for crop in cover_crops:
            crop_goals = data[data['Cover Crop'] == crop]['Goal'].tolist()
            matched_goals = [g for g in crop_goals if g in cover_crop_goals]
            if matched_goals:
                results.append((crop, matched_goals))
        results.sort(key=lambda x: len(x[1]), reverse=True)
        return results[:top_k]
    
    def recommend(self, current_cash_crop, next_cash_crop, after_next_cash_crop, N, P, K, sand, silt, clay):
        cover_crops = self.target_cover_crop_filter(current_cash_crop, next_cash_crop, after_next_cash_crop)
        cover_crop_goals = self.classify_cover_crop_goal(N, P, K, sand, silt, clay)
        final_cover_crops = self.final_cover_crop_filter(cover_crops, cover_crop_goals)
        return final_cover_crops