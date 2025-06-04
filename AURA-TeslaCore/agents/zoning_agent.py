# agents/zoning_agent.py 
# Enforces zoning laws, land use rules, height, FAR, setbacks, site shape constraints

from typing import Dict, List, Optional

class ZoningAgent:
    def __init__(self, site_data: Dict, zoning_rules: Dict):
        self.site_data = site_data
        self.rules = zoning_rules
        self.violations = []

    def check_far(self, built_up_area: float) -> bool:
        """
        FAR (Floor Area Ratio) = Total built-up area / Site area
        """
        site_area = self.site_data['area']
        max_far = self.rules['far']
        far = built_up_area / site_area
        if far > max_far:
            self.violations.append(f"FAR exceeded: {far:.2f} > allowed {max_far}")
            return False
        return True

    def check_setbacks(self, footprint: Dict[str, float]) -> bool:
        """
        Check if the building footprint respects required setbacks (front, rear, side)
        """
        result = True
        for edge, dist in self.rules['setbacks'].items():
            if footprint.get(edge, 0) < dist:
                self.violations.append(f"{edge} setback too small: {footprint.get(edge)} < {dist}")
                result = False
        return result

    def check_height(self, proposed_height: float) -> bool:
        max_height = self.rules['height_limit']
        if proposed_height > max_height:
            self.violations.append(f"Height limit exceeded: {proposed_height} > {max_height}")
            return False
        return True

    def check_land_use(self, program: str) -> bool:
        allowed = self.rules['allowed_uses']
        if program not in allowed:
            self.violations.append(f"Land use '{program}' not permitted in zone.")
            return False
        return True

    def validate(self, plan_summary: Dict) -> bool:
        """
        Run all checks: FAR, setbacks, height, land use.
        plan_summary = {
            'built_up_area': 210.0,
            'footprint': {'front': 5.2, 'rear': 3.0, 'left': 2.0, 'right': 2.1},
            'height': 9.5,
            'program': 'residential'
        }
        """
        self.violations.clear()
        checks = [
            self.check_far(plan_summary['built_up_area']),
            self.check_setbacks(plan_summary['footprint']),
            self.check_height(plan_summary['height']),
            self.check_land_use(plan_summary['program'])
        ]
        return all(checks)

    def get_violations(self) -> List[str]:
        return self.violations


# Example usage
if __name__ == "__main__":
    site = {'area': 500.0}  # m²
    rules = {
        'far': 1.5,
        'height_limit': 10.0,
        'setbacks': {
            'front': 5.0,
            'rear': 3.0,
            'left': 2.5,
            'right': 2.5
        },
        'allowed_uses': ['residential', 'office']
    }

    sample_plan = {
        'built_up_area': 620.0,
        'footprint': {'front': 4.2, 'rear': 3.0, 'left': 2.5, 'right': 2.1},
        'height': 11.0,
        'program': 'residential'
    }

    agent = ZoningAgent(site, rules)
    if agent.validate(sample_plan):
        print("✅ Zoning validation passed!")
    else:
        print("❌ Zoning validation failed:")
        for v in agent.get_violations():
            print(" -", v)
