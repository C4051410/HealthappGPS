import math
import flet as ft
import flet_map as ftm


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the distance between two coordinates in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
        dlon / 2) ** 2)
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def main(page: ft.Page):
    page.title = "Desktop Click Tracker"
    page.padding = 20

    path_points = []
    total_distance = 0.0

    # UI Elements
    distance_text = ft.Text(value="Distance: 0.00 km", size=24, weight=ft.FontWeight.BOLD)

    # Map Layers
    marker_layer = ftm.MarkerLayer(markers=[])
    polyline_layer = ftm.PolylineLayer(polylines=[])

    def handle_map_click(e: ftm.MapTapEvent):
        nonlocal total_distance
        new_coord = e.coordinates

        # Calculate distance if we have a previous point
        if path_points:
            prev = path_points[-1]
            dist = calculate_distance(prev.latitude, prev.longitude, new_coord.latitude, new_coord.longitude)
            total_distance += dist
            distance_text.value = f"Distance: {total_distance:.2f} km"

            # Draw or update the connecting line
            if not polyline_layer.polylines:
                polyline_layer.polylines.append(
                    ftm.PolylineMarker(coordinates=list(path_points) + [new_coord], color=ft.Colors.BLUE,
                                       border_stroke_width=4)
                )
            else:
                polyline_layer.polylines[0].coordinates = list(path_points) + [new_coord]

        # Save point and drop a marker
        path_points.append(new_coord)
        marker_layer.markers.append(
            ftm.Marker(content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.RED, size=30), coordinates=new_coord)
        )
        page.update()

    def reset_map(e):
        """Clears all points and resets distance to zero."""
        nonlocal total_distance
        path_points.clear()
        total_distance = 0.0
        distance_text.value = "Distance: 0.00 km"
        marker_layer.markers.clear()
        polyline_layer.polylines.clear()
        page.update()

    # The interactive map
    map_ctrl = ftm.Map(
        expand=True,
        initial_center=ftm.MapLatitudeLongitude(54.9783, -1.6178),  # Newcastle upon Tyne
        initial_zoom=14,
        on_tap=handle_map_click,
        layers=[
            ftm.TileLayer(url_template="https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"),
            polyline_layer,
            marker_layer,
        ]
    )

    # Top bar with text and reset button
    # FIX: Removed the 'text=' keyword argument to prevent the crash
    header = ft.Row(
        controls=[
            distance_text,
            ft.ElevatedButton("Reset Route", on_click=reset_map, icon=ft.Icons.RESTART_ALT)
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Add everything to the window
    page.add(
        header,
        ft.Container(content=map_ctrl, expand=True, border_radius=10)
    )


# Run as a standard desktop app
if __name__ == "__main__":
    ft.app(main)