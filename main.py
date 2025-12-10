# main.py
from typing import List, Dict, Tuple
from planner import RealPlanner
from pddl_builder import PDDLBuilder

# Optional plotting
try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# ---------------------------------------------------------------------
# REALISTIC USA TRAVEL DISTANCES (km) + durations (minutes)
# ---------------------------------------------------------------------
USA_DISTANCE_MATRIX = {
    ("los_angeles", "san_francisco"): (615, 360),
    ("san_francisco", "los_angeles"): (615, 360),

    ("los_angeles", "las_vegas"): (435, 270),
    ("las_vegas", "los_angeles"): (435, 270),

    ("san_francisco", "las_vegas"): (917, 540),
    ("las_vegas", "san_francisco"): (917, 540),

    ("new_york", "chicago"): (1145, 780),
    ("chicago", "new_york"): (1145, 780),

    ("new_york", "miami"): (1750, 1200),
    ("miami", "new_york"): (1750, 1200),

    ("chicago", "las_vegas"): (2440, 1500),
    ("las_vegas", "chicago"): (2440, 1500),

    ("miami", "chicago"): (2200, 1320),
    ("chicago", "miami"): (2200, 1320),

    ("los_angeles", "miami"): (3760, 2400),
    ("miami", "los_angeles"): (3760, 2400),

    # default fallback if pair missing:
}


# ---------------------------------------------------------------------
# ATTRACTION METADATA
# ---------------------------------------------------------------------
ATTRACTIONS = {
    "los_angeles": [
        {"id": "hollywood_sign", "name": "Hollywood Sign", "price": 0, "duration": 90,
         "tags": ["nature", "monument", "cultural"]},
        {"id": "getty_center", "name": "Getty Center", "price": 20, "duration": 180,
         "tags": ["cultural", "museum"]},
        {"id": "griffith_observatory", "name": "Griffith Observatory", "price": 0, "duration": 120,
         "tags": ["cultural", "science", "nature"]},
        {"id": "santa_monica_pier", "name": "Santa Monica Pier", "price": 0, "duration": 120,
         "tags": ["entertainment", "nature"]},
    ],

    "san_francisco": [
        {"id": "golden_gate_bridge", "name": "Golden Gate Bridge", "price": 0, "duration": 90,
         "tags": ["monument", "nature"]},
        {"id": "alcatraz_island", "name": "Alcatraz Island", "price": 45, "duration": 180,
         "tags": ["historical", "cultural"]},
        {"id": "fishermans_wharf", "name": "Fisherman's Wharf", "price": 0, "duration": 120,
         "tags": ["entertainment", "food"]},
        {"id": "chinatown_walk", "name": "Chinatown Cultural Walk", "price": 0, "duration": 90,
         "tags": ["cultural", "historical"]},
    ],

    "las_vegas": [
        {"id": "bellagio_fountains", "name": "Bellagio Fountains", "price": 0, "duration": 30,
         "tags": ["entertainment"]},
        {"id": "red_rock_canyon", "name": "Red Rock Canyon", "price": 15, "duration": 240,
         "tags": ["nature", "adventure"]},
        {"id": "high_roller", "name": "High Roller Wheel", "price": 25, "duration": 60,
         "tags": ["entertainment"]},
        {"id": "fremont_street", "name": "Fremont Street Experience", "price": 0, "duration": 90,
         "tags": ["entertainment", "cultural"]},
    ],

    "new_york": [
        {"id": "statue_liberty", "name": "Statue of Liberty", "price": 25, "duration": 180,
         "tags": ["historical", "monument", "cultural"]},
        {"id": "central_park", "name": "Central Park Walk", "price": 0, "duration": 120,
         "tags": ["nature", "relaxation"]},
        {"id": "met_museum", "name": "Metropolitan Museum of Art", "price": 25, "duration": 240,
         "tags": ["museum", "cultural"]},
        {"id": "times_square", "name": "Times Square", "price": 0, "duration": 60,
         "tags": ["entertainment"]},
    ],

    "chicago": [
        {"id": "millennium_park", "name": "Millennium Park", "price": 0, "duration": 90,
         "tags": ["nature", "cultural"]},
        {"id": "art_institute", "name": "Art Institute of Chicago", "price": 25, "duration": 180,
         "tags": ["museum", "cultural"]},
        {"id": "navy_pier", "name": "Navy Pier", "price": 10, "duration": 120,
         "tags": ["entertainment", "food"]},
        {"id": "willis_tower", "name": "Willis Tower Skydeck", "price": 32, "duration": 90,
         "tags": ["monument", "cultural"]},
    ],

    "miami": [
        {"id": "south_beach", "name": "South Beach", "price": 0, "duration": 180,
         "tags": ["nature", "relaxation"]},
        {"id": "wynwood_walls", "name": "Wynwood Walls", "price": 0, "duration": 90,
         "tags": ["art", "cultural"]},
        {"id": "little_havana", "name": "Little Havana Walk", "price": 0, "duration": 120,
         "tags": ["cultural", "food"]},
        {"id": "vizcaya_museum", "name": "Vizcaya Museum", "price": 25, "duration": 120,
         "tags": ["museum", "historical"]},
    ],
}


# ---------------------------------------------------------------------
# RESTAURANT METADATA
# ---------------------------------------------------------------------
RESTAURANTS = {
    "los_angeles": [
        {"name": "In-N-Out Burger", "price": 12, "tags": ["food", "fast_food"]},
        {"name": "Republique", "price": 45, "tags": ["food", "french"]},
        {"name": "Bestia", "price": 65, "tags": ["food", "italian"]},
    ],

    "san_francisco": [
        {"name": "Tartine Bakery", "price": 15, "tags": ["food", "bakery"]},
        {"name": "Swan Oyster Depot", "price": 35, "tags": ["food", "seafood"]},
        {"name": "Zuni Café", "price": 45, "tags": ["food", "american"]},
    ],

    "las_vegas": [
        {"name": "Gordon Ramsay Hell’s Kitchen", "price": 85, "tags": ["food", "fine_dining"]},
        {"name": "Secret Pizza", "price": 18, "tags": ["food", "pizza"]},
        {"name": "Bacchanal Buffet", "price": 65, "tags": ["food", "buffet"]},
    ],

    "new_york": [
        {"name": "Joe's Pizza", "price": 8, "tags": ["food", "pizza"]},
        {"name": "Katz's Delicatessen", "price": 25, "tags": ["food", "deli"]},
        {"name": "Le Bernardin", "price": 200, "tags": ["food", "fine_dining"]},
    ],

    "chicago": [
        {"name": "Lou Malnati's Pizza", "price": 20, "tags": ["food", "pizza"]},
        {"name": "Alinea", "price": 250, "tags": ["food", "fine_dining"]},
        {"name": "Portillo's", "price": 15, "tags": ["food", "american"]},
    ],

    "miami": [
        {"name": "Versailles Restaurant", "price": 20, "tags": ["food", "cuban"]},
        {"name": "Joe's Stone Crab", "price": 80, "tags": ["food", "seafood"]},
        {"name": "Yardbird", "price": 40, "tags": ["food", "american"]},
    ],
}


# ---------------------------------------------------------------------
# DESTINATION LABELS
# ---------------------------------------------------------------------
DESTINATION_LABELS = {
    "los_angeles": "Los Angeles",
    "san_francisco": "San Francisco",
    "las_vegas": "Las Vegas",
    "new_york": "New York City",
    "chicago": "Chicago",
    "miami": "Miami",
    "home": "Home",
}


# ---------------------------------------------------------------------
# TRIP ENGINE - core logic
# ---------------------------------------------------------------------

class TripEngine:

    def __init__(self):
        self.planner = RealPlanner()
        self.builder = PDDLBuilder()

    # -----------------------------------------------
    # MAIN ENTRY
    # -----------------------------------------------
    def plan_trip(
        self,
        destinations: List[str],
        budget: int,
        days: int,
        interests: List[str]
    ) -> Tuple[List[Dict], str, str, List[str], Dict]:

        if not destinations:
            raise ValueError("No destinations selected.")

        # Build domain + problem
        domain = self.builder.build_domain()
        problem = self.builder.build_problem(
            ["home"] + destinations,
            "home",
            destinations
        )

        # DEBUG PRINT
        print("=== DOMAIN ===")
        print(domain)
        print("=== PROBLEM ===")
        print(problem)

        # Real PDDL plan with fallback
        raw_plan = self.planner.solve_with_fallback(domain, problem)

        # Convert into itinerary
        itinerary = self._interpret_plan(raw_plan, budget, days, interests)

        # Compute summary
        summary = self._summarize(itinerary, budget)

        return itinerary, domain, problem, raw_plan, summary

    # -----------------------------------------------
    # CONVERT RAW PLAN INTO ITINERARY
    # -----------------------------------------------
    def _interpret_plan(
        self,
        plan: List[str],
        budget: int,
        days: int,
        interests: List[str]
    ) -> List[Dict]:

        itinerary = []
        current_day = 1
        current_time = 9 * 60   # start 09:00

        for step in plan:
            tokens = (
                step.lower()
                .replace("(", "")
                .replace(")", "")
                .split()
            )
            if not tokens:
                continue

            if tokens[0] == "travel":
                frm, to = tokens[1], tokens[2]
                cost, duration = self._travel_cost_duration(frm, to)

                itinerary.append({
                    "type": "travel",
                    "description": f"Travel from {self._label(frm)} to {self._label(to)}",
                    "cost": cost,
                    "duration": duration,
                    "day": current_day,
                    "time": self._time_str(current_time)
                })

                current_time += duration

            elif tokens[0] == "visit":
                city = tokens[1]

                # Choose matching attractions
                attractions = ATTRACTIONS.get(city, [])
                # filter by interests
                if interests:
                    attractions = [
                        a for a in attractions
                        if any(tag in interests for tag in a["tags"])
                    ]

                if not attractions:
                    continue

                # take the top attraction (simple choice)
                a = attractions[0]

                itinerary.append({
                    "type": "visit",
                    "description": f"Visit {a['name']}",
                    "cost": a["price"],
                    "duration": a["duration"],
                    "day": current_day,
                    "time": self._time_str(current_time)
                })

                current_time += a["duration"]

                # Add a meal if time allows
                restaurants = RESTAURANTS.get(city, [])
                if restaurants and current_time < (19 * 60):
                    r = restaurants[0]
                    itinerary.append({
                        "type": "meal",
                        "description": f"Dine at {r['name']}",
                        "cost": r["price"],
                        "duration": 75,
                        "day": current_day,
                        "time": self._time_str(current_time)
                    })
                    current_time += 75

            # Day rollover
            if current_time >= 19 * 60:
                current_day += 1
                current_time = 9 * 60

        return itinerary

    # -----------------------------------------------
    # COST + DURATION MODELS
    # -----------------------------------------------
    def _travel_cost_duration(self, frm: str, to: str):
        """Return realistic cost + duration using USA_DISTANCE_MATRIX."""
        if (frm, to) in USA_DISTANCE_MATRIX:
            km, mins = USA_DISTANCE_MATRIX[(frm, to)]
        else:
            km, mins = (500, 300)  # fallback distance

        cost = round(km * 0.12)  # $0.12 per km
        return cost, mins

    # -----------------------------------------------
    # SUMMARY
    # -----------------------------------------------
    def _summarize(self, itinerary: List[Dict], budget: int):
        total_cost = sum(i["cost"] for i in itinerary)
        total_minutes = sum(i["duration"] for i in itinerary)

        cost_by_type = {}
        for item in itinerary:
            t = item["type"]
            cost_by_type[t] = cost_by_type.get(t, 0) + item["cost"]

        return {
            "total_cost": total_cost,
            "budget": budget,
            "remaining": budget - total_cost,
            "hours": round(total_minutes / 60, 1),
            "cost_by_type": cost_by_type,
        }

    # -----------------------------------------------
    # HELPERS
    # -----------------------------------------------
    def _label(self, city: str):
        return DESTINATION_LABELS.get(city, city.replace("_", " ").title())

    def _time_str(self, minutes: int):
        return f"{minutes//60:02d}:{minutes%60:02d}"

    # -----------------------------------------------
    # CHART EXPORT
    # -----------------------------------------------
    def save_cost_pie(self, summary: Dict, path: str):
        if not HAS_MATPLOTLIB:
            raise Exception("matplotlib not installed.")
        labels = []
        sizes = []
        for k, v in summary["cost_by_type"].items():
            labels.append(k.title())
            sizes.append(v)
        plt.figure(figsize=(4, 4))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%")
        plt.title("Cost Breakdown")
        plt.savefig(path)
        plt.close()

# ---------------------------------------------------------------------
# MAIN EXECUTION TEST
# ---------------------------------------------------------------------
if __name__ == "__main__":
    engine = TripEngine()
    print("TripEngine loaded successfully")
