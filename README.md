# PathFinder - Real PDDL Trip Planner

An AI-powered trip planning application that uses PDDL (Planning Domain Definition Language) for automated travel itinerary generation across major US cities.

## Features

- **AI Planning**: Uses formal PDDL planning with fallback to simple planner
- **Multiple Destinations**: Los Angeles, San Francisco, Las Vegas, New York City, Chicago, Miami
- **Smart Recommendations**: Interest-based filtering (nature, cultural, entertainment, historical, food, museums)
- **Realistic Costs**: Based on actual travel distances and attraction prices
- **Full GUI**: Easy-to-use Tkinter interface with tabbed output
- **Detailed Itineraries**: Day-by-day scheduling with costs and durations

## Files

- `main.py` - Core trip planning engine with attraction/restaurant data
- `gui.py` - Tkinter GUI application
- `pddl_builder.py` - PDDL domain and problem file generator
- `planner.py` - Planning API interface with fallback planner

## Installation

1. Clone this repository
2. Install required packages:
   ```bash
   pip install requests matplotlib tkinter
   ```
3. Run the application:
   ```bash
   python gui.py
   ```

## Usage

1. Select your desired destinations
2. Set budget and trip duration
3. Choose your interests
4. Click "Plan Trip" to generate your itinerary
5. View the results in the tabbed output (PDDL files, planner output, final itinerary)

## Technology

- **PDDL**: Formal planning language for AI systems
- **Planning.Domains API**: Real automated planning service (with fallback)
- **Python**: Core implementation with Tkinter GUI
- **Realistic Data**: Actual distances, costs, and attraction information

## Example Output

The planner generates detailed itineraries including:
- Travel routes between cities
- Attraction recommendations based on interests
- Restaurant suggestions
- Cost breakdowns
- Day-by-day scheduling

Built with ❤️ using AI planning technology.