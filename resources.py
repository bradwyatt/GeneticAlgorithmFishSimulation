from pathlib import Path

import pygame


IMAGE_SPECS = {
    "spr_wall": ("Sprites/wall.bmp", True, False),
    "spr_redfish": ("Sprites/redfish.png", True, True),
    "spr_redfishleft": ("Sprites/redfishleft.png", True, True),
    "spr_eliteclone": ("Sprites/eliteclone.png", True, True),
    "spr_elitecloneleft": ("Sprites/elitecloneleft.png", True, True),
    "spr_arc": ("Sprites/arc.png", True, True),
    "spr_arcleft": ("Sprites/arcleft.png", True, True),
    "spr_shark": ("Sprites/shark.png", True, True),
    "spr_seaweed": ("Sprites/Seaweed.png", True, True),
}


def find_asset_path(relative_path: str) -> str:
    path = Path(relative_path)
    if path.exists():
        return str(path)

    parent = path.parent
    if not parent.exists():
        return str(path)

    target_name = path.name.lower()
    for candidate in parent.iterdir():
        if candidate.name.lower() == target_name:
            return str(candidate)

    return str(path)


def load_image(file_path, transparent, alpha):
    new_image = pygame.image.load(find_asset_path(file_path))
    new_image = new_image.convert_alpha() if alpha else new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0, 0))
        new_image.set_colorkey(colorkey, pygame.RLEACCEL)
    return new_image


def load_images():
    return {
        name: load_image(file_path, transparent, alpha)
        for name, (file_path, transparent, alpha) in IMAGE_SPECS.items()
    }
