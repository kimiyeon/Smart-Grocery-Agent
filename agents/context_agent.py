from pi_runtime import load_skill

class ContextAgent:
    def analyze(self, user_input):
        skill = load_skill("parse-intent")
        print(skill)

        return {
            "family_size": user_input["family_size"],
            "allergies": user_input["allergies"],
            "purpose": user_input["purpose"],
            "budget": user_input["budget"]
        }