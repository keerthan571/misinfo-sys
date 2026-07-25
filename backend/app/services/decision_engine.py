class DecisionEngine:

    def decide(self, verification_result, ml_result=None):

        verdict = verification_result.get("verdict", "").lower()
        confidence = self._extract_confidence(
            verification_result.get("confidence", "0%")
        )

        # 1. Trusted verification says TRUE
        if verdict == "true" and confidence >= 80:
            return {
                "final_verdict": "REAL",
                "decision_source": "FACT_VERIFICATION",
                "confidence": confidence,
                "details": verification_result
            }

        # 2. Trusted verification says FALSE
        if verdict == "false" and confidence >= 80:
            return {
                "final_verdict": "FAKE",
                "decision_source": "FACT_VERIFICATION",
                "confidence": confidence,
                "details": verification_result
            }

        # 3. Misleading content
        if verdict == "misleading":
            return {
                "final_verdict": "MISLEADING",
                "decision_source": "FACT_VERIFICATION",
                "confidence": confidence,
                "details": verification_result
            }

        # 4. Verification is uncertain → use ML fallback
        if ml_result:

            ml_prediction = ml_result.get("prediction", "").lower()
            ml_confidence = ml_result.get("confidence", 0)

            if ml_prediction == "real":
                return {
                    "final_verdict": "REAL",
                    "decision_source": "ML_MODEL",
                    "confidence": ml_confidence,
                    "details": ml_result
                }

            if ml_prediction == "fake":
                return {
                    "final_verdict": "FAKE",
                    "decision_source": "ML_MODEL",
                    "confidence": ml_confidence,
                    "details": ml_result
                }

        # 5. Nothing is reliable
        return {
            "final_verdict": "UNVERIFIED",
            "decision_source": "NONE",
            "confidence": confidence,
            "details": verification_result
        }

    def _extract_confidence(self, value):

        if isinstance(value, str):
            value = value.replace("%", "").strip()

        try:
            return float(value)
        except:
            return 0.0


decision_engine = DecisionEngine()