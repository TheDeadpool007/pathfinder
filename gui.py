# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List

from main import TripEngine, DESTINATION_LABELS


class PathfinderGUI:
    """Full GUI for Real PDDL Trip Planner."""

    def __init__(self):
        self.engine = TripEngine()
        self.root = tk.Tk()
        self.root.title("PathFinder – Real PDDL Trip Planner (USA Only)")
        self.root.geometry("1000x700")

        self._build_ui()
        self.root.mainloop()

    # ------------------------------------------------------------------
    def _build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        # ---------------- DESTINATION CHECKBOXES -----------------
        dest_frame = ttk.LabelFrame(top_frame, text="Select Destinations")
        dest_frame.grid(row=0, column=0, padx=15, pady=5, sticky="nw")

        self.dest_vars = {}
        row, col = 0, 0

        for key, label in DESTINATION_LABELS.items():
            if key == "home":
                continue
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(dest_frame, text=label, variable=var)
            cb.grid(row=row, column=col, sticky="w", padx=5, pady=2)
            self.dest_vars[key] = var

            row += 1
            if row >= 4:
                row = 0
                col += 1

        # ---------------- OPTIONS FRAME -----------------
        opt_frame = ttk.LabelFrame(top_frame, text="Trip Options")
        opt_frame.grid(row=0, column=1, padx=15, pady=5, sticky="nw")

        ttk.Label(opt_frame, text="Budget (USD):").grid(row=0, column=0, sticky="w")
        self.budget_entry = ttk.Entry(opt_frame)
        self.budget_entry.grid(row=0, column=1, padx=5, pady=3)
        self.budget_entry.insert(0, "2500")

        ttk.Label(opt_frame, text="Days:").grid(row=1, column=0, sticky="w")
        self.days_entry = ttk.Entry(opt_frame)
        self.days_entry.grid(row=1, column=1, padx=5, pady=3)
        self.days_entry.insert(0, "5")

        # ---------------- INTEREST CHECKBOXES -----------------
        interests_frame = ttk.LabelFrame(top_frame, text="Interests")
        interests_frame.grid(row=0, column=2, padx=15, pady=5, sticky="nw")

        interest_labels = {
            "nature": "Nature 🌿",
            "cultural": "Cultural 🏛",
            "entertainment": "Entertainment 🎭",
            "historical": "Historical 🏺",
            "food": "Food 🍽",
            "museum": "Museums 🖼",
        }

        self.interest_vars = {}
        r = 0
        for key, label in interest_labels.items():
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(interests_frame, text=label, variable=var)
            cb.grid(row=r, column=0, sticky="w", padx=5, pady=2)
            self.interest_vars[key] = var
            r += 1

        # ---------------- BUTTONS -----------------
        btn_frame = tk.Frame(top_frame)
        btn_frame.grid(row=0, column=3, padx=15, pady=5, sticky="ne")

        self.plan_btn = ttk.Button(btn_frame, text="Plan Trip", command=self._on_plan)
        self.plan_btn.pack(fill="x", pady=5)

        self.save_chart_btn = ttk.Button(
            btn_frame,
            text="Save Cost Chart",
            command=self._save_chart
        )
        self.save_chart_btn.pack(fill="x", pady=5)
        self.save_chart_btn["state"] = "disabled"

        # ---------------- TABS FOR OUTPUT -----------------
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.txt_domain = self._make_tab(notebook, "PDDL Domain")
        self.txt_problem = self._make_tab(notebook, "PDDL Problem")
        self.txt_plan = self._make_tab(notebook, "Planner Output")
        self.txt_itinerary = self._make_tab(notebook, "Itinerary + Summary")

        self.summary_data = None

    # ------------------------------------------------------------------
    def _make_tab(self, notebook, title: str):
        frame = tk.Frame(notebook)
        notebook.add(frame, text=title)

        text = tk.Text(frame, wrap="word", font=("Consolas", 10))
        text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text["yscrollcommand"] = scrollbar.set

        return text

    # ------------------------------------------------------------------
    def _selected_destinations(self) -> List[str]:
        return [k for k, v in self.dest_vars.items() if v.get()]

    def _selected_interests(self) -> List[str]:
        return [k for k, v in self.interest_vars.items() if v.get()]

    # ------------------------------------------------------------------
    def _on_plan(self):
        try:
            dests = self._selected_destinations()
            if not dests:
                raise ValueError("Select at least one destination.")

            budget = int(self.budget_entry.get())
            days = int(self.days_entry.get())
            interests = self._selected_interests()

            if budget <= 0 or days <= 0:
                raise ValueError("Budget and days must be positive.")

        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return

        self._clear_outputs()
        self._write(self.txt_itinerary, "Planning trip using REAL PDDL solver...\n\n")

        try:
            itinerary, domain, problem, raw_plan, summary = \
                self.engine.plan_trip(dests, budget, days, interests)
        except Exception as e:
            messagebox.showerror("Planning Error", str(e))
            return

        # Fill output tabs
        self._write(self.txt_domain, domain)
        self._write(self.txt_problem, problem)

        self._write(self.txt_plan, "Raw Planner Output:\n\n")
        for i, step in enumerate(raw_plan):
            self._write(self.txt_plan, f"{i}: {step}\n")

        # Itinerary
        self._write(self.txt_itinerary, "=== FINAL ITINERARY ===\n\n")
        current_day = None

        for item in itinerary:
            if item["day"] != current_day:
                current_day = item["day"]
                self._write(self.txt_itinerary, f"\n--- Day {current_day} ---\n")

            self._write(
                self.txt_itinerary,
                f"{item['time']} - {item['description']} "
                f"(Cost: ${item['cost']}, Duration: {item['duration']} mins)\n"
            )

        # Summary
        self._write(self.txt_itinerary, "\n=== SUMMARY ===\n")
        self._write(self.txt_itinerary, f"Total Cost: ${summary['total_cost']}\n")
        self._write(self.txt_itinerary, f"Budget Remaining: ${summary['remaining']}\n")
        self._write(self.txt_itinerary, f"Total Duration: {summary['hours']} hours\n\n")

        self._write(self.txt_itinerary, "Cost Breakdown:\n")
        for t, v in summary["cost_by_type"].items():
            self._write(self.txt_itinerary, f" - {t.title()}: ${v}\n")

        self.summary_data = summary
        self.save_chart_btn["state"] = "normal"

    # ------------------------------------------------------------------
    def _save_chart(self):
        if not self.summary_data:
            messagebox.showerror("Error", "Plan a trip first.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialfile="cost_breakdown.png"
        )
        if not filename:
            return

        try:
            self.engine.save_cost_pie(self.summary_data, filename)
            messagebox.showinfo("Saved", f"Chart saved to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------
    def _write(self, widget: tk.Text, content: str):
        widget.config(state="normal")
        widget.insert("end", content)
        widget.config(state="disabled")

    def _clear_outputs(self):
        for w in [self.txt_domain, self.txt_problem, self.txt_plan, self.txt_itinerary]:
            w.config(state="normal")
            w.delete("1.0", "end")
            w.config(state="disabled")


if __name__ == "__main__":
    PathfinderGUI()
