import argparse
from gui import drawing
import os

parser = argparse.ArgumentParser()
parser.add_argument("image_path", nargs='?',
                    default="images/example.jpg", help="Path to image")
parser.add_argument("scribble_path", nargs='?',
                    default="", help="Optional path to scribble")


def main(args):
    """
    Runs the application
    """
    if not os.path.exists(args.image_path):
        print(f'{args.image_path} is not a valid image path')
    
    elif not os.path.exists(args.scribble_path) and args.scribble_path != "":
        print(f'{args.scribble_path} is not a valid scribble path')
    
    else:
        ui = drawing.Interface(image_path=args.image_path, name="Colorization App",
                               bar_h=150, min_bar_w=512, frame_size=10,
                               scribble_path=args.scribble_path)
        ui.run()

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)