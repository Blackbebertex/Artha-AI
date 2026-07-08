"""Load prompt templates for wealth chain steps."""
import os
from functools import lru_cache

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")


@lru_cache(maxsize=16)
def load_prompt(step_filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, step_filename)
    with open(path, encoding="utf-8") as f:
        return f.read()


def render_prompt(step_filename: str, **kwargs) -> str:
    template = load_prompt(step_filename)
    for key, value in kwargs.items():
        template = template.replace(f"{{{{{key}}}}}", str(value))
    return template
