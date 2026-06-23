"""
1Now GuardRail — Mid-Trip Damage Notification Handler
======================================================
A CLI prototype for car-rental support automation.
Helps agents (or customers) quickly determine whether reported
damage is pre-existing or new, and routes the case accordingly.
"""

import textwrap
import datetime
import random
import string

# ---------------------------------------------------------------------------
# MOCK DATABASE
# ---------------------------------------------------------------------------
# In a real system these would be fetched from a rental management API.
# Each vehicle carries a pre_existing_damage list — a normalised list of
# lowercase keyword phrases recorded during the pre-trip inspection.
# An empty list means the car was returned spotless at the last check-in.

VEHICLES = {
    "V001": {
        "make": "Toyota",
        "model": "Camry",
        "year": 2022,
        "plate": "LHR-4821",
        "pre_existing_damage": [
            "scratch on front bumper",
            "small dent on rear door",
        ],
    },
    "V002": {
        "make": "Honda",
        "model": "Civic",
        "year": 2023,
        "plate": "LHR-7743",
        "pre_existing_damage": [],          # Clean car — zero pre-existing damage
    },
    "V003": {
        "make": "Suzuki",
        "model": "Cultus",
        "year": 2021,
        "plate": "ISB-0192",
        "pre_existing_damage": [
            "crack on windshield",
            "worn tyre on rear left",
        ],
    },
}

# Each booking links a customer to a vehicle.
# booking_id → { customer details, vehicle_id, trip dates }
BOOKINGS = {
    "BK-1001": {
        "customer_name": "Ayesha Tariq",
        "vehicle_id": "V001",          # Has pre-existing damage
        "pickup_date": "2026-06-20",
        "return_date": "2026-06-25",
    },
    "BK-1002": {
        "customer_name": "Omar Farooq",
        "vehicle_id": "V002",          # Clean car
        "pickup_date": "2026-06-22",
        "return_date": "2026-06-27",
    },
    "BK-1003": {
        "customer_name": "Sara Malik",
        "vehicle_id": "V003",          # Has pre-existing damage (incl. windshield crack)
        "pickup_date": "2026-06-21",
        "return_date": "2026-06-24",
    },
}

# ---------------------------------------------------------------------------
# DISPLAY HELPERS
# ---------------------------------------------------------------------------

WIDTH = 60  # Console column width for visual consistency

def divider(char="─"):
    print(char * WIDTH)

def header():
    """Prints the branded application header."""
    print()
    divider("═")
    print("  🚗  1Now GuardRail — Damage Notification Handler")
    print("       Powered by 1Now Support Automation")
    divider("═")
    print()

def section(title: str):
    """Prints a subtle section separator with a label."""
    print()
    divider()
    print(f"  {title}")
    divider()

def wrap_print(text: str, indent: int = 2):
    """Word-wraps a block of text to fit the console width."""
    prefix = " " * indent
    for line in textwrap.wrap(text, width=WIDTH - indent):
        print(prefix + line)

def generate_ticket_id() -> str:
    """Creates a mock support ticket ID (e.g. TKT-A3F9)."""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TKT-{suffix}"

# ---------------------------------------------------------------------------
# CORE LOGIC
# ---------------------------------------------------------------------------

def get_booking(booking_id: str) -> dict | None:
    """
    Returns the booking dict if the ID exists, otherwise None.
    Normalises input to uppercase so 'bk-1001' still matches 'BK-1001'.
    This is the primary guard against invalid/mistyped IDs.
    """
    return BOOKINGS.get(booking_id.upper().strip())


def match_damage(reported: str, pre_existing: list[str]) -> str | None:
    """
    Checks whether the customer's reported damage overlaps with any
    pre-existing damage entry for the vehicle.

    Strategy — simple substring / keyword matching:
      1. Normalise both sides to lowercase.
      2. For each pre-existing entry, check if any *word* from that entry
         appears in the reported string, AND vice versa (bidirectional
         containment guards against accidental single-word matches like 'on').
      3. Return the first matched pre-existing entry, or None if no match.

    Why this approach?
    ─────────────────
    Customers rarely describe damage in the exact words the agent used
    during inspection.  "There's a big crack in the front glass" should
    still map to "crack on windshield".  A full NLP pipeline would be
    ideal in production, but keyword overlap is a good-enough heuristic
    for this prototype and is trivially explainable to customers.
    """
    reported_lower = reported.lower()
    # Build a set of meaningful words from the reported description,
    # filtering out short stop-words (≤ 3 chars) to avoid false positives.
    reported_words = {w for w in reported_lower.split() if len(w) > 3}

    for entry in pre_existing:
        entry_lower = entry.lower()
        entry_words = {w for w in entry_lower.split() if len(w) > 3}

        # Match if there is ANY meaningful word overlap in either direction
        if reported_words & entry_words:
            return entry  # Return the original logged description

    return None  # No match found


def handle_known_damage(booking: dict, vehicle: dict, matched_entry: str):
    """Reassures the customer when the damage is already on record."""
    section("✅  Pre-Existing Damage Confirmed")
    wrap_print(
        f"Good news, {booking['customer_name'].split()[0]}! We found a match "
        f"in the pre-trip inspection report for your {vehicle['year']} "
        f"{vehicle['make']} {vehicle['model']} ({vehicle['plate']})."
    )
    print()
    print(f"  📋  Logged entry : \"{matched_entry}\"")
    print()
    wrap_print(
        "This damage was documented before your rental began. You will NOT "
        "be held responsible or charged for it. No further action is needed "
        "on your end — enjoy the rest of your trip!"
    )
    print()
    wrap_print(
        "If you have any other concerns, feel free to contact 1Now support "
        "at any time."
    )


def handle_new_damage(booking: dict, vehicle: dict, reported: str):
    """
    Handles a damage report that does NOT match any pre-existing entry.
    Asks a safety follow-up, then simulates logging a support ticket.
    """
    section("⚠️   New Damage Detected")
    wrap_print(
        f"Thank you for letting us know, {booking['customer_name'].split()[0]}. "
        f"The damage you've described does not appear in the pre-trip inspection "
        f"report for your vehicle. We've noted the following:"
    )
    print()
    print(f"  🔍  Reported     : \"{reported}\"")
    print(f"  🚗  Vehicle      : {vehicle['year']} {vehicle['make']} {vehicle['model']}")
    print(f"  🪪  Plate        : {vehicle['plate']}")
    print()

    # ── Follow-up safety question ──────────────────────────────────────────
    # This is important: if drivability is affected, the customer needs
    # guidance beyond a simple ticket log (e.g. pull over, call roadside).
    wrap_print(
        "Before we log this, we have one quick question:"
    )
    print()
    print("  ❓  Does this damage affect the safety or drivability")
    print("      of the car? (yes / no)")
    print()

    # Safely handle unexpected input on the safety question.
    while True:
        safety_input = input("  Your answer: ").strip().lower()
        if safety_input in ("yes", "y", "no", "n"):
            break
        # Messy edge: customer types something other than yes/no.
        print()
        wrap_print(
            "Please enter 'yes' or 'no' so we can route your case correctly."
        )
        print()

    safety_flag = safety_input in ("yes", "y")

    # ── Simulate ticket creation ───────────────────────────────────────────
    ticket_id = generate_ticket_id()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    section("📝  Support Ticket Created")
    print(f"  Ticket ID    : {ticket_id}")
    print(f"  Timestamp    : {timestamp}")
    print(f"  Booking      : {booking.get('_id', '')}".strip())
    print(f"  Customer     : {booking['customer_name']}")
    print(f"  Vehicle      : {vehicle['year']} {vehicle['make']} {vehicle['model']} — {vehicle['plate']}")
    print(f"  Description  : {reported}")
    print(f"  Safety Risk  : {'YES ⚠️' if safety_flag else 'No'}")
    print()

    if safety_flag:
        wrap_print(
            "🚨  Because this may affect drivability, please pull over safely "
            "when possible and call our 24/7 roadside assistance line: "
            "0800-1NOW-HELP. A specialist will assist you immediately."
        )
    else:
        wrap_print(
            "Since the damage doesn't appear to affect safety, you can continue "
            "your trip. Our team will review this ticket (ref: "
            + ticket_id + ") and reach out before your return date to "
            "walk you through next steps. We appreciate you reporting this promptly."
        )

    print()
    wrap_print(
        "A confirmation summary has been sent to the email on file. "
        "Thank you for being a responsible 1Now renter!"
    )


# ---------------------------------------------------------------------------
# MAIN APPLICATION LOOP
# ---------------------------------------------------------------------------

def main():
    header()
    wrap_print(
        "Welcome to 1Now GuardRail. This tool helps you report any "
        "damage you've noticed during your trip so we can handle it "
        "quickly and fairly."
    )

    # ── Step 1: Booking ID input & validation ─────────────────────────────
    # We loop until a valid ID is supplied or the user explicitly quits.
    # This guards against typos, wrong-format IDs, and accidental blank input.
    section("Step 1 — Identify Your Booking")
    print("  Hint: Booking IDs look like  BK-1001")
    print("  (Type 'quit' at any time to exit.)")
    print()

    while True:
        raw_id = input("  Enter your Booking ID: ").strip()

        # Messy edge: user leaves input blank
        if not raw_id:
            print()
            wrap_print("Booking ID cannot be empty. Please try again.")
            print()
            continue

        # Graceful exit
        if raw_id.lower() == "quit":
            print()
            wrap_print("Session ended. Safe travels! 👋")
            print()
            return

        booking = get_booking(raw_id)

        if booking is None:
            # Messy edge: ID doesn't exist in our records
            print()
            wrap_print(
                f"We couldn't find a booking with ID '{raw_id.upper()}'. "
                "Please double-check your confirmation email and try again."
            )
            print()
            continue

        # Valid booking found — attach the ID for use in ticket logging
        booking["_id"] = raw_id.upper()
        break

    # Pull the associated vehicle record
    vehicle = VEHICLES[booking["vehicle_id"]]

    # Confirm booking details back to the user
    section("Booking Confirmed")
    print(f"  👤  Customer  : {booking['customer_name']}")
    print(f"  🚗  Vehicle   : {vehicle['year']} {vehicle['make']} {vehicle['model']}")
    print(f"  🪪  Plate     : {vehicle['plate']}")
    print(f"  📅  Trip      : {booking['pickup_date']}  →  {booking['return_date']}")

    # ── Step 2: Damage description input ──────────────────────────────────
    section("Step 2 — Describe the Damage")
    wrap_print(
        "Please describe the damage you've noticed as clearly as possible "
        "(e.g. 'crack on windshield', 'dent on rear door')."
    )
    print()

    while True:
        reported = input("  Your description: ").strip()

        # Messy edge: blank description
        if not reported:
            print()
            wrap_print(
                "Description cannot be empty. Please describe what you see."
            )
            print()
            continue

        # Messy edge: suspiciously short input (likely accidental keypress)
        if len(reported) < 5:
            print()
            wrap_print(
                "That description seems too short. Could you provide a bit "
                "more detail so we can look it up accurately?"
            )
            print()
            continue

        break  # Acceptable description received

    # ── Step 3: Match & respond ───────────────────────────────────────────
    matched = match_damage(reported, vehicle["pre_existing_damage"])

    if matched:
        handle_known_damage(booking, vehicle, matched)
    else:
        handle_new_damage(booking, vehicle, reported)

    # Footer
    print()
    divider("═")
    print("  1Now GuardRail  |  Prototype v1.0  |  Support Automation")
    divider("═")
    print()


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Catch keyboard interrupts (Ctrl+C) gracefully so the terminal isn't
    # left in a broken state if the user force-quits mid-session.
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        wrap_print("Session interrupted. Goodbye! 👋")
        print()
