import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List
import logging
import joblib
import os
from src.llm_service import LLMService

logger = logging.getLogger(__name__)

class CreditAnalyzer:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.llm_service = LLMService()
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the credit risk model"""
        model_path = "models/credit_risk_model.joblib"
        scaler_path = "models/scaler.joblib"
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                logger.info("Loaded pre-trained model and scaler")
            except Exception as e:
                logger.warning(f"Failed to load model: {e}, using fallback model")
                self._create_fallback_model()
        else:
            self._create_fallback_model()
    
    def _create_fallback_model(self):
        """Create a simple fallback model for demonstration"""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
        # Generate sample training data for demonstration
        np.random.seed(42)
        n_samples = 1000
        
        # Features: income, credit_score, loan_amount, employment_length, debt_to_income_ratio
        X = np.random.rand(n_samples, 5)
        X[:, 0] = X[:, 0] * 200000 + 20000  # income: 20k-220k
        X[:, 1] = X[:, 1] * 350 + 450       # credit_score: 450-800
        X[:, 2] = X[:, 2] * 500000 + 10000  # loan_amount: 10k-510k
        X[:, 3] = X[:, 3] * 20              # employment_length: 0-20 years
        X[:, 4] = X[:, 4] * 0.8             # debt_to_income_ratio: 0-0.8
        
        # Simple rule-based target generation
        y = np.zeros(n_samples)
        for i in range(n_samples):
            score = 0
            if X[i, 1] > 700: score += 1  # Good credit score
            if X[i, 4] < 0.3: score += 1  # Low debt ratio
            if X[i, 2] / X[i, 0] < 5: score += 1  # Reasonable loan to income
            if X[i, 3] > 2: score += 1  # Stable employment
            
            if score >= 3:
                y[i] = 0  # Low risk
            elif score >= 2:
                y[i] = 1  # Medium risk
            else:
                y[i] = 2  # High risk
        
        # Train the model
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        # Save the model
        os.makedirs("models", exist_ok=True)
        joblib.dump(self.model, "models/credit_risk_model.joblib")
        joblib.dump(self.scaler, "models/scaler.joblib")
        
        logger.info("Created and saved fallback model")
    
    async def analyze_credit_risk(self, data: Dict[str, Any]) -> Dict:
        """
        Analyze credit risk using ML model and LLM
        """
        try:
            # Extract features
            features = self._extract_features(data)
            
            # ML prediction
            ml_result = self._predict_risk(features)
            
            # LLM analysis
            llm_result = await self._get_llm_analysis(data, ml_result)
            
            return {
                "ml_prediction": ml_result,
                "llm_analysis": llm_result,
                "combined_score": self._combine_scores(ml_result, llm_result),
                "features_analyzed": features,
                "metadata": {
                    "model_version": "1.0",
                    "analysis_timestamp": pd.Timestamp.now().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"Credit analysis failed: {str(e)}")
            raise
    
    def _extract_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from input data"""
        features = [
            float(data.get('income', 0)),
            float(data.get('credit_score', 0)),
            float(data.get('loan_amount', 0)),
            float(data.get('employment_length', 0)),
            float(data.get('debt_to_income_ratio', 0))
        ]
        return np.array(features).reshape(1, -1)
    
    def _predict_risk(self, features: np.ndarray) -> Dict:
        """Predict risk using ML model"""
        try:
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Predict
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            risk_levels = ['Low Risk', 'Medium Risk', 'High Risk']
            
            return {
                "predicted_class": int(prediction),
                "risk_level": risk_levels[int(prediction)],
                "probabilities": {
                    "low_risk": float(probabilities[0]),
                    "medium_risk": float(probabilities[1]),
                    "high_risk": float(probabilities[2])
                },
                "confidence": float(max(probabilities))
            }
        except Exception as e:
            logger.error(f"ML prediction failed: {str(e)}")
            return {
                "predicted_class": 1,
                "risk_level": "Medium Risk",
                "probabilities": {"low_risk": 0.33, "medium_risk": 0.34, "high_risk": 0.33},
                "confidence": 0.34
            }
    
    async def _get_llm_analysis(self, data: Dict[str, Any], ml_result: Dict) -> Dict:
        """Get LLM analysis of the credit data"""
        prompt = f"""
        Analyze this credit application data and provide detailed insights:
        
        Application Details:
        - Annual Income: ${data.get('income', 0):,.2f}
        - Credit Score: {data.get('credit_score', 0)}
        - Requested Loan Amount: ${data.get('loan_amount', 0):,.2f}
        - Employment Length: {data.get('employment_length', 0)} years
        - Current Debt-to-Income Ratio: {data.get('debt_to_income_ratio', 0):.1%}
        
        ML Model Prediction: {ml_result.get('risk_level', 'Unknown')}
        ML Confidence: {ml_result.get('confidence', 0):.1%}
        
        Please provide:
        1. Risk assessment and key factors
        2. Specific recommendations for approval/denial
        3. Suggested loan terms or conditions
        4. Areas of concern and mitigation strategies
        """
        
        try:
            return await self.llm_service.process_prompt(prompt, data)
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            return {
                "response": "LLM analysis unavailable. Based on standard criteria, please review credit score, income stability, and debt ratios.",
                "model": "fallback",
                "confidence": 0.5
            }
    
    def _combine_scores(self, ml_result: Dict, llm_result: Dict) -> Dict:
        """Combine ML and LLM results into final score"""
        ml_confidence = ml_result.get('confidence', 0.5)
        llm_confidence = llm_result.get('confidence', 0.5)
        
        # Weight the results based on confidence
        ml_weight = 0.7  # Higher weight for ML model
        llm_weight = 0.3
        
        combined_confidence = (ml_confidence * ml_weight + llm_confidence * llm_weight)
        
        return {
            "final_risk_level": ml_result.get('risk_level', 'Medium Risk'),
            "combined_confidence": combined_confidence,
            "recommendation": self._get_recommendation(ml_result, combined_confidence),
            "analysis_quality": "high" if combined_confidence > 0.8 else "medium" if combined_confidence > 0.6 else "low"
        }
    
    def _get_recommendation(self, ml_result: Dict, confidence: float) -> str:
        """Generate final recommendation"""
        risk_level = ml_result.get('risk_level', 'Medium Risk')
        
        if confidence < 0.6:
            return "Manual review recommended - insufficient data confidence"
        elif risk_level == "Low Risk":
            return "Approve with standard terms"
        elif risk_level == "Medium Risk":
            return "Approve with conditions or enhanced terms"
        else:
            return "Deny or require additional collateral/co-signer"
    
    async def explain_decision(self, data: Dict[str, Any]) -> str:
        """Generate detailed explanation of credit decision"""
        analysis = await self.analyze_credit_risk(data)
        
        explanation_prompt = f"""
        Provide a clear, detailed explanation of why this credit application received the following assessment:
        
        Final Decision: {analysis['combined_score']['recommendation']}
        Risk Level: {analysis['ml_prediction']['risk_level']}
        Confidence: {analysis['combined_score']['combined_confidence']:.1%}
        
        Application Data:
        {data}
        
        Explain in simple terms:
        1. What factors led to this decision
        2. Which aspects of the application were positive/negative
        3. What the applicant could do to improve their profile
        4. Any regulatory or policy considerations
        """
        
        try:
            result = await self.llm_service.process_prompt(explanation_prompt)
            return result.get('response', 'Explanation not available')
        except:
            return f"Decision based on risk level: {analysis['ml_prediction']['risk_level']} with {analysis['combined_score']['combined_confidence']:.1%} confidence."
    
    def get_status(self) -> Dict:
        """Get status of credit analyzer"""
        return {
            "model_loaded": self.model is not None,
            "scaler_loaded": self.scaler is not None,
            "model_type": type(self.model).__name__ if self.model else None,
            "features_count": 5
        }