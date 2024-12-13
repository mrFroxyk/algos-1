import threading
import argparse
from PIL import Image, ImageDraw
from ipdb import set_trace as st

boxType = tuple[int, int, int, int]  # (left, top, right, bottom)

class QuadtreeNode:
    """Node for Quadtree that holds a subsection of an image and
    information about that section."""

    def __init__(self, img, box: boxType, depth: int):
        st()
        self.box = box  # (left, top, right, bottom)
        self.depth = depth
        self.children = None  # tl, tr, bl, br
        self.leaf = False

        # Gets the nodes average color
        image = img.crop(box)
        self.width, self.height = image.size  # (width, height)
        hist = image.histogram()
        self.color, self.error = self.color_from_histogram(hist)  # (r, g, b), error


class Tree:
    """Tree that has nodes with at most four child nodes that hold
    sections of an image where there at most n leaf nodes where
    n is the number of pixels in the image
    """

    def __init__(self, image: Image.Image):
        st()
        self.root = QuadtreeNode(image, image.getbbox(), 0)
        self.width, self.height = image.size
        self.max_depth = 7

        # self._build_tree(image, self.root)

if __name__ == "__main__":
    "Entrypoint"
    parser = argparse.ArgumentParser(description="Make quadtree image")
    parser.add_argument("image_path", type=str, help="Path to the image")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Depth in tree")
    parser.add_argument(
        "-l", "--lines", action="store_true", help="Show lines in image"
    )
    parser.add_argument(
        "-m", "--max_depth", action="store_true", help="show maximum depth of an image"
    )
    parser.add_argument("-glove", "--gif_glove", action="store_true", help="create gif")

    args = parser.parse_args()

    img = Image.open(args.image_path).convert("RGB")
    qtree = Tree(img)
    depth = args.depth
    # output_image = qtree.make_img(depth, lines=args.lines)
    # output_image.save("compressed_img.jpg")

    # if args.gif_glove:
    #     frames = []
    #     for i in range(qtree.max_depth):
    #         output_image = qtree.make_img(i, lines=args.lines)
    #         frames.append(output_image)
    #     frames[0].save(
    #         "compress_gif.gif",
    #         save_all=True,
    #         append_images=frames[1:],  # Ignore first frame.
    #         optimize=True,
    #         duration=800,
    #         loop=0,
    #     )

    # if args.max_depth:
    #     print(f"max depth of an image is {qtree.max_depth}")
