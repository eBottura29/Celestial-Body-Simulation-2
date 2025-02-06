import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pg_extensions import *
import tkinter as tk
import copy  # To clone objects for simulation


class Settings:
    G = 0.001

    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    PREDICTION_STEPS = 5000  # How far to predict
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
        draw_line(
            window.SURFACE,
            WHITE,
            self.position,
            self.position + self.velocity,
            2,
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

    m1, m2 = 10000000, 20000000
    r = 200  # Initial separation

    v = (Settings.G * (m1 + m2) / r) ** 0.5  # Orbital velocity formula
    print(f"Orbital Velocity: {v}")

    body1 = Body(Vector2(-r // 2, 0), Vector2(0, v / 2), 10, m1, GREEN)
    body2 = Body(Vector2(r // 2, 0), Vector2(0, -v / 2), 10, m2, BLUE)

    bodies.append(body1)
    bodies.append(body2)


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

    set_window(window)


if __name__ == "__main__":
    print("Width:", Settings.width, "Height:", Settings.height)
    run(start, update, Settings.width, Settings.height, False, "Celestial Body Simulation", 999)
