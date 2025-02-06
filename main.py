import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pg_extensions import *
import tkinter as tk
import copy  # To clone objects for simulation


class Settings:
    G = 1

    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    PREDICTION_STEPS = 100  # How far to predict
    TIME_STEP = 0.1  # Time step for prediction


def draw_polyline(surface, color, points, width=1):
    """Draws a continuous line through multiple points (polyline)."""
    if len(points) > 1:  # Only draw if there are at least two points
        pygame.draw.lines(
            surface,
            color.tup(),
            False,
            [(p.x + window.WIDTH // 2, -p.y + window.HEIGHT // 2) for p in points],
            width,
        )


class Body:
    def __init__(self, position, velocity, radius, mass, color):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.mass = mass
        self.color = color
        self.orbit_path = []  # Stores predicted positions

    def update(self, bodies, delta_time):
        total_force = Vector2()

        for body in bodies:
            if body == self:
                continue

            distance_vector = body.position - self.position
            distance_squared = distance_vector.sqr_magnitude()

            if distance_squared == 0:
                continue  # Prevent division by zero

            force_magnitude = Settings.G * self.mass * body.mass / distance_squared
            force_direction = distance_vector.normalize()
            total_force += force_direction * force_magnitude

        # Update velocity and position using the accumulated force
        self.velocity += total_force * delta_time / self.mass
        self.position += self.velocity * delta_time

    def render(self):
        draw_circle(window.SURFACE, self.color, self.position, self.radius)

        # Velocity Line
        draw_line(
            window.SURFACE,
            WHITE,
            self.position,
            self.position + self.velocity,
            2,
        )

        # Velocity Line Tip
        norm = self.velocity.normalize()
        mag = self.velocity.magnitude()
        direction = math.atan2(self.velocity.y, self.velocity.x)
        tip_size = 10

        theta = math.atan2(tip_size, mag)
        dst = tip_size / math.sin(theta)
        direction_l = Vector2(math.cos(direction + theta), math.sin(direction + theta)).normalize()
        direction_r = Vector2(math.cos(direction - theta), math.sin(direction - theta)).normalize()

        draw_line(
            window.SURFACE, WHITE, self.position + direction_l * dst, self.position + direction_r * dst, 2
        )

    def predict_orbit(self, bodies):
        # Create deep copies of all bodies
        temp_bodies = copy.deepcopy(bodies)
        for b in temp_bodies:
            if b.position == self.position and b.velocity == self.velocity:
                temp_self = b
                break
        else:
            raise ValueError("Could not find matching body in temp_bodies")

        predicted_positions = []

        for _ in range(Settings.PREDICTION_STEPS):
            temp_self.update(temp_bodies, Settings.TIME_STEP)
            predicted_positions.append(Vector2(temp_self.position.x, temp_self.position.y))

        self.orbit_path = predicted_positions


def start():
    global bodies
    bodies = []

    scale_factor = 260.87

    mass = scale_factor * 10**3

    positions = [
        Vector2(-0.97000436, 0.24308753) * scale_factor,
        Vector2(0.97000436, -0.24308753) * scale_factor,
        Vector2(0, 0) * scale_factor,
    ]

    velocities = [
        Vector2(0.46620368, 0.43236573) * scale_factor**0.5,
        Vector2(0.46620368, 0.43236573) * scale_factor**0.5,
        Vector2(-0.93240737, -0.86473146) * scale_factor**0.5,
    ]

    colors = [RED, GREEN, BLUE]

    for i in range(3):
        bodies.append(Body(positions[i], velocities[i], 10, mass, colors[i]))


def draw_orbits():
    for body in bodies:
        if len(body.orbit_path) > 1:
            draw_polyline(window.SURFACE, WHITE, body.orbit_path, 1)  # Draw predicted orbit lines


def compute_barycenter(bodies):
    total_mass = sum(body.mass for body in bodies)

    if total_mass == 0:
        return Vector2(0, 0)  # Avoid division by zero

    barycenter = sum((body.position * body.mass for body in bodies), Vector2()) / total_mass
    return barycenter


def update():
    global window
    window = get_window()

    if input_manager.get_key_down(pygame.K_ESCAPE):
        window.running = False

    window.SURFACE.fill(BLACK.tup())

    # Predict orbits for all bodies
    for body in bodies:
        body.predict_orbit(bodies)

    # Draw predicted orbits
    draw_orbits()

    # Compute and draw barycenter
    barycenter = compute_barycenter(bodies)
    draw_circle(window.SURFACE, WHITE, barycenter, 5)  # Small white dot at barycenter

    # Update and render bodies
    for body in bodies:
        body.update(bodies, window.delta_time)
        body.render()

    fps_text = Text(
        f"FPS: {window.clock.get_fps():.2f}", Text.arial_32, Vector2(32, 32), Text.top_left, WHITE
    )
    fps_text.render()

    set_window(window)


if __name__ == "__main__":
    print("Width:", Settings.width, "Height:", Settings.height)
    run(start, update, Settings.width, Settings.height, False, "Celestial Body Simulation", 99999)
