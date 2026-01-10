"""
PromptConcept: Collect and structure change requirements
Purpose: User describes changes -> System parses intent
"""

from typing import Optional
import re


class PromptConcept:
    """
    Parses natural language prompts into structured requirements.
    Free-standing concept with no external dependencies.
    """

    def __init__(self):
        self.raw_prompt = ""
        self.structured_requirements = {}

    def parse_intent(self, prompt: str) -> dict:
        """
        Extract structured requirements from natural language.

        Args:
            prompt: User's description of desired changes

        Returns:
            Structured requirements dict with parsed intent
        """
        self.raw_prompt = prompt.strip()

        requirements = {
            "raw_prompt": self.raw_prompt,
            "action_type": self._detect_action_type(self.raw_prompt),
            "targets": self._extract_targets(self.raw_prompt),
            "properties": self._extract_properties(self.raw_prompt),
            "clarifications": self._generate_clarifications(self.raw_prompt),
        }

        self.structured_requirements = requirements
        return requirements

    def _detect_action_type(self, prompt: str) -> str:
        """Detect the type of change requested."""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["add", "create", "insert", "new"]):
            return "add"
        elif any(word in prompt_lower for word in ["remove", "delete", "hide"]):
            return "remove"
        elif any(word in prompt_lower for word in ["change", "modify", "update", "make"]):
            return "modify"
        elif any(word in prompt_lower for word in ["move", "relocate", "reposition"]):
            return "move"
        else:
            return "modify"

    def _extract_targets(self, prompt: str) -> list[str]:
        """Extract UI elements mentioned in the prompt."""
        common_targets = [
            "header", "footer", "sidebar", "button", "navbar", "menu",
            "dashboard", "card", "table", "form", "input", "search",
            "logo", "icon", "image", "text", "title", "link", "modal",
            "dropdown", "tab", "panel", "section", "container"
        ]

        targets = []
        prompt_lower = prompt.lower()

        for target in common_targets:
            if target in prompt_lower:
                targets.append(target)

        return targets if targets else ["component"]

    def _extract_properties(self, prompt: str) -> dict:
        """Extract visual properties mentioned in the prompt."""
        properties = {}

        # Color detection
        color_pattern = r'\b(red|blue|green|yellow|orange|purple|pink|black|white|gray|grey|dark|light)\b'
        colors = re.findall(color_pattern, prompt.lower())
        if colors:
            properties["colors"] = colors

        # Size detection
        size_pattern = r'\b(large|small|big|tiny|medium|huge)\b'
        sizes = re.findall(size_pattern, prompt.lower())
        if sizes:
            properties["sizes"] = sizes

        # Position detection
        position_pattern = r'\b(top|bottom|left|right|center|middle)\b'
        positions = re.findall(position_pattern, prompt.lower())
        if positions:
            properties["positions"] = positions

        return properties

    def _generate_clarifications(self, prompt: str) -> list[str]:
        """Generate clarifying questions if prompt is ambiguous."""
        clarifications = []

        if len(prompt.split()) < 5:
            clarifications.append("Could you provide more details about the desired changes?")

        if not self._extract_targets(prompt):
            clarifications.append("Which UI element would you like to modify?")

        if not self._extract_properties(prompt):
            clarifications.append("What visual changes are you looking for?")

        return clarifications

    def validate_requirements(self) -> bool:
        """Check if requirements are sufficient for mockup generation."""
        if not self.structured_requirements:
            return False

        has_target = bool(self.structured_requirements.get("targets"))
        has_action = bool(self.structured_requirements.get("action_type"))

        return has_target and has_action

    def get_summary(self) -> str:
        """Generate human-readable summary of requirements."""
        if not self.structured_requirements:
            return "No requirements parsed yet."

        action = self.structured_requirements.get("action_type", "modify")
        targets = self.structured_requirements.get("targets", [])
        properties = self.structured_requirements.get("properties", {})

        target_str = ", ".join(targets) if targets else "component"
        prop_str = ", ".join(f"{k}: {v}" for k, v in properties.items())

        summary = f"{action.capitalize()} {target_str}"
        if prop_str:
            summary += f" with {prop_str}"

        return summary
