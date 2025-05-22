import pandas as pd
from pyDatalog import pyDatalog

def create_mappings():
    # Read and merge trip data (stop_times.txt and trips.txt)
    df_trips = pd.merge(
        pd.read_csv('stop_times.txt'),
        pd.read_csv('trips.txt'),
        on='trip_id'
    )[['trip_id', 'route_id', 'stop_id', 'stop_sequence']]
    # Read and merge fare data (fare_rules.txt and fare_attributes.txt)
    df_fare_rules = pd.read_csv('fare_rules.txt')
    df_fare_attributes = pd.read_csv('fare_attributes.txt')
    # Convert numeric fields in fare rules
    df_fare_rules['route_id'] = df_fare_rules['route_id'].astype(int)
    df_fare_rules['origin_id'] = df_fare_rules['origin_id'].astype(int)
    df_fare_rules['destination_id'] = df_fare_rules['destination_id'].astype(int)
    # Convert price in fare attributes to float
    df_fare_attributes['price'] = df_fare_attributes['price'].astype(float)
    # Merge fare data on fare_id
    df_fares = pd.merge(df_fare_rules, df_fare_attributes, on='fare_id')
    
    # Create route_to_stops dictionary with ordered stops
    route_to_stops = {}
    for route, group in df_trips.groupby('route_id'):
        # Sort by stop_sequence and extract stop_id list
        stops = group.sort_values('stop_sequence')['stop_id'].tolist()
        # Remove duplicates while preserving order
        seen = set()
        ordered_stops = []
        for stop in stops:
            if stop not in seen:
                ordered_stops.append(stop)
                seen.add(stop)
        route_to_stops[int(route)] = ordered_stops

    # Create fares dictionary
    fares = {}
    for idx, row in df_fares.iterrows():
        key = (int(row['route_id']), int(row['origin_id']), int(row['destination_id']))
        fares[key] = float(row['price'])
    return route_to_stops, fares

def setup_datalog(route_to_stops, fares):
    # Add facts for routes and stops
    for route, stops in route_to_stops.items():
        for stop in stops:
            +RouteHasStop(route, stop)
    
    # Add facts for fares
    for (route, origin, dest), price in fares.items():
        +TripFare(route, origin, dest, price)

def define_rules():
    # Implement DirectRoute rule
    DirectRoute(X, Y, R, P) <= (RouteHasStop(R, X)) & (RouteHasStop(R, Y)) & (TripFare(R, X, Y, P))
    # Implement Transfer1Route rule (1-transfer via intermediate stop Z with different routes)
    Transfer1Route(X, Y, R1, Z, R2, P) <= (DirectRoute(X, Z, R1, P1) & DirectRoute(Z, Y, R2, P2) & (P == P1 + P2) & (R1 != R2))
    # Implement Transfer2Route rule (2-transfer via stops Z1 and Z2 with all routes different)
    Transfer2Route(X, Y, R1, Z1, R2, Z2, R3, P) <= (
        DirectRoute(X, Z1, R1, P1) &
        DirectRoute(Z1, Z2, R2, P2) &
        DirectRoute(Z2, Y, R3, P3) &
        (P == P1 + P2 + P3) &
        (R1 != R2) & (R1 != R3) & (R2 != R3)
    )
    # Implement AvoidStopRoute rule (direct route that does not include AvoidStop)
    AvoidStopRoute(X, Y, AvoidStop, R, P) <= (DirectRoute(X, Y, R, P)) & ~(RouteHasStop(R, AvoidStop))

def query_routes(start_stop, end_stop, avoid_stop=None):
    results = {'direct_routes': [],'one_transfer': [],'two_transfer': [],'avoid_stop': []}
    # Query for direct routes and return at most 5 results sorted by fare (ascending)
    direct_q = DirectRoute(start_stop, end_stop, R, P)
    direct_list = [(int(r), float(p)) for r, p in direct_q]
    results['direct_routes'] = sorted(set(direct_list), key=lambda x: x[1])[:5]
    # Query for 1-transfer routes and return at most 5 results sorted by total fare
    one_transfer_q = Transfer1Route(start_stop, end_stop, R1, Z, R2, P)
    one_transfer_list = [(int(r1), int(z), int(r2), float(p)) for r1, z, r2, p in one_transfer_q]
    results['one_transfer'] = sorted(set(one_transfer_list), key=lambda x: x[3])[:5]
    # Query for 2-transfer routes and return at most 5 results sorted by total fare
    two_transfer_q = Transfer2Route(start_stop, end_stop, R1, Z1, R2, Z2, R3, P)
    two_transfer_list = [(int(r1), int(z1), int(r2), int(z2), int(r3), float(p)) for r1, z1, r2, z2, r3, p in two_transfer_q]
    results['two_transfer'] = sorted(set(two_transfer_list), key=lambda x: x[5])[:5]
    # Query for avoid-stop routes if avoid_stop is provided; return at most 5 sorted by fare
    if avoid_stop is not None:
        avoid_q = AvoidStopRoute(start_stop, end_stop, avoid_stop, R, P)
        avoid_list = [(int(r), float(p)) for r, p in avoid_q]
        results['avoid_stop'] = sorted(set(avoid_list), key=lambda x: x[1])[:5]
    return results

def main():
    # Create data mappings
    route_to_stops, fares = create_mappings()
    # Setup pyDatalog
    setup_datalog(route_to_stops, fares)
    # Define rules
    define_rules()
    # Example usage
    results = query_routes(146, 148, avoid_stop=233)
    # Print results
    print("Direct routes:", results['direct_routes'])
    print("1-transfer:", results['one_transfer'])
    print("2-transfer:", results['two_transfer'])
    print("Avoid Stop:", results['avoid_stop'])

if __name__ == "__main__":
    # Initialize pyDatalog
    pyDatalog.clear() 
    # Define terms
    pyDatalog.create_terms('RouteHasStop, TripFare, DirectRoute, Transfer1Route, '
        'Transfer2Route, AvoidStopRoute, X, Y, Z, Z1, Z2, R, R1, R2, R3, P, P1, P2, P3, AvoidStop')
    main()