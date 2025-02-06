import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from pg_extensions import *
import tkinter as tk


class Settings:
    G = 0.001

    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()


class Body:
    def __init__(self, position, velocity, radius, mass, color):
        self.position = position
        self.velocity = velocity
        self.total_force = Vector2()
        self.radius = radius
        self.mass = mass
        self.color = color

    def update(self, bodies):
        self.total_force = Vector2()

        for body in bodies:
            if body == self:
                continue

            distance_vector = body.position - self.position
            distance_squared = distance_vector.sqr_magnitude()

            if distance_squared == 0:
                continue  # Prevent division by zero

            force_magnitude = Settings.G * self.mass * body.mass / distance_squared
            force_direction = distance_vector.normalize()
            self.total_force += force_direction * force_magnitude

        # Update velocity using the accumulated force
        self.velocity += self.total_force * window.delta_time / self.mass
        self.position += self.velocity * window.delta_time

    def render(self):
        draw_circle(window.SURFACE, self.color, self.position, self.radius)
        draw_line(
            window.SURFACE,
            WHITE,
            self.position,
            self.position + self.velocity,
            2,
        )


def start():
    global bodies
    bodies = []

    m1, m2 = 10000000, 10000000
    r = 50  # Initial separation

    v = (Settings.G * (m1 + m2) / r) ** 0.5  # Orbital velocity formula
    print(f"Orbital Velocity: {v}")

    bodies.append(Body(Vector2(-r, 0), Vector2(0, v), 10, m1, GREEN))
    bodies.append(Body(Vector2(r, 0), Vector2(0, -v), 10, m2, BLUE))


def update():
    global window
    window = get_window()

    if input_manager.get_key_down(pygame.K_ESCAPE):
        window.running = False

    window.SURFACE.fill(BLACK.tup())

    for body in bodies:
        body.update(bodies)

    for body in bodies:
        body.render()

    set_window(window)


if __name__ == "__main__":
    print("Width:", Settings.width, "Height:", Settings.height)
    run(start, update, Settings.width, Settings.height, False, "Celestial Body Simulation", 999)
