import argparse
import subprocess
import os
import glob
import sys
import string
import tempfile
from console import Console
import core.utils as utils
from core.utils import ImageUtils, FileSystemUtils

class ImageStitcher:
    def __init__(self, pto_file):
        self.pto_file = pto_file
        self.pto_tools = PtoTools(self.pto_file)
        self.pto_tools.pto_gen()
        # fullgrid > All images already scanned, cpfind multirow in sets of 4
            # HFOV??
        # partialgrid > Real-time scanning, cpfind multirow with existent neighbors + extra diagonals
        # manual prealigned
        # linearmatch + prealigned
        # default?
        # self.mode¿
        #debug activated, save pto_files at every step
        pass
    def method_petroff(self):
        # Make temporary directory
        tmp_dir = tempfile.TemporaryDirectory()
        tmp = tmp_dir.name
        print(f"Temporary directory: {tmp}")

        # use_wsl


        # pto_mask --process=CLIP --mask=mask.msk@0 --mask=mask.msk@1 --mask=mask.msk@2 --mask=mask.msk@3 --mask=mask.msk@4 --mask=mask.msk@5 --mask=mask.msk@6 --mask=mask.msk@7 --output=scripting_step3_masks.pto scripting_step2_align_rows_and_columns.pto
# cpfind --prealigned --fullscale --cache --output=scripting_step4_prealigned_cpfind.pto scripting_step3_masks.pto

        # Find control points
        # --- Analyze Images ---
        # --- Find matches ---
        # --- Find matches for overlapping images ---
        self.run_cpfind(pto_file, mode='multirow')

        subprocess.call(['cpfind', '--fullscale', '--multirow', '--sieve1size', '500',
                        '--sieve2width', '20', '--sieve2height', '20', '-o', pto_file,
                        pto_file])

        # Set image parameters to optimize
        # Updating optimizer variables
        subprocess.call(['pto_var', '--opt', 'r,TrX,TrY', '-o', pto_file, pto_file])

        # Remove incorrect control points
        # Step 1: Do image pair control point checking...
        # Step 2: Do whole panorama control point checking...
        subprocess.call(['cpclean', '-n', '1', '-o', pto_file, pto_file])
        subprocess.call(['cpclean', '-o', pto_file, pto_file])

        # Optimize rotation and x, y translation
       # optimize position
        # *** Optimising parameters specified in PTO file
        # Optimizing Variables
        subprocess.call(['autooptimiser', '-n', '-o', pto_file, pto_file])

        # _morph_images_to_fit_control_points
        # Stitch images
        # === 6. Modify for canvas size and cropping ===
        subprocess.call(['pano_modify', '-p', '0', '--fov=AUTO', '--canvas=AUTO',
                        '--crop=AUTO', '-o', pto_file, pto_file])

        #pano_modify --projection=0 --center

        # linefind --output=scripting_step5_vertical-lines.pto scripting_step4_prealigned_cpfind.pto

        # optional
        # geocpset --each-overlap --output=scripting_step6_geocpset.pto scripting_step5_vertical-lines.pto

        # autooptimiser -a -m --output=scripting_step7_autoptimized.pto scripting_step6_geocpset.pto

        # hugin scripting_step7_autoptimized.pto

        # here it takes longer
        subprocess.call(['nona', '-o', tmp + os.sep + 'remapped', pto_file])
        subprocess.call(['enblend', '--primary-seam-generator=graph-cut', '-o',
                        args.output.split('.')[0] + '.tif']
                        + glob.glob(tmp + os.sep + 'remapped*'))


    def method_real_time_generation(self):
        pass

    def method_quadruplet(self):
        pass

    def method_yaw_and_pitch_repositioning(self):
        pass


    def apply_yaw_pitch_to_pto(pto_file, matrix):
        temp_pto = pto_file + '.tmp'

        index = 0
        for row in matrix:
            for cell in row:
                if not cell:
                    continue
                # cell = (value, fname, orientation_degrees, yaw, pitch)
                _, _, roll, yaw, pitch = cell
                subprocess.call([
                    'pto_var',
                    '-o', temp_pto,
                    '--set', f"y{index}={yaw},p{index}={pitch},r{index}={roll}",
                    pto_file
                ])
                # Overwrite original for next call
                os.replace(temp_pto, pto_file)
                index += 1




class PtoTools:
    def __init__(self, project_name=None, debug=False):
        self._project_name = project_name or utils.current_unix_timestamp()
        self._pto_file = f"{self._project_name}.pto"
        self._debug = debug

    def pto_gen(self, input_files=None, fov=5):
        output_file = self._pto_file if not self._debug else f"{self._project_name}_pto_gen.pto"

        if input_files is None:
            # Case 1: No input_files specified, use current directory
            input_files = FileSystemUtils.get_images_from_dir(".")
        elif isinstance(input_files, str) and os.path.isdir(input_files):
            # Case 2: A directory path was passed
            input_files = FileSystemUtils.get_images_from_dir(input_files)
        elif isinstance(input_files, list):
            # Case 3: A list of files
            input_files = input_files
        else:
            raise ValueError("input_files must be None, a directory path, or a list of files.")

        Console.run([
            "pto_gen",
            f"--fov={fov}",
            "-o", output_file
        ] + input_files)

    def cpfind(
        self,
        pto_file,
        mode="multirow",
        sieve1size="500",
        sieve2width="20",
        sieve2height="20",
        output_pto_file=False
    ):
        allowed_modes = {"prealigned", "multirow", "linearmatch"}
        if mode not in allowed_modes:
            raise ValueError(f"Invalid mode '{mode}'. Allowed modes are: {', '.join(allowed_modes)}")

        if not output_pto_file:
            output_pto_file = FileSystemUtils.get_filename_without_extension_or_final_folder(pto_file) + "_cpfind_output.pto"

        subprocess.run([
            "cpfind",
            f"--{mode}",
            "--sieve1size", sieve1size,
            "--sieve2width", sieve2width,
            "--sieve2height", sieve2height,
            "-o", pto_file,
            pto_file
        ])




    # @property
    # def pto_file(self):
    #     return self._pto_file

    # @pto_file.setter
    # def pto_file(self, value):
    #     # You can add validation here if needed
    #     self._pto_file = value

    def set_parameters_to_optimize(self, pto_file, optimize_roll=True, optimize_translation=True, optimize_yaw_and_pitch=False):

        # Alt params to test: r,d,e,!r0,!d0,!e0
        params_to_optimize = []
        if optimize_roll:
            params_to_optimize.append('r')
        if optimize_translation:
            params_to_optimize.append('TrX')
            params_to_optimize.append('TrY')
        if optimize_yaw_and_pitch:
            params_to_optimize.append('y')
            params_to_optimize.append('p')

        params_to_optimize_str = ','.join(params_to_optimize)
        print(f"Optimizing parameters: {params_to_optimize_str}")

        # Set image parameters to optimize
        subprocess.call(['pto_var', '--opt', params_to_optimize_str, '-o', pto_file, pto_file])

    def Process(self):
        pass

    def _generate_matrix(self):
        pass

    def generate_matrix_from_folder(folder_path, base_value=1.0, multiplier=5, offset=-1):
        # Filter for files matching the letter-number format (e.g., A1.jpg)
        filenames = [
            f for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f)) and f[0].isalpha() and f[1].isdigit()
        ]

        positions = {}
        for fname in filenames:
            pos = parse_filename(fname)
            positions[pos] = fname

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
            orientation_degrees = ImageUtils.get_rotation_degrees(os.path.join(folder_path, fname))

            yaw = (c - avg_center_col) * multiplier   # horizontal offset scaled
            pitch = (avg_center_row - r) * multiplier # vertical offset scaled

            # Include yaw and pitch in the matrix cell
            matrix[r][c] = (f"{val:.2f}", fname, orientation_degrees, yaw, pitch)

        return matrix, values

    def parse_filename(name):
        """Parses a name like 'A1.jpg' or 'B2.png' -> (row, col)"""
        base = os.path.splitext(name)[0]
        row_letter = ''.join(filter(str.isalpha, base))
        col_number = ''.join(filter(str.isdigit, base))
        return (
            string.ascii_uppercase.index(row_letter.upper()),
            int(col_number) - 1
        )

    def find_center(cells):
        rows = sorted(set(r for r, _ in cells))
        cols = sorted(set(c for _, c in cells))
        # Find the single middle row/col if odd, or two if even
        if len(rows) % 2 == 1:
            mid_rows = [rows[len(rows)//2]]
        else:
            mid_rows = rows[len(rows)//2 - 1:len(rows)//2 + 1]

        if len(cols) % 2 == 1:
            mid_cols = [cols[len(cols)//2]]
        else:
            mid_cols = cols[len(cols)//2 - 1:len(cols)//2 + 1]

        return {(r, c) for r in mid_rows for c in mid_cols if (r, c) in cells}
















class MergeImages:
    # Different methods to blend the images
    def __init__(self, pto_file):
        pass

    def defaultMerge(self):
        pass

    def _nona(self):
        subprocess.call(['nona', '-o', tmp + os.sep + 'remapped', pto_file])

    def _enblend(self):
        pass

    def _morph_images_to_fit_control_points(pto_file, input_files, tmp):
        # Legacy step, makes process slower and does not impact final result, kept in case it's needed in some edge cases.
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

class GridSets:
    @staticmethod
    def _check_grid_completeness(grid):
        if not all(len(row) == len(grid[0]) and all(cell not in (None, '', [], {}) for cell in row) for row in grid):
            raise ValueError("Grid has inconsistent row lengths or contains empty/null values.")

    @staticmethod
    def quadruplets(grid, use_alphabetical_rows=True):
        GridSets._check_grid_completeness(grid)
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
        GridSets._check_grid_completeness(grid)
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


# wsl


































def main():
    parser = argparse.ArgumentParser(description="Large format image creation tools.")

    parser.add_argument('input_files', metavar='N', nargs='*', help='Image files to be blended together.')
    parser.add_argument('--input-dir', dest='input_dir', help='Directory containing images to use.')
    parser.add_argument('-o', '--output', dest='output', default='output', help='Output name (default: output)')
    parser.add_argument("tool", choices=["pto_gen"], help="Which tool to run")

    args = parser.parse_args()

    input_files = []
    if args.input_dir:
        if not os.path.isdir(args.input_dir):
            print(f"Error: '{args.input_dir}' is not a valid directory.", file=sys.stderr)
            sys.exit(1)
        # Collect all image files from the directory
        for file in sorted(os.listdir(args.input_dir)):
            full_path = os.path.join(args.input_dir, file)
            if os.path.isfile(full_path) and file.lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
                input_files.append(full_path)
    elif args.input_files:
        # Expand glob patterns
        for pattern in args.input_files:
            input_files += glob.glob(pattern)
    else:
        print("Error: You must specify either image files or --input-dir", file=sys.stderr)
        sys.exit(1)

    if not input_files:
        print("Error: No valid input images found.", file=sys.stderr)
        sys.exit(1)

    pto_file = args.output + '.pto'
    output_dir = args.output_dir

    if args.tool == "pto_gen":
        pto_tools = PtoTools()
        pto_tools.pto_gen(input_files, fov=5, output_file=pto_file)
        pto_tools.pto_var(pto_file, output_dir=output_dir)
    else:
        pass

if __name__ == "__main__":
    main()