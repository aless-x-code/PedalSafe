# PedalSafe Route Planner

- A web-application that allows user to compute the safest NYC cycling route between two locations, by triaging bicycles lanes with the highest level of protection
- Program converts a geojson road network of NYC into a directed NetworkX graph, and uses Dijkstra's algorithm to compute the shortest path, given bicycle lane attribute as weight
- Use of GoogleMaps API to for address geocoding, and derivative time to travel route

## Demo
!(Demo picture)[https://64.media.tumblr.com/32952fdbdcfab15dd4f910aec4f8b2dd/c8365ffbc0af5e48-37/s2048x3072/8c771aa5621a30c80c7c3ad4e2d0ef151901b1c8.pnj]