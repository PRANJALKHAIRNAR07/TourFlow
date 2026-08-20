from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = os.path.join("data", "destinations.json")


def load_destinations():
    """Load destination data from JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_crowd(destination, date, time_slot):
    """
    Estimate crowd based on destination capacity,
    historical demand and selected time slot.
    """

    base_demand = destination["time_slots"].get(time_slot, 0)
    capacity = destination["capacity"]

    # Simple scheduling logic for MVP
    expected_visitors = base_demand

    if expected_visitors >= capacity:
        status = "Overcrowded"
        level = "high"
    elif expected_visitors >= capacity * 0.75:
        status = "Busy"
        level = "medium"
    else:
        status = "Comfortable"
        level = "low"

    utilization = round((expected_visitors / capacity) * 100, 2)

    return {
        "expected_visitors": expected_visitors,
        "capacity": capacity,
        "utilization": utilization,
        "status": status,
        "level": level
    }


def recommend_slots(destination, date):
    """
    Find suitable time slots based on expected crowd.
    """

    recommendations = []

    for time_slot, demand in destination["time_slots"].items():

        capacity = destination["capacity"]

        utilization = (demand / capacity) * 100

        if utilization <= 60:
            category = "Recommended"
            score = 3
        elif utilization <= 80:
            category = "Possible"
            score = 2
        else:
            category = "Avoid"
            score = 1

        recommendations.append({
            "time": time_slot,
            "expected_visitors": demand,
            "capacity": capacity,
            "utilization": round(utilization, 2),
            "category": category,
            "score": score
        })

    recommendations.sort(
        key=lambda x: (-x["score"], x["expected_visitors"])
    )

    return recommendations


@app.route("/")
def home():
    destinations = load_destinations()
    return render_template(
        "index.html",
        destinations=destinations
    )


@app.route("/dashboard")
def dashboard():
    destinations = load_destinations()

    dashboard_data = []

    for destination in destinations:

        peak_slot = max(
            destination["time_slots"],
            key=destination["time_slots"].get
        )

        peak_visitors = destination["time_slots"][peak_slot]

        dashboard_data.append({
            "name": destination["name"],
            "capacity": destination["capacity"],
            "peak_slot": peak_slot,
            "peak_visitors": peak_visitors,
            "peak_utilization": round(
                (peak_visitors / destination["capacity"]) * 100,
                2
            )
        })

    return render_template(
        "dashboard.html",
        destinations=dashboard_data
    )


@app.route("/api/destinations")
def api_destinations():
    return jsonify(load_destinations())


@app.route("/api/recommend", methods=["POST"])
def recommend():

    data = request.get_json()

    destination_id = data.get("destination_id")
    date = data.get("date")
    preferred_time = data.get("preferred_time")

    if not destination_id or not date:
        return jsonify({
            "success": False,
            "message": "Destination and date are required."
        }), 400

    destinations = load_destinations()

    destination = next(
        (
            item for item in destinations
            if item["id"] == int(destination_id)
        ),
        None
    )

    if destination is None:
        return jsonify({
            "success": False,
            "message": "Destination not found."
        }), 404

    recommendations = recommend_slots(
        destination,
        date
    )

    preferred_result = None

    if preferred_time:
        preferred_result = calculate_crowd(
            destination,
            date,
            preferred_time
        )

    best_slot = recommendations[0]

    return jsonify({
        "success": True,
        "destination": destination["name"],
        "date": date,
        "preferred_time": preferred_time,
        "preferred_result": preferred_result,
        "recommended_slot": best_slot,
        "all_slots": recommendations
    })


@app.route("/api/book", methods=["POST"])
def book():

    data = request.get_json()

    destination = data.get("destination")
    date = data.get("date")
    time_slot = data.get("time_slot")
    visitor_name = data.get("visitor_name")

    if not destination or not date or not time_slot or not visitor_name:
        return jsonify({
            "success": False,
            "message": "All booking details are required."
        }), 400

    pass_id = (
        "TF-"
        + datetime.now().strftime("%Y%m%d%H%M%S")
    )

    return jsonify({
        "success": True,
        "message": "Tourist slot reserved successfully.",
        "pass_id": pass_id,
        "visitor_name": visitor_name,
        "destination": destination,
        "date": date,
        "time_slot": time_slot
    })


if __name__ == "__main__":
    app.run(debug=True)
