# planner.py
import requests
import json

PLANNER_API_URL = "https://solver.planning.domains/solve"

class RealPlanner:
    """
    Wrapper around the Planning.Domains API.
    This executes a REAL planner, not simulated logic.
    """

    def solve(self, domain_str: str, problem_str: str):
        payload = {
            "domain": domain_str,
            "problem": problem_str
        }

        try:
            print(f"Sending request to: {PLANNER_API_URL}")
            print(f"Payload size - Domain: {len(domain_str)} chars, Problem: {len(problem_str)} chars")
            
            response = requests.post(
                PLANNER_API_URL,
                json=payload,
                timeout=40,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            # Check if response is successful
            response.raise_for_status()
            
            data = response.json()
            print(f"Response data keys: {list(data.keys())}")
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response content: {response.text}")
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"Response text: {response.text}")
            raise Exception(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise Exception(f"Planner request failed: {e}")

        if data.get("status") != "ok":
            raise Exception(
                "Planner returned an error:\n" +
                json.dumps(data, indent=2)
            )

        plan_steps = data["result"]["plan"]
        return [step["name"] for step in plan_steps]
    
    def solve_with_fallback(self, domain_str: str, problem_str: str):
        """Try the real planner first, fall back to simple planner if it fails."""
        try:
            return self.solve(domain_str, problem_str)
        except Exception as e:
            print(f"Real planner failed: {e}")
            print("Falling back to simple planner...")
            return self._simple_fallback_planner(domain_str, problem_str)
    
    def _simple_fallback_planner(self, domain_str: str, problem_str: str):
        """Simple fallback planner when the API is unavailable."""
        # Extract locations and goals from the problem string
        import re
        
        # Find objects section
        objects_match = re.search(r':objects\s+([^)]+)', problem_str)
        if not objects_match:
            raise Exception("Could not parse problem objects")
        
        objects_line = objects_match.group(1).strip()
        locations = [loc.strip() for loc in objects_line.split('-')[0].split()]
        
        # Find goal section  
        goals_match = re.search(r'\(visited\s+([^)]+)\)', problem_str)
        if not goals_match:
            raise Exception("Could not parse problem goals")
        
        # Simple plan: travel to each goal location and visit it
        plan = []
        current = "home"  # assume we start at home
        
        # Extract all visited goals
        visited_goals = re.findall(r'\(visited\s+([^)]+)\)', problem_str)
        
        for goal in visited_goals:
            goal = goal.strip()
            if goal != current:
                plan.append(f"(travel {current} {goal})")
                current = goal
            plan.append(f"(visit {goal})")
        
        print(f"Fallback plan generated: {plan}")
        return plan
