import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from launcher import Launcher

    result = Launcher().run()

    if result is None:
        return

    if result == "subway_kb":
        from game.runner import Game
        Game(use_camera=False).run()

    elif result == "subway_cam":
        from game.runner import Game
        Game(use_camera=True).run()

    elif result == "dino_kb":
        from dino.dino_game import DinoGameLocal
        DinoGameLocal(use_camera=False).run()

    elif result == "dino_cam":
        from dino.dino_game import DinoGameLocal
        DinoGameLocal(use_camera=True).run()

    elif result == "online":
        from camera_controller import run_external_controller
        run_external_controller()


if __name__ == "__main__":
    main()
