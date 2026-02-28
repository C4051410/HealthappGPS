import math
import flet as ft
import flet_map as ftm
from flet_geolocator import Geolocator


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(
        dlon / 2) ** 2)
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def main(page: ft.Page):
    page.title = "Health App GPS"
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- State Variables ---
    path_points = []
    total_dist = 0.0
    is_tracking = False

    # ==========================================
    # 1. MAP VIEW COMPONENTS (The Tracking Screen)
    # ==========================================
    distance_value = ft.Text(value="0.00", size=48, weight=ft.FontWeight.BOLD)
    distance_label = ft.Text(value="KILOMETERS", size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD)

    marker_layer = ftm.MarkerLayer(markers=[])
    polyline_layer = ftm.PolylineLayer(
        polylines=[ftm.PolylineMarker(coordinates=[], color=ft.Colors.DEEP_ORANGE, stroke_width=4)]
    )

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

    # Tracking Logic
    def on_position_change(e):
        nonlocal total_dist, is_tracking
        new_loc = ftm.MapLatitudeLongitude(e.position.latitude, e.position.longitude)

        marker_layer.markers.clear()
        marker_layer.markers.append(
            ftm.Marker(content=ft.Icon(ft.Icons.MY_LOCATION, color=ft.Colors.BLUE, size=30), coordinates=new_loc)
        )
        map_ctrl.center = new_loc

        if is_tracking:
            if path_points:
                prev = path_points[-1]
                total_dist += calculate_distance(prev.latitude, prev.longitude, new_loc.latitude, new_loc.longitude)

            path_points.append(new_loc)
            distance_value.value = f"{total_dist:.2f}"

            if len(path_points) > 1:
                polyline_layer.polylines[0].coordinates = list(path_points)

        page.update()

    # Initialize Geolocator in the background overlay
    gl = Geolocator(on_position_change=on_position_change)
    page.overlay.append(gl)

    # Tracking Buttons
    async def start_tracking(e):
        nonlocal is_tracking
        status = await gl.get_permission_status()
        if "denied" in str(status).lower():
            await gl.request_permission()

        is_tracking = True
        start_btn.visible = False
        pause_row.visible = True
        page.update()

        try:
            await gl.get_current_position()
        except Exception as err:
            print(f"GPS Searching: {err}")

    def pause_tracking(e):
        nonlocal is_tracking
        is_tracking = False
        pause_row.visible = False
        start_btn.visible = True
        start_btn.content = ft.Text("RESUME", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        start_btn.icon = ft.Icons.PLAY_ARROW
        page.update()

    def stop_tracking(e):
        nonlocal is_tracking, total_dist
        is_tracking = False
        path_points.clear()
        total_dist = 0.0
        distance_value.value = "0.00"
        if polyline_layer.polylines:
            polyline_layer.polylines[0].coordinates.clear()

        pause_row.visible = False
        start_btn.visible = True
        start_btn.content = ft.Text("START", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
        start_btn.icon = ft.Icons.FIBER_MANUAL_RECORD
        page.update()

    start_btn = ft.FloatingActionButton(
        content=ft.Text("START", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        icon=ft.Icons.FIBER_MANUAL_RECORD, bgcolor=ft.Colors.DEEP_ORANGE, width=150, on_click=start_tracking
    )
    pause_btn = ft.FloatingActionButton(icon=ft.Icons.PAUSE, bgcolor=ft.Colors.GREY_300, on_click=pause_tracking)
    stop_btn = ft.FloatingActionButton(icon=ft.Icons.STOP, bgcolor=ft.Colors.RED_400, on_click=stop_tracking)

    pause_row = ft.Row(controls=[pause_btn, stop_btn], alignment=ft.MainAxisAlignment.CENTER, visible=False, spacing=20)

    map_dashboard = ft.Container(
        content=ft.Column(
            controls=[
                ft.Column([distance_label, distance_value], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                          spacing=0),
                start_btn,
                pause_row
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.BorderRadius(top_left=30, top_right=30, bottom_left=0, bottom_right=0),
        padding=30,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK26)
    )

    map_view_stack = ft.Stack(
        controls=[
            map_ctrl,
            ft.Container(content=map_dashboard, alignment=ft.Alignment.BOTTOM_CENTER, bottom=0, left=0, right=0)
        ],
        expand=True
    )

    # ==========================================
    # 2. HOME VIEW COMPONENTS (The Dashboard)
    # ==========================================

    async def go_map(e):
        await page.push_route("/map")

    home_content = ft.Container(
        padding=20,
        expand=True,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # Profile Header
                ft.Row(
                    controls=[
                        ft.CircleAvatar(foreground_image_src="https://ui-avatars.com/api/?name=User&background=random"),
                        ft.Text("Good Morning, Runner!", size=20, weight=ft.FontWeight.BOLD)
                    ],
                    alignment=ft.MainAxisAlignment.START
                ),
                ft.Divider(height=30),

                # Stats Card
                ft.Container(
                    bgcolor=ft.Colors.GREY_100,
                    padding=20,
                    border_radius=15,
                    content=ft.Column([
                        ft.Text("THIS WEEK", size=12, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                        ft.Text("14.2 km", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.DEEP_ORANGE),
                        ft.Text("3 Activities", size=14, color=ft.Colors.GREY_500)
                    ])
                ),
                ft.Divider(height=40, color=ft.Colors.TRANSPARENT),

                # BIG Record Button
                ft.Button(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.ADD_LOCATION_ALT, color=ft.Colors.WHITE),
                         ft.Text("RECORD ACTIVITY", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    bgcolor=ft.Colors.DEEP_ORANGE,
                    width=300,
                    height=60,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=30)),
                    on_click=go_map
                )
            ]
        )
    )

    # ==========================================
    # 3. ROUTING LOGIC (Switching Screens)
    # ==========================================
    def route_change(e):
        page.views.clear()

        # Always build the Home View first
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(title=ft.Text("HealthTracker", weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.WHITE),
                    home_content
                ],
                bgcolor=ft.Colors.WHITE
            )
        )

        # If the user clicks Record, layer the Map View on top
        if page.route == "/map":
            page.views.append(
                ft.View(
                    route="/map",
                    controls=[
                        # FIX: Changed icon_color to color for universal icon/text styling in Flet 1.0
                        ft.AppBar(title=ft.Text("Recording", color=ft.Colors.WHITE), bgcolor=ft.Colors.DEEP_ORANGE,
                                  color=ft.Colors.WHITE),
                        map_view_stack
                    ],
                    padding=0
                )
            )
        page.update()

    async def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.route = "/"
    route_change(None)


if __name__ == "__main__":
    try:
        ft.run(main)
    except AttributeError:
        ft.app(main)