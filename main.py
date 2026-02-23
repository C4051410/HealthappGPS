import math
import flet as ft
import flet_map as ftm
from flet_geolocator import Geolocator, GeolocatorPosition


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in km
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def main(page: ft.Page):
    page.title = "Live GPS Tracker"

    path_points = []
    total_dist = 0.0

    distance_text = ft.Text("Distance: 0.00 km", size=20, weight="bold")

    def on_position_change(e: GeolocatorPosition):
        nonlocal total_dist
        new_loc = ftm.MapLatitudeLongitude(e.latitude, e.longitude)

        if path_points:
            prev = path_points[-1]
            total_dist += calculate_distance(prev.latitude, prev.longitude, new_loc.latitude, new_loc.longitude)

        path_points.append(new_loc)
        distance_text.value = f"Distance: {total_dist:.2f} km"

        # Update markers and path
        marker_layer.markers.append(
            ftm.Marker(content=ft.Icon(ft.Icons.LOCATION_PIN, color="blue"), coordinates=new_loc))
        if len(path_points) > 1:
            polyline_layer.polylines[0].coordinates = list(path_points)

        map_ctrl.center = new_loc
        page.update()

    # Note the change here: 'Geolocator' instead of 'FletGeolocator'
    gl = Geolocator(on_position_change=on_position_change)
    page.overlay.append(gl)

    marker_layer = ftm.MarkerLayer(markers=[])
    polyline_layer = ftm.PolylineLayer(polylines=[ftm.PolylineMarker(coordinates=[], color="blue", stroke_width=3)])

    map_ctrl = ftm.Map(
        expand=True,
        initial_center=ftm.MapLatitudeLongitude(54.9783, -1.6178),
        initial_zoom=16,
        layers=[
            ftm.TileLayer(url_template="https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"),
            polyline_layer,
            marker_layer,
        ]
    )

    page.add(
        ft.Row([distance_text, ft.ElevatedButton("Start Live Tracking", on_click=lambda _: gl.get_current_position())],
               alignment="spaceBetween"),
        ft.Container(map_ctrl, expand=True)
    )


ft.app(main)
