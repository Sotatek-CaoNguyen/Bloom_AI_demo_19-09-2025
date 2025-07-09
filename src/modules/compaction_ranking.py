import pandas as pd
from src.utils import LLM

class CompactionLevelRanking:
    def __init__(self, compaction_thresholds_path, system_prompt, user_prompt, api_key):
        """
        Initialize CompactionLevelRanking with thresholds data and LLM
        
        Args:
            compaction_thresholds_path: Path to CSV with compaction thresholds by soil texture
            system_prompt: System prompt for LLM
            user_prompt: User prompt template for LLM
            api_key: API key for LLM
        """
        self.compaction_thresholds = pd.read_csv(compaction_thresholds_path)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.llm = LLM(api_key=api_key)
    
    def classify_soil_texture(self, sand, silt, clay):
        """
        Classify soil texture based on sand/silt/clay percentages
        
        Args:
            sand: Sand percentage (%)
            silt: Silt percentage (%)
            clay: Clay percentage (%)
            
        Returns:
            str: Soil texture classification
        """
        # USDA soil texture classification
        if clay >= 40:
            return "Clay"
        elif clay >= 27:
            if sand >= 20:
                return "Clay loam"
            else:
                return "Silty clay"
        elif clay >= 20:
            if sand >= 45:
                return "Clay loam"
            elif silt >= 28:
                return "Silty clay loam"
            else:
                return "Loam"
        elif clay >= 7:
            if sand >= 52:
                return "Sandy clay loam"
            elif silt >= 50:
                return "Silt loam"
            else:
                return "Loam"
        elif silt >= 80:
            return "Silt"
        elif silt >= 50:
            return "Silt loam"
        elif sand >= 85:
            return "Sand"
        elif sand >= 70:
            return "Loamy sand"
        else:
            return "Sandy loam"
    
    def get_compaction_thresholds(self, soil_texture):
        """
        Get compaction thresholds for specific soil texture
        
        Args:
            soil_texture: Classified soil texture
            
        Returns:
            dict: Thresholds for green, orange, red levels
        """
        threshold_data = self.compaction_thresholds[
            self.compaction_thresholds['Soil_Texture'] == soil_texture
        ]
        
        if threshold_data.empty:
            # Default thresholds if specific texture not found
            threshold_data = self.compaction_thresholds[
                self.compaction_thresholds['Soil_Texture'] == 'General'
            ]
        
        return {
            'green_max': threshold_data['Green_Max'].iloc[0],
            'orange_max': threshold_data['Orange_Max'].iloc[0],
            'red_min': threshold_data['Red_Min'].iloc[0]
        }
    
    def classify_compaction_level(self, compaction_value, soil_texture):
        """
        Classify compaction level based on measured value and soil texture
        
        Args:
            compaction_value: Measured compaction value
            soil_texture: Classified soil texture
            
        Returns:
            dict: Classification result with level and color
        """
        thresholds = self.get_compaction_thresholds(soil_texture)
        
        if compaction_value <= thresholds['green_max']:
            return {
                'level': 'Good/Acceptable',
                'color': 'Green',
                'description': 'Compaction level is within acceptable range'
            }
        elif compaction_value <= thresholds['orange_max']:
            return {
                'level': 'Concerning',
                'color': 'Orange',
                'description': 'Compaction level is concerning and may affect crop growth'
            }
        else:
            return {
                'level': 'Alarming',
                'color': 'Red',
                'description': 'Compaction level is alarming and requires immediate attention'
            }
    
    def recommend(self, sand, silt, clay, plough_depth, bare_soil_history, machine_type):
        """
        Estimate compaction level when direct measurement is not available
        
        Args:
            sand, silt, clay: Soil composition percentages
            plough_depth: Past depth of ploughing (cm)
            bare_soil_history: Boolean - was there bare soil between crops
            machine_type: Type of machine used for ploughing
            
        Returns:
            dict: Estimated compaction assessment
        """
        soil_texture = self.classify_soil_texture(sand, silt, clay)
        
        inputs = {
            "sand": sand,
            "silt": silt,
            "clay": clay,
            "soil_texture": soil_texture,
            "plough_depth": plough_depth,
            "bare_soil_history": bare_soil_history,
            "machine_type": machine_type
        }
        
        formatted_prompt = self.user_prompt.format(**inputs)
        return self.llm.generate(self.system_prompt, formatted_prompt)
        
        # return {
        #     'soil_texture': soil_texture,
        #     'estimation_method': 'LLM_based',
        #     'llm_assessment': llm_response,
        #     'inputs_used': inputs
        # }
    
    def assess_compaction(self, sand, silt, clay, compaction_measurement=None, 
                         plough_depth=None, bare_soil_history=None, machine_type=None):
        """
        Main method to assess compaction level
        
        Args:
            sand, silt, clay: Soil composition percentages
            compaction_measurement: Direct compaction measurement (optional)
            plough_depth: Past depth of ploughing (required if no measurement)
            bare_soil_history: Boolean - bare soil between crops (required if no measurement)
            machine_type: Machine type used for ploughing (required if no measurement)
            
        Returns:
            dict: Complete compaction assessment
        """
        soil_texture = self.classify_soil_texture(sand, silt, clay)
        
        result = {
            'soil_texture': soil_texture,
            'sand': sand,
            'silt': silt,
            'clay': clay
        }
        
        if compaction_measurement is not None:
            # Direct measurement available
            classification = self.classify_compaction_level(compaction_measurement, soil_texture)
            result.update({
                'measurement_available': True,
                'compaction_value': compaction_measurement,
                'classification': classification,
                'assessment_method': 'Direct measurement'
            })
        else:
            # No direct measurement - use estimation
            if None in [plough_depth, bare_soil_history, machine_type]:
                raise ValueError("When compaction measurement is not available, "
                               "plough_depth, bare_soil_history, and machine_type are required")
            
            estimation = self.estimate_compaction_without_measurement(
                sand, silt, clay, plough_depth, bare_soil_history, machine_type
            )
            result.update({
                'measurement_available': False,
                'estimation': estimation,
                'assessment_method': 'Estimation based on field history'
            })
        
        return result
    
    def get_recommendations(self, assessment_result):
        """
        Get recommendations based on compaction assessment
        
        Args:
            assessment_result: Result from assess_compaction method
            
        Returns:
            dict: Recommendations for addressing compaction
        """
        if assessment_result['measurement_available']:
            color = assessment_result['classification']['color']
            
            if color == 'Green':
                return {
                    'action_required': 'None',
                    'recommendations': ['Continue current soil management practices']
                }
            elif color == 'Orange':
                return {
                    'action_required': 'Preventive measures',
                    'recommendations': [
                        'Monitor soil moisture before field operations',
                        'Consider controlled traffic farming',
                        'Implement cover crops to improve soil structure'
                    ]
                }
            else:  # Red
                return {
                    'action_required': 'Immediate intervention',
                    'recommendations': [
                        'Implement deep tillage or subsoiling',
                        'Avoid field operations when soil is wet',
                        'Consider using low ground pressure equipment',
                        'Establish permanent traffic lanes'
                    ]
                }
        else:
            return {
                'action_required': 'Assessment needed',
                'recommendations': [
                    'Conduct direct compaction measurement',
                    'Monitor based on field history assessment',
                    'Implement preventive measures as precaution'
                ]
            }
