def update():
    global window
    window = get_window()

    if input_manager.get_key_down(pygame.K_ESCAPE):
        window.running = False

    window.SURFACE.fill(BLACK.tup())

    # Draw predicted orbits
    draw_orbits()

    # Update and render bodies
    for body in bodies:
        body.update(bodies, window.delta_time)
        body.render()

    set_window(window)