# Delhi Metro Route Planner using pyDatalog

This project implements a route planning system for the Delhi Metro using pyDatalog and GTFS (General Transit Feed Specification) data. It enables efficient route discovery, transfer analysis, and fare calculation using logic programming principles.

## 📁 Dataset

The project uses 5 standard GTFS files:
- `routes.txt`: Route metadata
- `trips.txt`: Trip-to-route mappings
- `stop_times.txt`: Ordered stops for each trip
- `stops.txt`: Stop metadata
- `fare_rules.txt`: Fare details for each route

## 🛠️ Features

- Create mappings from route IDs to ordered stop IDs.
- Build a fare dictionary mapping each `(route_id, origin_id, destination_id)` to price.
- Define a logic-based knowledge base using pyDatalog.
- Implement queryable rules to:
  - Find **direct routes** between stops.
  - Discover **1-transfer** and **2-transfer** route options.
  - Identify direct routes that **avoid a specific stop**.
- Results are:
  - Sorted by **fare in ascending order**.
  - Limited to **at most 5 results per category**.

## ⚙️ Technologies Used

- Python 3
- [pyDatalog](https://sites.google.com/site/pydatalog/)
- Pandas (for GTFS preprocessing)

## 📌 Evaluation Criteria

- Data preparation: route-to-stops mapping and fare dictionary.
- pyDatalog knowledge base and fact loading.
- Correct and optimized rule definitions for route discovery.
- Accurate query results in required format and constraints.

## 📂 File Structure

├── data/
│ ├── routes.txt
│ ├── trips.txt
│ ├── stop_times.txt
│ ├── stops.txt
│ └── fare_rules.txt
├── route_planner.py