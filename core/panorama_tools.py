# TODO:
# - Allow extra scans not in the grid (used to patch weak connections).
#      - Set position in grid.
# - Allow extra passes of cpfind in diagonal neighbors.
# - Run cpfind in rows and columns.
# - Monitor scan folder for sequential stitch.
# - Set rotation (roll).
# - Linear match + prealigned method.
# - Clean pto file.
# - hugin_executor --assistant

import argparse, os, sys, string, re, tempfile, glob
from core.console import Console, PathConverter
import core.utils as utils
from core.utils import ImageUtils, FileSystemUtils

class ImageStitcher:
    def __init__(self, project_name, images=None, debug=False):
        self.project_name = project_name or utils.current_unix_timestamp()
        self.pto_tools = PtoTools(project_name, debug=debug)
        self.images = images

    def empty_pto(self):
        pass

    def hugin_alignment(self):
        pass

    def hugin_stitching(self):
        pass

    """
    Original steps described here: https://github.com/mpetroff/stitch-scanned-images
    Runs on a finished set of images.
    Searches control points between all images.
    Slow on large maps and can lead to a bad result in maps with a lot of big similar sections (like sea borders with very little detail).
    """
    def strategy_petroff(self, fov=10, stitch=False):
        self.pto_tools.pto_gen(self.images, args=[f"--fov={fov}"] if fov else [])

        # Find control points
        # Analyze Images, find matches, find matches for overlapping images...
        self.pto_tools.cpfind([
            "--fullscale",
            "--multirow",
            "--sieve1size", 500,
            "--sieve2width", 20,
            "--sieve2height", 20,
        ])

        # Set image parameters to optimize ("updating optimizer variables...")
        self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])

        # Remove incorrect control points
        self.pto_tools.cpclean(["-n", "1"])
        self.pto_tools.cpclean()

        # Optimizing Variables: rotation and "x,y" translation
        self.pto_tools.autooptimiser(["-n"])

        # Morph images to fit control points: makes process slower and does not impact final result, kept in case it's needed in some edge cases.
        # pto_tools.morph_images_to_fit_control_points(...)

        # Stitch images
        self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])

        if stitch:
            self.pto_tools.nona()
            self.pto_tools.enblend(["--primary-seam-generator=graph-cut"])

    """
    Runs on a finished set of images.
    Searches control points in sets of 4 bordering images.
    Creates a pto file for each set, runs cpfind, then merges the pto files together.
    """
    def strategy_quadruplet(self, fov=5, stitch=False):
        # GridSets.build_matrix_from_cells()
        # , args=[f"--fov{fov}"] if fov else []
        filenames = self.get_plain_filenames()
        # grid of files
        # A1 to coordinate
        # coordinate to file

        (grid, file_grid) = self.build_grid(self.images)
        grid = GridSets.build_matrix_from_cells(filenames)
        quadruplets = GridSets.quadruplets(grid)
        for quadruple in quadruplets:

            # pto_gen temp file
            PtoTools.pto_gen()

            self.pto_tools.cpfind([
                "--fullscale",
                "--multirow",
                "--sieve1size", 500,
                "--sieve2width", 20,
                "--sieve2height", 20,
            ])

        # pto_merge

        self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])
        self.pto_tools.cpclean(["-n", "1"])
        self.pto_tools.cpclean()
        self.pto_tools.autooptimiser(["-n"])
        self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])
        if stitch:
            self.pto_tools.nona()
            self.pto_tools.enblend()

    """
    Runs on a finished set of images.
    Repositions the images yaw and pitch and runs cpfind with --prealigned option.
    """
    def strategy_prealigned(self, fov=5, stitch=False):
        # TODO: Could be simplified a lot:
        # Iterate rows and set a pitch based on length.
        # Iterate columns and set a yaw based on length.

        def generate_yaw_and_pitch_matrix(filenames, base_value=1.0, multiplier=5, offset=-1):

            def find_center(cells):
                rows = sorted(set(r for r, _ in cells))
                cols = sorted(set(c for _, c in cells))

                if len(rows) % 2 == 1:
                    mid_rows = [rows[len(rows)//2]]
                else:
                    mid_rows = rows[len(rows)//2 - 1:len(rows)//2 + 1]

                if len(cols) % 2 == 1:
                    mid_cols = [cols[len(cols)//2]]
                else:
                    mid_cols = cols[len(cols)//2 - 1:len(cols)//2 + 1]

                return {(r, c) for r in mid_rows for c in mid_cols if (r, c) in cells}

            positions = {}
            for filename in filenames:
                row_letter = ''.join(filter(str.isalpha, filename)).upper()
                col_number = ''.join(filter(str.isdigit, filename))
                pos = (
                    string.ascii_uppercase.index(row_letter),
                    int(col_number) - 1
                )
                positions[pos] = filename

            coords = list(positions.keys())
            center_cells = find_center(coords)

            # Compute average center row and column for yaw/pitch reference
            avg_center_row = sum(r for r, _ in center_cells) / len(center_cells)
            avg_center_col = sum(c for _, c in center_cells) / len(center_cells)

            values = {}
            for pos in coords:
                r, c = pos
                min_dist = min(abs(r - cr) + abs(c - cc) for cr, cc in center_cells)
                values[pos] = base_value * (multiplier ** min_dist) + offset

            max_row = max(r for r, _ in coords)
            max_col = max(c for _, c in coords)
            matrix = [['' for _ in range(max_col + 1)] for _ in range(max_row + 1)]

            for (r, c), val in values.items():
                fname = positions[(r, c)]
                # orientation_degrees = ImageUtils.get_rotation_degrees(os.path.join(folder_path, fname))

                yaw = (c - avg_center_col) * multiplier   # horizontal offset scaled
                pitch = (avg_center_row - r) * multiplier # vertical offset scaled

                # Include yaw and pitch in the matrix cell
                matrix[r][c] = (f"{val:.2f}", fname, 1, yaw, pitch)

            return matrix, values

        matrix, _ = generate_yaw_and_pitch_matrix(self.get_plain_filenames())
        pto_file = self.pto_tools.pto_gen(self.images, args=[f"--fov={fov}"] if fov else [])

        temp_pto = f"{self.project_name}_pto.tmp"
        index = 0
        for row in matrix:
            for cell in row:
                if not cell:
                    continue
                _, _, roll, yaw, pitch = cell
                PtoTools.pto_var(pto_file, args=["--set", f"y{index}={yaw},p{index}={pitch},r{index}={roll}"])
                # os.replace(temp_pto, pto_file) # Overwrite original for next call
                index += 1

        self.pto_tools.cpfind([
            "--prealigned",
            "--sieve1size", 500,
            "--sieve2width", 20,
            "--sieve2height", 20
        ])
        # Reset yaw and pitch to 0 before optimization (pending testing if the result is better...)
        self.pto_tools.pto_var(["--set", "y=0,p=0"])
        self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])
        self.pto_tools.cpclean(["-n", "1"])
        self.pto_tools.cpclean()
        self.pto_tools.autooptimiser(["-n"])
        self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])
        if stitch:
            self.pto_tools.nona()
            self.pto_tools.enblend()

    """
    Runs while the images are being created. Stitching done separately.
    Searches control points based on the last image added to the project, using only the direct neighbours.
    Creates a new partial pto file that is merged to the project pto file.
    """
    def strategy_sequential(self, fov=5):
        # , args=[f"--fov{fov}"] if fov else []
    #     os.makedirs(output_dir, exist_ok=True)
    #     pto_files = []
    #     for i, row in enumerate(rows):
    #         # Filter out any empty entries (like accidental commas or typos)
    #         input_files = [f"{name}.jpg" for name in row if name]
    #         pto_file = os.path.join(output_dir, f"row_{i}.pto")
    #         # Step 1: Create .pto for this row
    #         subprocess.check_call(['pto_gen', '--fov=5', '-o', pto_file] + input_files)
    #         # Step 2: Run cpfind with key caching
    #         subprocess.check_call([
    #             'cpfind',
    #             '--fullscale',
    #             '--multirow',
    #             '--sieve1size', '500',
    #             '--sieve2width', '20',
    #             '--sieve2height', '20',
    #             '--cache',
    #             '-o', pto_file,
    #             pto_file
    #         ])
    #         pto_files.append(pto_file)
    #     # Step 3: Merge all .pto files into a single project
    #     merged_pto = os.path.join(output_dir, 'merged.pto')
    #     subprocess.check_call(['pto_merge', '-o', merged_pto] + pto_files)
        self.pto_tools.pto_var(["--opt", "r,TrX,TrY"])
        self.pto_tools.cpclean(["-n", "1"])
        self.pto_tools.cpclean()
        self.pto_tools.autooptimiser(["-n"])
        self.pto_tools.pano_modify(["-p", "0", "--fov=AUTO", "--canvas=AUTO", "--crop=AUTO"])

    """
    """
    @staticmethod
    def stitch(pto_file):
        PtoTools.nona(pto_file)
        PtoTools.enblend()

    """
    """
    def get_plain_filenames(self):
        filenames_with_ext = [os.path.basename(image_path) for image_path in self.images]
        filenames = [os.path.splitext(filename)[0] for filename in filenames_with_ext]

        if not GridSets.validate_array_items_pattern(filenames):
            print("Failed validation:", filenames)
            raise Exception("Images must be named in letter-number format (e.g., A1.jpg)")

        return filenames

# ***************************************************************** #
# ***************************************************************** #
# ***************************************************************** #

class PtoTools:
    def __init__(self, project_name=None, debug=False):
        self._project_name = project_name or utils.current_unix_timestamp()
        self._pto_file = f"{self._project_name}.pto"
        self._debug = debug

        self._tmp_dir_obj = tempfile.TemporaryDirectory()
        self._tmp_dir = self._tmp_dir_obj.name

        # Match instance methods names to the static ones
        self.pto_gen = self._pto_gen
        self.pto_merge = self._pto_merge
        self.cpfind = self._cpfind
        self.pto_var = self._pto_var
        self.cpclean = self._cpclean
        self.autooptimiser = self._autooptimiser
        self.pano_modify = self._pano_modify
        self.nona = self._nona
        self.enblend = self._enblend

    @property
    def pto_file(self):
        return self._pto_file

    def sanitize_image_input(self, input):
        pass

    """
    > hugin_executor
    Execute a hugin command.

    Usage: hugin_executor [-h] [-a] [-s] [-t <num>] [-p <str>] [-u <str>] [--user-defined-assistant <str>] [-d] input.pto
    -h, --help                            shows this help message
    -a, --assistant                       execute assistant
    -s, --stitching                       execute stitching with given project
    -t, --threads=<num>                   number of used threads
    -p, --prefix=<str>                    prefix used for stitching
    -u, --user-defined-output=<str>       use user defined commands in given file
    --user-defined-assistant=<str>        use user defined assistant commands in given file
    -d, --dry-run                         only print commands
    """
    def hugin_executor(self, args=[]):
        pass

    """
    > pto_gen
    Generate project file from images.

    -p, --projection=INT                Projection type (default: read from database)
    -f, --fov=FLOAT                     Horizontal field of view of images default: read from database
    --ignore-fov-rectilinear            Don't read fov for rectilinear images from the database,
                                        instead use only the values from EXIF data
    -c, --crop=left,right,top,bottom    Sets the crop of input images (especially for fisheye lenses)
    -s, --stacklength=INT               Number of images in stack (default: automatic detection)
    -l, --linkstacks                    Link image positions in stacks
    --distortion                        Try to load distortion information from lens database
    --vignetting                        Try to load vignetting information from lens database
    --sort                              Sort the files by name alphanumeric otherwise the images
                                        are processed in the order given at the command line
    """
    @staticmethod
    def pto_gen(input_files=None, output_pto_file=None, args=[]):

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

        print(f"Creating project file {output_pto_file} with images:", input_files)
        print("Running pto_gen with args:", args)
        Console.wsl(["pto_gen"]  + args + [
            "-o", output_pto_file
        ] + input_files)
        return output_pto_file

    def _pto_gen(self, input_files, args=[]):
        return PtoTools.pto_gen(input_files, self._pto_file, args)

    """
    > pto_merge
    Merges several project files.
    """
    @staticmethod
    def pto_merge(input_pto_files=None, output_pto_file=None):
        """
        Run enblend stitching.

        Supports:
        - pto_merge(input_pto_files: list|str)
        - pto_merge(input_pto_files: str)
        - pto_merge(input_pto_files: liststr, images: list or folder_path, options: list)
        """

        if not output_pto_file:
            output_pto_file = f"{self._project_name}_merged.pto"

        if not input_pto_files:
            input_pto_files = glob.glob("*.pto")

        # print(f"Running pto_merge with args:", args)
        Console.wsl([
            "pto_merge",
            "-o", output_pto_file,
        ] + input_pto_files)

        return output_pto_file

    def _pto_merge(self, input_pto_files, output_pto_file=None):
        return PtoTools.pto_merge(input_pto_files)

    """
    > cpfind
    Control point detector.

    Matching strategy (these options are mutually exclusive)
    --linearmatch   Enable linear images matching
                    Can be fine tuned with
        --linearmatchlen=<int>  Number of images to match (default: 1)
    --multirow      Enable heuristic multi row matching
    --prealigned    Match only overlapping images,
                    requires a rough aligned panorama

    Feature description options
    --sieve1width=<int>    Sieve 1: Number of buckets on width (default: 10)
    --sieve1height=<int>   Sieve 1: Number of buckets on height (default: 10)
    --sieve1size=<int>     Sieve 1: Max points per bucket (default: 100)
    --kdtreesteps=<int>          KDTree: search steps (default: 200)
    --kdtreeseconddist=<double>  KDTree: distance of 2nd match (default: 0.25)

    Feature matching options
    --minmatches=<int>     Minimum matches (default: 6)
    --sieve2width=<int>    Sieve 2: Number of buckets on width (default: 5)
    --sieve2height=<int>   Sieve 2: Number of buckets on height (default: 5)
    --sieve2size=<int>     Sieve 2: Max points per bucket (default: 1)

    Caching options
    -c|--cache    Caches keypoints to external file
    --clean       Clean up cached keyfiles
    -p|--keypath=<string>    Store keyfiles in given path
    -k|--writekeyfile=<int>  Write a keyfile for this image number
    --kall                   Write keyfiles for all images in the project

    Run --help for more information.
    """
    @staticmethod
    def cpfind(pto_file, output_pto_file=None, args=[]):
        if not output_pto_file:
            output_pto_file = pto_file

        print("Running cpfind with args:", args)
        Console.wsl(["cpfind"] + args + [
            "-o", output_pto_file,
            pto_file
        ])
        return output_pto_file

    def _cpfind(self, args=[]):
        output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_cpfind.pto"
        return PtoTools.cpfind(self._pto_file, output_pto_file, args)

    """
    > pto_var
    Change image variables inside pto files.

    --opt varlist           Change optimizer variables
    --modify-opt            Modify the existing optimizer variables (without pto_var will start with an empty variables set)
                            Examples:
        --opt=y,p,r         Optimize yaw, pitch and roll of all images (special treatment for anchor image applies)
        --opt=v0,b2         Optimize hfov of image 0 and barrel distortion of image 2
        --opt=v,!v0         Optimize field of view for all images except for the first image
        --opt=!a,!b,!c      Don't optimise distortion (works only with switch --modify-opt together)

    --link varlist          Link given variables
                            Example:
        --link=v3           Link hfov of image 3
        --link=a1,b1,c1     Link distortions parameter for image 1

    --unlink varlist        Unlink given variables
                            Examples:
        --unlink=v5         Unlink hfov for image 5
        --unlink=a2,b2,c2   Unlink distortions parameters for image 2

    --set varlist           Sets variables to new values
                            Examples:
        --set=y0=0,r0=0,p0=0  Resets position of image 0
        --set=Vx4=-10,Vy4=10  Sets vignetting offset for image 4
        --set=v=20            Sets the field of view to 20 for all images
        --set=y=val+20        Increase yaw by 20 deg for all images
        --set=v=val*1.1       Increase fov by 10 % for all images
        --set=y=i*20          Set yaw to 0, 20, 40, ...
    --set-from-file filename  Sets variables to new values
                            It reads the varlist from a file

    --crop=left,right,top,bottom Set the crop for all images
    --crop=width,height       Set the crop for all images and activate
                            autocenter for crop
                            relative values can be used with %
    --crop=iNUM=left,right,top,bottom Set the crop for image NUM
    --crop=iNUM=width,height  Set the crop for image NUM and
                            activate autocenter for crop
                            These switches can be used several times.

    --anchor=NUM            Sets the image NUM as anchor for geometric
                            optimisation.
    --color-anchor=NUM      Sets the image NUM as anchor for photometric
                            optimisation.

    Run --help for more information.
    """
    def pto_var(pto_file, output_pto_file=None, args=[]):
        if not output_pto_file:
            output_pto_file = pto_file

        print("Running pto_var with args:", args)
        Console.wsl(["pto_var"] + args + [
            "-o", output_pto_file,
            pto_file
        ])
        return output_pto_file

    def _pto_var(self, args=[]):
        output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_pto_var.pto"
        return PtoTools.pto_var(self._pto_file, output_pto_file, args)

    """
    > cpclean
    Remove wrong control points by statistic method.
    Step 1: Do image pair control point checking.
    Step 2: Do whole panorama control point checking.

    --max-distance|-n num       Distance factor for checking (default: 2) (cps with an error mean + this factor*sigma will be removed)
    --pairwise-checking|-p      Do only images pairs cp checking (skip step 2)
    --whole-pano-checking|-w    Do only whole panorama cp checking (skip step 1)
    --dont-optimize|-s          Skip optimisation step when checking the whole panorama (only step 2)
    --check-line-cp|-l          Also include line control points for calculation and filtering in step 2
    """
    @staticmethod
    def cpclean(pto_file, output_pto_file=None, args=[]):
        if not output_pto_file:
            output_pto_file = pto_file

        print("Running cpclean with args:", args)
        Console.wsl(["cpclean"] + args + [
            "-o", output_pto_file,
            pto_file
        ])
        return output_pto_file

    def _cpclean(self, args=[]):
        output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_cpclean.pto"
        return PtoTools.cpclean(self._pto_file, output_pto_file, args)

    """
    > autooptimiser
    Optimize image positions.

    -a  Auto align mode, includes various optimisation stages, depending on the amount and distribution of the control points
    -p  Pairwise optimisation of yaw, pitch and roll, starting from first image
    -m  Optimise photometric parameters
    -n  Optimize parameters specified in script file (like PTOptimizer)

    Run --help for more information.
    """
    @staticmethod
    def autooptimiser(pto_file, output_pto_file=None, args=[]):
        if not output_pto_file:
            output_pto_file = pto_file
        Console.wsl(["autooptimiser"] + args + [
            "-o", output_pto_file,
            pto_file
        ])
        return output_pto_file

    def _autooptimiser(self, args=[]):
        output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_autooptimiser.pto"
        return PtoTools.autooptimiser(self._pto_file, output_pto_file, args)

    """
    > pano_modify
    Change output parameters of project file.

    -p, --projection=x                  Sets the output projection to number x
    --projection-parameter=x            Sets the parameter of the projection
                                        (Several parameters are separated by
                                        space or comma)
    --fov=AUTO|HFOV|HFOVxVFOV           Sets field of view
                                        AUTO: calculates optimal fov
                                        HFOV|HFOVxVFOV: set to given fov
    -s, --straighten                    Straightens the panorama
    -c, --center                        Centers the panorama
    --canvas=AUTO|num%|WIDTHxHEIGHT     Sets the output canvas size
                                        AUTO: calculate optimal canvas size
                                        num%: scales the optimal size by given percent
                                        WIDTHxHEIGHT: set to given size
    --crop=AUTO|AUTOHDR|AUTOOUTSIDE|left,right,top,bottom|left,right,top,bottom%
                                        Sets the crop rectangle
                                        AUTO: autocrop panorama
                                        AUTOHDR: autocrop HDR panorama
                                        AUTOOUTSIDE: autocrop outside of all images
                                        left,right,top,bottom: to given size
                                        left,right,top,bottom%: to size relative to canvas
    --output-type=str                   Sets the type of output
                                        Valid items are
                                        NORMAL|N: normal panorama
                                        STACKSFUSEDBLENDED|BF: LDR panorama with
                                            blended stacks
                                        EXPOSURELAYERSFUSED|FB: LDR panorama with
                                            fused exposure layers (any arrangement)
                                        HDR: HDR panorama
                                        REMAP: remapped images with corrected exposure
                                        REMAPORIG: remapped images with
                                            uncorrected exposure
                                        HDRREMAP: remapped images in linear color space
                                        FUSEDSTACKS: exposure fused stacks
                                        HDRSTACKS: HDR stacks
                                        EXPOSURELAYERS: blended exposure layers
                                        and separated by a comma.
    --rotate=yaw,pitch,roll             Rotates the whole panorama with the given angles
    --translate=x,y,z                   Translate the whole panorama with the given values
    --interpolation=int                 Sets the interpolation method

    Run --help for more information.
    """
    @staticmethod
    def pano_modify(pto_file, output_pto_file=None, args=[]):
        if not output_pto_file:
            output_pto_file = pto_file
        Console.wsl(["pano_modify"] + args + [
            "-o", output_pto_file,
            pto_file
        ])
        return output_pto_file

    def _pano_modify(self, args=[]):
        output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_pano_modify.pto"
        return PtoTools.pano_modify(self._pto_file, output_pto_file, args)

    """
    > nona
    Stitch a panorama image. It uses the transform function from PanoTools.

    nona [options] -o output project_file (image files)

    Run --help for more information.
    """
    @staticmethod
    def nona(pto_file, output_folder=None, args=[]):
        if not output_folder:
            output_folder = f"{FileSystemUtils.get_filename_without_extension(pto_file)}_remapped"

        print("Running nona...")
        Console.wsl(["nona"] + args + [
            "-o", output_folder,
            pto_file
        ])
        print(f"Output folder: {output_folder}")
        return output_folder

    def _nona(self, args=[]):
        if self._debug:
            output_folder = f"{self._project_name}_nona"
            os.makedirs(output_folder, exist_ok=True)
        else:
            output_folder = self._tmp_dir

        self._remapped_folder = output_folder
        return PtoTools.nona(self._pto_file, output_folder + os.sep + "remapped", args)

    """
    > enblend
    Blend INPUT images into a single IMAGE.

    enblend [options] [--output=IMAGE] INPUT...

    Run --help for more information.
    """
    @staticmethod
    def enblend(output=None, images=None, options=[]):
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
        return output

    def _enblend(self, options=[]):
        image_folder = self._remapped_folder + os.sep + "remapped*"
        return PtoTools.enblend(self._project_name, image_folder, options)

    @staticmethod
    def morph_images_to_fit_control_points(pto_file, input_files, tmp):
        # Should be handled by Console class
        import subprocess

        img_ctrl_pts = ''
        with open(pto_file) as input:
            for line in input:
                if line[0] == 'c':
                    img1 = line.split('n')[1].split()[0]
                    img2 = line.split('N')[1].split()[0]
                    x1 = line.split('x')[1].split()[0]
                    x2 = line.split('X')[1].split()[0]
                    y1 = line.split('y')[1].split()[0]
                    y2 = line.split('Y')[1].split()[0]
                    img_ctrl_pts += img1 + ' ' + x1 + ' ' + y1 + '\n' \
                                + img2 + ' ' + x2 + ' ' + y2 + '\n'
        pipe = subprocess.Popen(['pano_trafo', pto_file], stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        trafo_out = (pipe.communicate(input
                                    = img_ctrl_pts.encode('utf-8'))[0]).decode('utf-8')
        split_img_ctrl_pts = img_ctrl_pts.splitlines()
        split_trafo_out = trafo_out.splitlines()
        morphed_split_trafo_out = [''] * len(split_trafo_out)
        for i in range(0, int(len(split_trafo_out) / 2)):
            i1 = split_img_ctrl_pts[i*2].split()[0]
            i2 = split_img_ctrl_pts[i*2+1].split()[0]
            x = (float(split_trafo_out[i*2].split()[0]) \
                + float(split_trafo_out[i*2+1].split()[0])) / 2
            y = (float(split_trafo_out[i*2].split()[1]) \
                + float(split_trafo_out[i*2+1].split()[1])) / 2
            morphed_split_trafo_out[i*2] = i1 + ' ' + str(x) + ' ' + str(y)
            morphed_split_trafo_out[i*2+1] = i2 + ' ' + str(x) + ' ' + str(y)
        trafo_r_in = "\n".join(morphed_split_trafo_out)
        pipe = subprocess.Popen(['pano_trafo', '-r', pto_file], stdout=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        trafo_r_out = (pipe.communicate(input
                                    = trafo_r_in.encode('utf-8'))[0]).decode('utf-8')
        split_trafo_r_out = trafo_r_out.splitlines()
        ctrlPts = [''] * len(input_files)
        for i in range(0, len(split_trafo_r_out)):
            ctrlPts[int(split_img_ctrl_pts[i].split()[0])] \
                += split_img_ctrl_pts[i].split()[1] + ',' \
                + split_img_ctrl_pts[i].split()[2] \
                + ' ' + split_trafo_r_out[i].split()[0] + ',' \
                + split_trafo_r_out[i].split()[1] + ' '
        pto_opt = open(pto_file, 'r', encoding='utf-8').read()
        for i in range(0, len(input_files)):
            print('morphing image: ' + str(i))
            subprocess.call(['convert', input_files[i], '-compress', 'LZW', '-distort',
                            'Shepards', ctrlPts[i],
                            tmp + os.sep + 'm' + str(i) + '.tif'])
            pto_opt = pto_opt.replace(input_files[i], tmp + '/m' + str(i) + '.tif')
        open(pto_file, 'w', encoding='utf-8').write(pto_opt)

    ##############
    #### TODO ####
    ##############
    """
    > linefind
    Find vertical lines in images.
    ...
    """

    """
    > geocpset
    Set geometric control points.

     -e, --each-overlap         By default, geocpset will only work on the overlap of unconnected images. With this switch it will work on all overlaps without control points.
     -m, --minimum-overlap=NUM  Take only these images into account where the overlap is bigger than NUM percent (default 10).
    """

    """
    > pto_mask
    Add mask to pto project.

     --mask=filename@imgNr  Read the mask from the file and
                            assign the mask to given image
     --rotate=CLOCKWISE|90|COUNTERCLOCKWISE|-90
                            Rotates the mask clock- or counterclockwise
     --process==CLIP|SCALE|PROP_SCALE
                            Specify how the mask should be modified
                            if the mask is create for an image with
                            different size.
                            * CLIP: clipping (Default)
                            * SCALE: Scaling width and height individually
                            * PROP_SCALE: Proportional scale
     --delete-mask=maskNr@imgNr|ALL@imgNr|ALL
                            Removes the specified mask(s)
    """

    """
    > pano_trafo
    Transform images according to a pto file.
    """

    """
    > pto_lensstack
    Create a lensstack from a pto file.
    """

# ***************************************************************** #
# ***************************************************************** #
# ***************************************************************** #

class GridSets:
    # Returns specific sets given partial or full grids.
    # @staticmethod
    # def grid_has_no_empty_values(grid):
    #     return all(all(cell not in (None, '', [], {}) for cell in row) for row in grid)

    @staticmethod
    def validate_array_items_pattern(arr):
        pattern = re.compile(r"^[A-Z]\d{1,2}$")
        return all(isinstance(item, str) and pattern.match(item) for item in arr)

    @staticmethod
    def validate_grid_completeness(grid):
        if not grid or not all(isinstance(row, list) for row in grid):
            return False  # must be a list of lists

        num_cols = len(grid[0])
        for i, row in enumerate(grid):
            if len(row) != num_cols:
                raise ValueError("Grid has inconsistent row lengths.")
            expected_row_label = chr(ord('A') + i)
            for j, item in enumerate(row):
                expected_value = f"{expected_row_label}{j + 1}"
                if item != expected_value:
                    raise ValueError("Grid cells don't follow the expected pattern of letters for rows, numbers for columns.")
        return True

    """
    Given an array like ['A1', 'B3', 'C2'], builds a matrix (list of lists)
    with the appropriate size, inserting values at their correct positions
    and filling missing positions with None.
    """
    @staticmethod
    def build_matrix_from_cells(cells):
        # Parse the cells into (row_index, col_index) tuples
        parsed = []
        for cell in cells:
            if len(cell) < 2 or not cell[0].isalpha() or not cell[1:].isdigit():
                raise ValueError(f"Invalid cell format: {cell}")
            row_char = cell[0].upper()
            col_num = int(cell[1:])
            row_index = string.ascii_uppercase.index(row_char)
            col_index = col_num - 1  # zero-based index
            parsed.append((row_index, col_index, cell))

        # Determine matrix size
        max_row = max(r for r, _, _ in parsed)
        max_col = max(c for _, c, _ in parsed)

        # Create matrix filled with None
        matrix = [[None for _ in range(max_col + 1)] for _ in range(max_row + 1)]

        # Fill in known values
        for r, c, val in parsed:
            matrix[r][c] = val

        return matrix

    @staticmethod
    def quadruplets(grid, use_alphabetical_rows=True):
        GridSets.validate_grid_completeness(grid)
        rows = len(grid)
        cols = len(grid[0])

        combinations = []
        for col in range(cols - 1):
            for row in range(rows - 1):
                mat = [
                    [row + 1, col + 1],
                    [row + 1, col + 2],
                    [row + 2, col + 1],
                    [row + 2, col + 2],
                ]
                combinations.append(GridSets._convert_mat_to_str_array(mat, use_alphabetical_rows))
        return combinations

    @staticmethod
    def inverted_diagonal_couples(grid, use_alphabetical_rows=True):
        GridSets.validate_grid_completeness(grid)
        rows = len(grid)
        cols = len(grid[0])

        combinations = []

        for col in range(cols - 1):
            for row in range(rows - 1):
                mat = []
                if not row % 2:
                    mat = [
                        [row + 1, col + 2],
                        [row + 2, col + 1],
                    ]
                else:
                    mat = [
                        [row + 1, col + 1],
                        [row + 2, col + 2],
                    ]
                combinations.append(GridSets._convert_mat_to_str_array(mat, use_alphabetical_rows))
        return combinations

    @staticmethod
    def last_adjacent_neighbours(grid):
        # Empty or single element grid
        if len(grid) == 0 or (len(grid) == 1 and utils.count_valid_elements(grid[0]) <= 1):
            return []

        # First row, with at least two elements
        if len(grid) == 1 and len(grid[0]) > 1:
            (cell, col) = utils.get_last_valid_element(grid[0])
            return [grid[0][col], grid[0][col - 1]]

        # More than one row from now on
        rows = len(grid)

        # Last row contains a single valid element, return only element above
        if utils.count_valid_elements(grid[-1]) == 1:
            cell, col = None, None  # Initialize variables

            if rows % 2: # Odd rows (3, 5, 7...)
                (cell, col) = utils.get_last_valid_element(grid[-1])
            else: # Even rows (2, 4, 6, 8...)
                (cell, col) = utils.get_first_valid_element(grid[-1])

            if cell is not None and col is not None and grid[-2]:
                return [
                    cell,
                    grid[-2][col]
                ]
            else:
                raise ValueError("Invalid column or grid structure.")

        # All other instances will return side and up
        if rows % 2:
            (cell, col) = utils.get_last_valid_element(grid[-1])
            return [
                cell,
                grid[-2][col],
                grid[-1][col - 1]
            ]
        else:
            (cell, col) = utils.get_first_valid_element(grid[-1])
            return [
                cell,
                grid[-2][col],
                grid[-1][col + 1]
            ]

    @staticmethod
    def _convert_mat_to_str_array(mat, use_alphabetical_rows=True):
        if use_alphabetical_rows:
            mat = [f"{utils.alpha_converter(item[0])}{item[1]}" for item in mat]
        else:
            mat = [f"{item[0]}{item[1]}" for item in mat]
        return mat

# ***************************************************************** #
# ***************************************************************** #
# ***************************************************************** #

class InputSanitizer:
    def sanitize(self):
        pass






def main():
    parser = argparse.ArgumentParser(description="Large format image creation tools.")

    parser.add_argument(
        '-p', '--project',
        dest='project',
        default=None,
        help='Project name (default: timestamp)'
    )
    parser.add_argument(
        '-f', '--fov',
        dest='fov',
        default=None,
        help='HFOV (default: determined by strategy)'
    )
    parser.add_argument(
        '--stitch',
        action='store_true',
        help='Stitch images automatically.'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode.'
    )
    parser.add_argument(
        "strategy",
        choices=["petroff", "quadruplet", "prealigned", "sequential"],
        help="Which stitching strategy to use."
    )
    parser.add_argument(
        'input',
        metavar='N',
        nargs='*',
        help='Input files (supports glob patterns) or a single folder path.'
    )

    args = parser.parse_args()

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

    kwargs = {}
    if args.fov is not None:
        kwargs['fov'] = args.fov

    if args.strategy == "petroff":
        image_stitcher.strategy_petroff(stitch=args.stitch, **kwargs)
    elif args.strategy == "quadruplet":
        image_stitcher.strategy_quadruplet(stitch=args.stitch, **kwargs)
    elif args.strategy == "prealigned":
        image_stitcher.strategy_prealigned(stitch=args.stitch, **kwargs)
    elif args.strategy == "sequential":
        image_stitcher.strategy_sequential(**kwargs)
    elif args.strategy == "stitch-only" and input_str:
        image_stitcher.stitch(input_str)

if __name__ == "__main__":
    main()
