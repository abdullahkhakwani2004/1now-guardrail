# 1Now GuardRail 🚗🛡️
### Take-Home Assignment — Support Automation Prototype

1Now GuardRail is a Python-based CLI tool designed to automate mid-trip damage claims for independent car-rental fleet operators. It solves a major administrative headache: instantly differentiating between pre-existing vehicle wear-and-tear and brand-new damage incidents.

## 🌟 Key Features & "Messy Edges" Handled
* **Bidirectional Keyword Matching:** Intelligently maps natural customer language (e.g., *"front bumper is scraped"*) to inspection log entries (*"scratch on front bumper"*) without requiring heavy NLP infrastructure.
* **Input Validation Guardrails:** Normalizes case/whitespace matching, blocks empty strings, and rejects suspiciously short entries (accidental keystrokes).
* **Safety Routing Fork:** If a customer reports a high-severity issue affecting drivability, the app intercepts the workflow to immediately provide emergency roadside assistance context.
* **Graceful Interrupt Handling:** Captures terminal interrupts (`Ctrl+C`) cleanly to protect user experience.

## 🚀 How to Run the Prototype
1. Ensure you have Python installed on your machine.
2. Clone this repository or download `app.py`.
3. Open your terminal, navigate to the folder, and execute:
   ```bash
   python app.py
