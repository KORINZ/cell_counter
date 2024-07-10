from PIL import ImageFont, ImageDraw, Image
import cv2
import numpy as np
import argparse
import os
import glob

# Olympus CM30 Incubation Monitoring System
DISPLAY_SCALE_NUMBER = True

# Constants from the calibration of the scopes
scale_pixel_200_um = 90

scale_bar_location_x_offset = 30
scale_bar_location_y_offset = 45
scale_bar_font_size = 30
text_position_y_offset = 40
scale_bar_thickness = 15
scale_bar_color = (255, 255, 255)


def process_directory(directory_path) -> None:
    """Process all .png images in the given directory."""
    for image_file in glob.glob(os.path.join(directory_path, "*")):
        if not "_scaled" in image_file:
            add_scale_bar(image_file)


def add_scale_bar(image_path) -> None:
    """Add a scale bar to an image based on the type of scope."""

    # Check if the image exists
    if not os.path.exists(image_path):
        print("The image does not exist. Please provide a valid image.")
        return

    # Check the file extension
    if (
        not image_path.lower().endswith(".tif")
        and not image_path.lower().endswith(".png")
        and not image_path.lower().endswith(".jpg")
    ):
        print(
            "The image must be in .tif, .png, or .jpg format. Please provide a valid image."
        )
        return

    # Read the image including the alpha channel
    image = cv2.imread(image_path, -1)

    # Check the image size
    if image is None or image.shape[0] != 960 or image.shape[1] != 1280:
        print("The image must be 1920x1080 in size. Please provide a valid image.")
        return

    # Define the scale bar size based on the scope_type
    scale_bar_size = int(scale_pixel_200_um * 1)
    label = "200 μm"

    if not DISPLAY_SCALE_NUMBER:
        label = ""

    # Define the position and thickness of the scale bar
    position = (
        image.shape[1] - scale_bar_size - scale_bar_location_x_offset,
        image.shape[0] - scale_bar_location_y_offset,
    )

    # Draw the scale bar using a rectangle
    cv2.rectangle(
        image,
        position,
        (position[0] + scale_bar_size, position[1] + scale_bar_thickness),
        color=scale_bar_color,
        thickness=-1,
    )

    # Convert from BGR to RGB and to PIL
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image)

    # Load font
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", scale_bar_font_size)

    # Draw non-ascii text onto image
    draw = ImageDraw.Draw(pil_image)

    # Calculate text width to center it
    text_width = draw.textlength(label, font=font)
    text_position = (
        position[0] + (scale_bar_size - text_width) // 2,
        position[1] - text_position_y_offset,
    )

    draw.text(text_position, label, font=font, fill=scale_bar_color)

    # Convert back to Numpy array and switch back from RGB to BGR
    image = np.asarray(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Save the new image
    output_path = image_path[:-4] + "_scaled.png"
    cv2.imwrite(output_path, image)
    print(f"Scale bar added to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add a scale bar to an image or all images in a directory based on the type of scope."
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to the image or directory containing images.",
    )

    args = parser.parse_args()

    # Check if the path is a directory or a file
    if os.path.isdir(args.path):
        process_directory(args.path)
    elif os.path.isfile(args.path):
        add_scale_bar(args.path)
    else:
        print("The provided path does not exist or is not a valid image or directory.")
