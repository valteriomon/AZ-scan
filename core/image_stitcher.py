
def main():
    parser = argparse.ArgumentParser(description="Large format image creation tools.")

#     parser.add_argument(
#         '-p', '--project',
#         dest='project',
#         default=None,
#         help='Project name (default: timestamp)'
#     )
#     parser.add_argument(
#         '-f', '--fov',
#         dest='fov',
#         default=None,
#         help='HFOV (default: determined by strategy)'
#     )
#     parser.add_argument(
#         '--stitch',
#         action='store_true',
#         help='Stitch images automatically.'
#     )
#     parser.add_argument(
#         '--debug',
#         action='store_true',
#         help='Enable debug mode.'
#     )
#     parser.add_argument(
#         "strategy",
#         choices=["petroff", "quadruplet", "prealigned", "sequential"],
#         help="Which stitching strategy to use."
#     )
#     parser.add_argument(
#         'input',
#         metavar='N',
#         nargs='*',
#         help='Input files (supports glob patterns) or a single folder path.'
#     )

    args = parser.parse_args()

#     input = args.input if args.input else ["."]

#     image_stitcher = ImageStitcher(args.project, input, debug=args.debug)

#     kwargs = {}
#     if args.fov is not None:
#         kwargs['fov'] = args.fov

#     if args.strategy == "petroff":
#         image_stitcher.strategy_petroff(stitch=args.stitch, **kwargs)
#     elif args.strategy == "quadruplet":
#         image_stitcher.strategy_quadruplet(stitch=args.stitch, **kwargs)
#     elif args.strategy == "prealigned":
#         image_stitcher.strategy_prealigned(stitch=args.stitch, **kwargs)
#     elif args.strategy == "sequential":
#         image_stitcher.strategy_sequential(**kwargs)
#     elif args.strategy == "stitch-only":
#         image_stitcher.stitch()

# if __name__ == "__main__":
#     main()

# panorama_tools







def to_absolute_paths(paths):
    """
    Convert a list of file paths (strings or Path objects) to absolute paths.

    Args:
        paths (list[str|Path]): List of file paths.

    Returns:
        list[str]: List of absolute file paths.
    """
    return [str(Path(p).resolve()) for p in paths]












class ImageStitcher:
    def __init__(self, project_name=None, images=None, debug=False):




        self.project_name = project_name or utils.current_unix_timestamp()
        self.pto_tools = PtoTools(project_name, debug=debug)
        self.images = self.sanitize_image_input(images) if images else []

    # def parse_input(self, input):
    #     if input isinstance(str):
    #         self.images = glob.glob(input)
    #     else:
    #         self.images = input



    if not input_files or isinstance(input_files, str):
            input_files = FileSystemUtils.get_images_from_dir(input_files if input_files else ".")

        if len(input_files) == 0:
            print("Error: pto_gen requires a set of images as input.", file=sys.stderr)
            sys.exit(1)

        if not output_pto_file:
            if isinstance(input_files, str):
                output_pto_file = f"project_{FileSystemUtils.get_filename_without_extension_or_final_folder(input_files)}"
            else:
                output_pto_file = f"project_{utils.current_unix_timestamp()}"

        output_pto_file = FileSystemUtils.get_filename_without_extension_or_final_folder(output_pto_file) + ".pto"





    input = []

    if len(args.input) == 1 and os.path.isdir(args.input[0]):
        # Single directory provided
        input = args.input[0]
        input_str = input
    else:
        # One or more file globs provided
        for pattern in args.input:
            input += glob.glob(PathConverter.to_native_path(pattern))
    if not input:
        print("No input images found.")
        return

    image_stitcher = ImageStitcher(args.project, input, debug=args.debug)



    def get_plain_filenames(self):
        filenames_with_ext = [os.path.basename(image_path) for image_path in self.images]
        filenames = [os.path.splitext(filename)[0] for filename in filenames_with_ext]

        if not GridSets.validate_array_items_pattern(filenames):
            print("Failed validation:", filenames)
            raise Exception("Images must be named in letter-number format (e.g., A1.jpg)")

        # return filenames



        """
        Run enblend stitching.

        Supports:
        - enblend(images: list)
        - enblend(path: str)
        - enblend(output: str, images: list or str, [options: list])
        """
        args = [arg for arg in [output, images, options] if arg]
        args_len = len(args)
        if args_len == 0:
            print("Error: enblend requires at least one argument.", file=sys.stderr)
            sys.exit(1)
        elif args_len == 1:
            if isinstance(args[0], list):
                images = args[0]
                output = f"output_{utils.current_unix_timestamp()}"
            elif isinstance(args[0], str):
                if os.path.isdir(args[0]):
                    images =    glob.glob(os.path.join(args[0], '*.tif')) + \
                                glob.glob(os.path.join(args[0], '*.tiff'))
                else:
                    print("Error: enblend requires a folder or a set of images as input.", file=sys.stderr)
                    sys.exit(1)
                output = FileSystemUtils.get_filename_without_extension_or_final_folder(args[0])
        else:
            output  = FileSystemUtils.get_filename_without_extension_or_final_folder(args[0])
            if isinstance(args[1], str):
                images =    glob.glob(os.path.join(args[1], '*.tif')) + \
                            glob.glob(os.path.join(args[1], '*.tiff'))
            elif isinstance(args[1], list):
                images  = args[1]
            else:
                print("Error: enblend requires a folder or a set of images as input.", file=sys.stderr)
                sys.exit(1)
            options = args[2]

        output += ".tif"
        print("Running enblend...")
        Console.wsl(["enblend"] + options + ["-o", output ] + images)
        print(f"Output: {output}")
        # return output





        input = []

    if len(args.input) == 1 and os.path.isdir(args.input[0]):
        # Single directory provided
        input = args.input[0]
        input_str = input
    else:
        # One or more file globs provided
        for pattern in args.input:
            input += glob.glob(PathConverter.to_native_path(pattern))
    if not input:
        print("No input images found.")
        return

        if len(input) == 1:
        input_str = input[0]
    elif len(input) > 1:
        input_str = input









        if project_name and not images:
            images = project_name
        elif images and not project_name:
            if isinstance(images, str):
                project_name = images
            elif isinstance(images, list):
                project_name = utils.current_unix_timestamp()

        # ImageStitcher("test", ["1.jpg", "2.jpg", "3.jpg"])
        # ImageStitcher("x11")
        # ImageStitcher
        # ImageStitcher
        # ImageStitcher
        # ImageStitcher

        # images:
        # project_name:

        if not images:


            # treat project_name as folder


        self.project_name = project_name or utils.current_unix_timestamp()
        self.pto_tools = PtoTools(project_name, debug=debug)
        self.images = self.sanitize_image_input(images) if images else []

    # def parse_input(self, input):
    #     if input isinstance(str):
    #         self.images = glob.glob(input)
    #     else:
    #         self.images = input

    def parse_folder(self, folder):

        images = FileSystemUtils.get_images_from_dir(folder)




        # Flexible inference between project name and image input
        if project_name and not images:
            images = project_name
        elif images and not project_name:
            if isinstance(images, str):
                project_name = images
            elif isinstance(images, list):
                project_name = self._default_project_name()

        # Default to current directory if nothing provided
        if not images:
            images = "."

        # Now process images input
        image_list, inferred_project_name = self._resolve_images(images)
        self.images = image_list
        self.project_name = project_name or inferred_project_name or self._default_project_name()

        if not self.images:
            raise ValueError("No valid images found.")

        self.pto_tools = PtoTools(self.project_name, debug=debug)

    def _resolve_images(self, source):
        """Given a str or list input, return (list_of_images, project_name_if_inferable)"""
        project_name = None

        if isinstance(source, str):
            path = Path(source)
            if path.is_dir():
                # Get images from directory
                images = FileSystemUtils.get_images_from_dir(str(path))
                project_name = path.name
            else:
                # Treat as glob pattern
                images = glob.glob(Path(source).as_posix())
        elif isinstance(source, list):
            # Flatten globs in list
            images = []
            for item in source:
                images.extend(glob.glob(Path(item).as_posix()))
        else:
            raise TypeError("Unsupported input type for images.")

        return images, project_name

    def _default_project_name(self):
        return utils.current_unix_timestamp()





    def get_plain_filenames(self):
        filenames_with_ext = [os.path.basename(image_path) for image_path in self.images]
        filenames = [os.path.splitext(f)[0] for f in filenames_with_ext]
        if not GridSets.validate_array_items_pattern(filenames):
            raise ValueError("Images must be named in letter-number format (e.g., A1.jpg)")
        return filenames












class ImageStitcher:
    def __init__(self, input=None, debug=False):
        pass
        # No input > Current folder > Get images
        # Input > String > Folder > Get images
        # Input > Array of images > Get valid images
    #     self.debug = debug

    #     if input is None:
    #         input = "."

    #     if isinstance(input, str):
    #         input_path = Path(input)

    #         if input_path.exists() and input_path.is_dir():
    #             self.images = self.get_images_from_dir(input_path)
    #         else:
    #             # Assume glob string
    #             self.images = self.expand_glob(input)
    #     elif isinstance(input, list):
    #         self.images = self.filter_valid_images(input)
    #     else:
    #         raise ValueError("Unsupported input type")

    #     if not self.images:
    #         raise FileNotFoundError("No images found of accepted extensions.")

    #     prefix = self.get_current_directory(self.images[0])
    #     self.images = self.validate_grid_filenames(self.images)

    #     if not self.images:
    #         raise FileNotFoundError("No images match the expected pattern.")


    #     if self.debug:
    #         print(f"Found {len(self.images)} image(s):")
    #         for img in self.images:
    #             print(f" - {img}")

    # def get_images_from_dir(self, folder):
    #     extensions = ("*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff")
    #     images = []
    #     for ext in extensions:
    #         images.extend(folder.glob(ext))
    #     return [str(p.resolve()) for p in images]

    # def expand_glob(self, pattern):
    #     pattern = PathConverter.to_native_path(pattern)
    #     return [str(Path(p).resolve()) for p in glob.glob(pattern) if self.is_image_file(p)]

    # def filter_valid_images(self, paths):
    #     return [str(Path(p).resolve()) for p in paths if self.is_image_file(p)]

    # def is_image_file(self, path):
    #     return Path(path).suffix.lower() in [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".gif", ".webp"]

    # def get_current_directory(path):
    #     path = Path(path).resolve()

    #     if path.is_file():
    #         path = path.parent

    #     return path.name

    # def validate_grid_filenames(paths, prefix=None):
    #     valid = []

    #     if prefix:
    #         pattern = re.compile(rf"^{re.escape(prefix)}_[A-Z]\d+$")
    #     else:
    #         pattern = re.compile(r"^[A-Z]\d+$")

    #     for path in paths:
    #         filename = os.path.splitext(os.path.basename(path))[0]
    #         if pattern.match(filename):
    #             valid.append(path)

    #     return valid

# image_stitcher = ImageStitcher()



#     def empty_pto(self):
#         pass

#     def hugin_alignment(self):
#         pass

#     def hugin_stitching(self):
#         pass














#     """
#     Original steps described here: https://github.com/mpetroff/stitch-scanned-images
#     Runs on a finished set of images.
#     Searches control points between all images.
#     Slow on large maps and can lead to a bad result in maps with a lot of big similar sections (like sea borders with very little detail).
#     """
#     def strategy_petroff(self, fov=10, stitch=False):
#         self.pto_tools.pto_gen(self.images, args=[f"--fov={fov}"] if fov else [])

#         # Find control points
#         # Analyze Images, find matches, find matches for overlapping images...
#         self.pto_tools.cpfind([
#             "--fullscale",
#             "--multirow",
#             "--sieve1size", 500,
#             "--sieve2width", 20,
#             "--sieve2height", 20,
#         ])

#         # Set image parameters to optimize ("updating optimizer variables...")
#         self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])

#         # Remove incorrect control points
#         self.pto_tools.cpclean(["-n", "1"])
#         self.pto_tools.cpclean()

#         # Optimizing Variables: rotation and "x,y" translation
#         self.pto_tools.autooptimiser(["-n"])

#         # Morph images to fit control points: makes process slower and does not impact final result, kept in case it's needed in some edge cases.
#         # pto_tools.morph_images_to_fit_control_points(...)

#         # Stitch images
#         self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])

#         if stitch:
#             self.pto_tools.nona()
#             self.pto_tools.enblend(["--primary-seam-generator=graph-cut"])

#     """
#     Runs on a finished set of images.
#     Searches control points in sets of 4 bordering images.
#     Creates a pto file for each set, runs cpfind, then merges the pto files together.
#     """
#     def strategy_quadruplet(self, fov=5, stitch=False):
#         # GridSets.build_matrix_from_cells()
#         # , args=[f"--fov{fov}"] if fov else []
#         filenames = self.get_plain_filenames()
#         # grid of files
#         # A1 to coordinate
#         # coordinate to file

#         (grid, file_grid) = self.build_grid(self.images)
#         grid = GridSets.build_matrix_from_cells(filenames)
#         quadruplets = GridSets.quadruplets(grid)
#         for quadruple in quadruplets:

#             # pto_gen temp file
#             PtoTools.pto_gen()

#             self.pto_tools.cpfind([
#                 "--fullscale",
#                 "--multirow",
#                 "--sieve1size", 500,
#                 "--sieve2width", 20,
#                 "--sieve2height", 20,
#             ])

#         # pto_merge

#         self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])
#         self.pto_tools.cpclean(["-n", "1"])
#         self.pto_tools.cpclean()
#         self.pto_tools.autooptimiser(["-n"])
#         self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])
#         if stitch:
#             self.pto_tools.nona()
#             self.pto_tools.enblend()

#     """
#     Runs on a finished set of images.
#     Repositions the images yaw and pitch and runs cpfind with --prealigned option.
#     """
#     def strategy_prealigned(self, fov=5, stitch=False):
#         # TODO: Could be simplified a lot:
#         # Iterate rows and set a pitch based on length.
#         # Iterate columns and set a yaw based on length.

#         def generate_yaw_and_pitch_matrix(filenames, base_value=1.0, multiplier=5, offset=-1):

#             def find_center(cells):
#                 rows = sorted(set(r for r, _ in cells))
#                 cols = sorted(set(c for _, c in cells))

#                 if len(rows) % 2 == 1:
#                     mid_rows = [rows[len(rows)//2]]
#                 else:
#                     mid_rows = rows[len(rows)//2 - 1:len(rows)//2 + 1]

#                 if len(cols) % 2 == 1:
#                     mid_cols = [cols[len(cols)//2]]
#                 else:
#                     mid_cols = cols[len(cols)//2 - 1:len(cols)//2 + 1]

#                 return {(r, c) for r in mid_rows for c in mid_cols if (r, c) in cells}

#             positions = {}
#             for filename in filenames:
#                 row_letter = ''.join(filter(str.isalpha, filename)).upper()
#                 col_number = ''.join(filter(str.isdigit, filename))
#                 pos = (
#                     string.ascii_uppercase.index(row_letter),
#                     int(col_number) - 1
#                 )
#                 positions[pos] = filename

#             coords = list(positions.keys())
#             center_cells = find_center(coords)

#             # Compute average center row and column for yaw/pitch reference
#             avg_center_row = sum(r for r, _ in center_cells) / len(center_cells)
#             avg_center_col = sum(c for _, c in center_cells) / len(center_cells)

#             values = {}
#             for pos in coords:
#                 r, c = pos
#                 min_dist = min(abs(r - cr) + abs(c - cc) for cr, cc in center_cells)
#                 values[pos] = base_value * (multiplier ** min_dist) + offset

#             max_row = max(r for r, _ in coords)
#             max_col = max(c for _, c in coords)
#             matrix = [['' for _ in range(max_col + 1)] for _ in range(max_row + 1)]

#             for (r, c), val in values.items():
#                 fname = positions[(r, c)]
#                 # orientation_degrees = ImageUtils.get_rotation_degrees(os.path.join(folder_path, fname))

#                 yaw = (c - avg_center_col) * multiplier   # horizontal offset scaled
#                 pitch = (avg_center_row - r) * multiplier # vertical offset scaled

#                 # Include yaw and pitch in the matrix cell
#                 matrix[r][c] = (f"{val:.2f}", fname, 1, yaw, pitch)

#             return matrix, values

#         matrix, _ = generate_yaw_and_pitch_matrix(self.get_plain_filenames())
#         pto_file = self.pto_tools.pto_gen(self.images, args=[f"--fov={fov}"] if fov else [])

#         temp_pto = f"{self.project_name}_pto.tmp"
#         index = 0
#         for row in matrix:
#             for cell in row:
#                 if not cell:
#                     continue
#                 _, _, roll, yaw, pitch = cell
#                 PtoTools.pto_var(pto_file, args=["--set", f"y{index}={yaw},p{index}={pitch},r{index}={roll}"])
#                 # os.replace(temp_pto, pto_file) # Overwrite original for next call
#                 index += 1

#         self.pto_tools.cpfind([
#             "--prealigned",
#             "--sieve1size", 500,
#             "--sieve2width", 20,
#             "--sieve2height", 20
#         ])
#         # Reset yaw and pitch to 0 before optimization (pending testing if the result is better...)
#         self.pto_tools.pto_var(["--set", "y=0,p=0"])
#         self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])
#         self.pto_tools.cpclean(["-n", "1"])
#         self.pto_tools.cpclean()
#         self.pto_tools.autooptimiser(["-n"])
#         self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])
#         if stitch:
#             self.pto_tools.nona()
#             self.pto_tools.enblend()

#     """
#     Runs while the images are being created. Stitching done separately.
#     Searches control points based on the last image added to the project, using only the direct neighbours.
#     Creates a new partial pto file that is merged to the project pto file.
#     """
#     def strategy_sequential(self, fov=5):
#         # , args=[f"--fov{fov}"] if fov else []
#     #     os.makedirs(output_dir, exist_ok=True)
#     #     pto_files = []
#     #     for i, row in enumerate(rows):
#     #         # Filter out any empty entries (like accidental commas or typos)
#     #         input_files = [f"{name}.jpg" for name in row if name]
#     #         pto_file = os.path.join(output_dir, f"row_{i}.pto")
#     #         # Step 1: Create .pto for this row
#     #         subprocess.check_call(['pto_gen', '--fov=5', '-o', pto_file] + input_files)
#     #         # Step 2: Run cpfind with key caching
#     #         subprocess.check_call([
#     #             'cpfind',
#     #             '--fullscale',
#     #             '--multirow',
#     #             '--sieve1size', '500',
#     #             '--sieve2width', '20',
#     #             '--sieve2height', '20',
#     #             '--cache',
#     #             '-o', pto_file,
#     #             pto_file
#     #         ])
#     #         pto_files.append(pto_file)
#     #     # Step 3: Merge all .pto files into a single project
#     #     merged_pto = os.path.join(output_dir, 'merged.pto')
#     #     subprocess.check_call(['pto_merge', '-o', merged_pto] + pto_files)
#         self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])
#         self.pto_tools.cpclean(["-n", "1"])
#         self.pto_tools.cpclean()
#         self.pto_tools.autooptimiser(["-n"])
#         self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])

#     """
#     """
#     @staticmethod
#     def stitch(pto_file):
#         PtoTools.nona(pto_file)
#         PtoTools.enblend()

#     """
#     """


# ***************************************************************** #
# ***************************************************************** #
# ***************************************************************** #



# from core.utils import ImageUtils, FileSystemUtils

# Folder > Images > Valid images




