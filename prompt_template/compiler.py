"""XML prompt template compiler with variable substitution."""

import re
from pathlib import Path
from typing import Any

from prompt_template.models import PromptContext, PromptVariables


class TemplateCompiler:
    """Compiles XML templates with Mustache-style variable substitution."""

    def __init__(self, templates_dir: str = "prompts"):
        # Resolve relative to this file's location
        base_dir = Path(__file__).parent
        self.templates_dir = base_dir / templates_dir

    def load_template(self, template_name: str) -> str:
        """Load an XML template file."""
        template_path = self.templates_dir / f"{template_name}.xml"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_path.read_text()

    def substitute(
        self,
        template: str,
        context: PromptContext,
        variables: PromptVariables,
        user_query: str,
    ) -> str:
        """
        Substitute variables into the template.

        Supports:
        - {{variable}} - simple substitution
        - {{#list}}...{{.}}...{{/list}} - list iteration
        """
        result = template

        # Build flat dict of all variables
        all_vars = {
            "role": context.role,
            "expertise": context.expertise,
            "constraints": context.constraints,
            "user_query": user_query,
            **variables.variables,
        }

        # Handle list iterations first: {{#list}}...{{.}}...{{/list}}
        result = self._substitute_lists(result, all_vars)

        # Handle simple substitutions: {{variable}}
        result = self._substitute_simple(result, all_vars)

        return result

    def _substitute_lists(self, template: str, variables: dict[str, Any]) -> str:
        """Handle list iteration blocks."""
        pattern = r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}"

        def replace_list(match):
            list_name = match.group(1)
            inner_template = match.group(2)

            items = variables.get(list_name, [])
            if not isinstance(items, list):
                return ""

            result_parts = []
            for item in items:
                # Replace {{.}} with the item value
                if isinstance(item, dict):
                    # For dict items, serialize to string
                    item_str = str(item)
                else:
                    item_str = str(item)
                part = inner_template.replace("{{.}}", item_str)
                result_parts.append(part)

            return "".join(result_parts)

        return re.sub(pattern, replace_list, template, flags=re.DOTALL)

    def _substitute_simple(self, template: str, variables: dict[str, Any]) -> str:
        """Handle simple {{variable}} substitution."""
        pattern = r"\{\{(\w+)\}\}"

        def replace_var(match):
            var_name = match.group(1)
            value = variables.get(var_name, f"{{{{MISSING:{var_name}}}}}")
            return str(value)

        return re.sub(pattern, replace_var, template)

    def compile(
        self,
        template_name: str,
        context: PromptContext,
        variables: PromptVariables,
        user_query: str,
    ) -> str:
        """Load and compile a template with all substitutions."""
        template = self.load_template(template_name)
        return self.substitute(template, context, variables, user_query)
