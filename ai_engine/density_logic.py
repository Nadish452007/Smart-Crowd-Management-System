def get_density_level(count):

    levels = [
        (3, "SAFE", (0,255,0)),
        (7, "MEDIUM", (0,255,255)),
        (12, "HIGH", (0,165,255)),
        (999, "DANGER", (0,0,255))
    ]

    for limit, label, color in levels:
        if count <= limit:
            return label, color

