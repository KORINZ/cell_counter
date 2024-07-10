import sys
import os
import re
from PIL import Image, ImageDraw, ImageFont


def add_figure_letter(image_path: str, fig_arg: str, scale: float = 1.0) -> None:
    """Add a letter to a figure image."""

    # Parse the figure argument
    match = re.match(r"(-|[0-9]+)([a-zA-Z])", fig_arg)
    if not match:
        print("Figure argument must be in the format 'number+letter' or '-letter'.")
        sys.exit(1)

    fig_number, letter = match.groups()
    letter = letter.lower()

    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font_size = int(190 * scale)
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", font_size)
    square_size = int(200 * scale)
    square_position = (int(40 * scale), int(40 * scale))

    letter_box = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
    letter_box_draw = ImageDraw.Draw(letter_box)

    letter_box_draw.rectangle(
        ((0, 0), (square_size, square_size)),
        fill="black",
    )

    if letter == "f" or letter == "i":
        letter_position = (
            0.5 * square_size - 0.155 * font_size,
            0.5 * square_size - 0.60 * font_size,
        )
    elif letter == "g":
        letter_position = (
            0.5 * square_size - 0.275 * font_size,
            0.5 * square_size - 0.75 * font_size,
        )
    else:
        letter_position = (
            0.5 * square_size - 0.275 * font_size,
            0.5 * square_size - 0.60 * font_size,
        )
    letter_box_draw.text(letter_position, letter, font=font, fill="white")

    image.paste(letter_box, square_position, letter_box)

    if fig_number == "-":
        output_path = image_path
    else:
        original_path_folder, _ = os.path.split(image_path)
        output_path = f"{original_path_folder}/fig_{fig_number}{letter}.png".replace(
            "\\", "/"
        )
    image.save(output_path)
    print(f"Output saved as {output_path}")


if __name__ == "__main__":
    if len(sys.argv) not in [3, 4]:
        print("Usage: python3 add_fig_letter.py <image_path> <figure_argument> [scale]")
        print("Figure argument should be in the format '4a' or '-a'")
        sys.exit(1)
    image_path = sys.argv[1]
    fig_arg = sys.argv[2]
    scale = float(sys.argv[3]) if len(sys.argv) == 4 else 1.0
    add_figure_letter(image_path, fig_arg, scale)
