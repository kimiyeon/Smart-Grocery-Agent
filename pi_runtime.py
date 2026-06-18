import os

def load_skill(skill_name):
    path = f".pi/skills/{skill_name}/SKILL.md"

    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        return f.read()