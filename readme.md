# PedalSafe Route Planner

- A web-application that allows user to compute the safest NYC cycling route between two locations, by triaging bicycles lanes with the highest level of protection
- Program converts a geojson road network of NYC into a directed NetworkX graph, and uses Dijkstra's algorithm to compute the shortest path, given bicycle lane attribute as weight
- Use of GoogleMaps API to for address geocoding, and derivative time to travel route
