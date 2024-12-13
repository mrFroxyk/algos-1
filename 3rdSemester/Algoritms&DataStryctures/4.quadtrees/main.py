import click
import pathlib
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
import math

box_coords = tuple[int, int, int, int]  # (left, top, right, bottom)
colors_brightness = tuple[int, int, int]

class QuadtreeNode:
    """Node for Quadtree that holds a subsection of an image and
    information about that section."""

    def __init__(self, img: Image.Image, box: box_coords, depth: int):
        self.box = box  # (left, top, right, bottom)
        self.depth = depth
        self.children = None  # tl, tr, bl, br
        self.leaf = False

        # Gets the nodes average color
        image = img.crop(box)
        self.width, self.height = image.size  # (width, height)
        hist = image.histogram()  # list of 768 color value | hist[767] - pixel counts with the max brightness of Blue channel
        self.color, self.error = self.color_from_histogram(
            hist
        )  # (r, g, b), variance_error


    
    def weighted_average(self, hist):
        """Return the weighted color average and error from a hisogram of pixles."""
        total = sum(hist)
        value, error = 0, 0
        if total > 0:
            value = sum(i * j for i, j in enumerate(hist)) / total
            error = sum(j * (value - i) ** 2 for i, j in enumerate(hist)) / total
            error = error**0.5
        return value, error

    def color_from_histogram(self, hist):
        """Returns the average rgb color from a given histogram of pixel color counts"""
        r, re = self.weighted_average(hist[:256])
        g, ge = self.weighted_average(hist[256:512])
        b, be = self.weighted_average(hist[512:768])
        e = re * 0.2989 + ge * 0.5870 + be * 0.1140
        return (int(r), int(g), int(b)), e

    # def color_from_histogram(
    #     self,
    #     hist: list[int],
    #     image: Image.Image,
    # ) -> tuple[ colors_brightness, int ]:
    #     """Return the average rgb color from a given histogram of pixel color counts"""
    #     from PIL import ImageStat
    #     stat = ImageStat.Stat(img)

    #     red_error, green_error, blue_error = stat.stddev[:3]  # color_variance
    #     total_error = red_error * 0.2989 + green_error * 0.5870 + blue_error * 0.1140
    #     red, green, blue = stat.mean[:3]  # color_mean

    #     return (int(red_error), int(green_error), int(blue_error)), total_error
    
    def split(self, img: Image.Image) -> None:
        """
        Divide image into 4 ports
        :param img: image
        """
        l, t, r, b = self.box
        lr = l + (r - l) / 2
        tb = t + (b - t) / 2
        tl = QuadtreeNode(img, (l, t, lr, tb), self.depth + 1)
        tr = QuadtreeNode(img, (lr, t, r, tb), self.depth + 1)
        bl = QuadtreeNode(img, (l, tb, lr, b), self.depth + 1)
        br = QuadtreeNode(img, (lr, tb, r, b), self.depth + 1)
        self.children = [tl, tr, bl, br]


class Tree:
    """Tree that has nodes with at most four child nodes that hold
    sections of an image where there at most n leaf nodes where
    n is the number of pixels in the image
    """
    
    

    def __init__(self, image: Image.Image, depth: int):
        # image.getbbox() - return some like (0, 0, 4096, 2304) = left & top coord for main point and width and heigh of image
        self.root = QuadtreeNode(image, image.getbbox(), 0)
        self.width, self.height = image.size
        self.max_depth = min(depth, 100)
        self.COLOR_VARIANCE = 10 - math.log2(depth)

        # print(self.COLOR_VARIANCE)
        if depth > 10: 
            print("Be paitient, more depth = more runtime")

        self._build_tree(image, self.root)

    def _build_tree(self, image, node):
        """Recursively adds nodes untill max_depth is reached or error is less than 12"""
        if (node.depth >= self.max_depth) or (node.error <= self.COLOR_VARIANCE):
            node.leaf = True
            return
        node.split(image)

        if node.depth == 0:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self._build_tree, image, child)
                    for child in node.children
                ]
                # Ensure all threads complete
                for future in futures:
                    future.result()
        else:
            for child in node.children:
                self._build_tree(image, child)


    def get_leaf_nodes(self, depth: int):
        """Gets all the leaf nodes."""

        def get_leaf_nodes_recusion(node: QuadtreeNode):
            """Recusivley gets leaf nodes based on whether a node is a leaf."""
            collector = []
            if node.leaf or node.depth == depth:
                collector.append(node)
            else:
                # if have any child node
                for child in node.children:
                    collector = [*collector, *get_leaf_nodes_recusion(child)]
            return collector

        return get_leaf_nodes_recusion(self.root)

    def make_img(self, depth, lines) -> Image.Image:
        """Creates a Pillow image object from a given level/depth of the tree"""
        image = Image.new("RGB", (int(self.width), int(self.height)))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, self.width, self.height))

        leaf_nodes = self.get_leaf_nodes(depth)
        for node in leaf_nodes:
            l, t, r, b = node.box
            box = (l, t, r - 1, b - 1)
            if lines:
                draw.rectangle(box, node.color, outline=(0, 0, 0))
            else:
                draw.rectangle(box, node.color)
        return image


@click.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("-d", "--depth", type=int, default=2, help="Depth in tree")
@click.option("-l", "--lines", is_flag=True, help="Show lines in image")
@click.option("-glove", "--gif_glove", is_flag=True, help="Create gif")
def make_quadtree_image(image_path: pathlib.Path, depth: int, lines: bool, gif_glove: bool):
    """Entrypoint"""

    img = Image.open(image_path).convert("RGB")
    qtree = Tree(img, depth)
    output_image = qtree.make_img(depth, lines=lines)
    output_image.save("compressed_img.jpg")

    if gif_glove:
        frames = []
        for i in range(qtree.max_depth):
            output_image = qtree.make_img(i, lines=lines)
            frames.append(output_image)
        
        extra_images = [*frames[1:], *[frames[-1]]*8]  # More duration for output frame

        # kostia_anime = Image.open('kostia_anime.jpg').convert("RGB")
        #extra_images = [*frames[1:], *[frames[-1]]*1, *[kostia_anime]*30]  # More duration for output frame

        frames[0].save(
            "compress_gif.gif",
            save_all=True,
            append_images=extra_images,  # Ignore first frame.
            optimize=True,
            duration=600,
            loop=0,
        )

if __name__ == "__main__":
    make_quadtree_image()