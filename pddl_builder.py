# pddl_builder.py
from typing import List
from textwrap import dedent

class PDDLBuilder:
    """Builds REAL PDDL domain and problem files with correct, flush-left syntax."""

    def build_domain(self) -> str:
        domain = """(define (domain trip)
  (:requirements :strips :typing)
  (:types location)

  (:predicates
    (at ?l - location)
    (connected ?a - location ?b - location)
    (visited ?l - location)
  )

  (:action travel
    :parameters (?from - location ?to - location)
    :precondition (and (at ?from) (connected ?from ?to))
    :effect (and
      (not (at ?from))
      (at ?to)
    )
  )

  (:action visit
    :parameters (?place - location)
    :precondition (at ?place)
    :effect (visited ?place)
  )
)
"""
        return domain

    def build_problem(self, locations: List[str], start: str, goals: List[str]) -> str:
        # OBJECTS
        all_locs = " ".join(locations)

        # INIT
        init_lines = [f"(at {start})"]
        for a in locations:
            for b in locations:
                if a != b:
                    init_lines.append(f"(connected {a} {b})")
        init_str = "\n    ".join(init_lines)

        # GOALS
        goal_parts = [f"(visited {g})" for g in goals]
        goal_str = "\n      ".join(goal_parts)

        # PROBLEM (flush-left, no indentation before (define))
        problem = f"""(define (problem trip-problem)
  (:domain trip)

  (:objects
    {all_locs} - location
  )

  (:init
    {init_str}
  )

  (:goal
    (and
      {goal_str}
    )
  )
)
"""
        return problem
