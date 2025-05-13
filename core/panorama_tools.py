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
from pathlib import Path
from core.console import Console, PathConverter
import core.utils as utils



















# class PtoTools:
#     def __init__(self, project_name=None, debug=False):
#         self._project_name = project_name or utils.current_unix_timestamp()
#         self._pto_file = f"{self._project_name}.pto"
#         self._debug = debug

#         self._tmp_dir_obj = tempfile.TemporaryDirectory()
#         self._tmp_dir = self._tmp_dir_obj.name

#         # Match instance methods names to the static ones
#         self.pto_gen = self._pto_gen
#         self.pto_merge = self._pto_merge
#         self.cpfind = self._cpfind
#         self.pto_var = self._pto_var
#         self.cpclean = self._cpclean
#         self.autooptimiser = self._autooptimiser
#         self.pano_modify = self._pano_modify
#         self.nona = self._nona
#         self.enblend = self._enblend

#     @property
#     def pto_file(self):
#         return self._pto_file

#     """
#     > hugin_executor
#     Execute a hugin command.

#     Usage: hugin_executor [-h] [-a] [-s] [-t <num>] [-p <str>] [-u <str>] [--user-defined-assistant <str>] [-d] input.pto
#     -h, --help                            shows this help message
#     -a, --assistant                       execute assistant
#     -s, --stitching                       execute stitching with given project
#     -t, --threads=<num>                   number of used threads
#     -p, --prefix=<str>                    prefix used for stitching
#     -u, --user-defined-output=<str>       use user defined commands in given file
#     --user-defined-assistant=<str>        use user defined assistant commands in given file
#     -d, --dry-run                         only print commands
#     """
#     def hugin_executor(self, args=[]):
#         pass

#     """
#     > pto_gen
#     Generate project file from images.

#     -p, --projection=INT                Projection type (default: read from database)
#     -f, --fov=FLOAT                     Horizontal field of view of images default: read from database
#     --ignore-fov-rectilinear            Don't read fov for rectilinear images from the database,
#                                         instead use only the values from EXIF data
#     -c, --crop=left,right,top,bottom    Sets the crop of input images (especially for fisheye lenses)
#     -s, --stacklength=INT               Number of images in stack (default: automatic detection)
#     -l, --linkstacks                    Link image positions in stacks
#     --distortion                        Try to load distortion information from lens database
#     --vignetting                        Try to load vignetting information from lens database
#     --sort                              Sort the files by name alphanumeric otherwise the images
#                                         are processed in the order given at the command line
#     """
#     @staticmethod
#     def pto_gen(input_files, output_pto_file, args=[]):
#         print(f"Creating project file {output_pto_file} with images:", input_files)
#         print("Running pto_gen with args:", args)
#         Console.wsl(["pto_gen"]  + args + [
#             "-o", output_pto_file
#         ] + input_files)
#         return output_pto_file

#     def _pto_gen(self, input_files, args=[]):
#         return PtoTools.pto_gen(input_files, self._pto_file, args)

#     """
#     > pto_merge
#     Merges several project files.
#     """
#     @staticmethod
#     def pto_merge(input_pto_files=None, output_pto_file=None):
#         """
#         Run enblend stitching.

#         Supports:
#         - pto_merge(input_pto_files: list|str)
#         - pto_merge(input_pto_files: str)
#         - pto_merge(input_pto_files: liststr, images: list or folder_path, options: list)
#         """

#         if not output_pto_file:
#             output_pto_file = f"{self._project_name}_merged.pto"

#         if not input_pto_files:
#             input_pto_files = glob.glob("*.pto")

#         # print(f"Running pto_merge with args:", args)
#         Console.wsl([
#             "pto_merge",
#             "-o", output_pto_file,
#         ] + input_pto_files)

#         return output_pto_file

#     def _pto_merge(self, input_pto_files, output_pto_file=None):
#         output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_pto_merge.pto"
#         self._debug_pto = output_pto_file
#         return PtoTools.pto_merge(input_pto_files)

#     """
#     > cpfind
#     Control point detector.

#     Matching strategy (these options are mutually exclusive)
#     --linearmatch   Enable linear images matching
#                     Can be fine tuned with
#         --linearmatchlen=<int>  Number of images to match (default: 1)
#     --multirow      Enable heuristic multi row matching
#     --prealigned    Match only overlapping images,
#                     requires a rough aligned panorama

#     Feature description options
#     --sieve1width=<int>    Sieve 1: Number of buckets on width (default: 10)
#     --sieve1height=<int>   Sieve 1: Number of buckets on height (default: 10)
#     --sieve1size=<int>     Sieve 1: Max points per bucket (default: 100)
#     --kdtreesteps=<int>          KDTree: search steps (default: 200)
#     --kdtreeseconddist=<double>  KDTree: distance of 2nd match (default: 0.25)

#     Feature matching options
#     --minmatches=<int>     Minimum matches (default: 6)
#     --sieve2width=<int>    Sieve 2: Number of buckets on width (default: 5)
#     --sieve2height=<int>   Sieve 2: Number of buckets on height (default: 5)
#     --sieve2size=<int>     Sieve 2: Max points per bucket (default: 1)

#     Caching options
#     -c|--cache    Caches keypoints to external file
#     --clean       Clean up cached keyfiles
#     -p|--keypath=<string>    Store keyfiles in given path
#     -k|--writekeyfile=<int>  Write a keyfile for this image number
#     --kall                   Write keyfiles for all images in the project

#     Run --help for more information.
#     """
#     @staticmethod
#     def cpfind(pto_file, output_pto_file=None, args=[]):
#         if not output_pto_file:
#             output_pto_file = pto_file

#         print("Running cpfind with args:", args)
#         Console.wsl(["cpfind"] + args + [
#             "-o", output_pto_file,
#             pto_file
#         ])
#         return output_pto_file

#     def _cpfind(self, args=[]):
#         input_pto_file = self._pto_file if not self._debug else self._debug_pto_file
#         self._debug_pto_file = f"{self._project_name}_cpfind.pto"
#         output_pto_file = self._pto_file if not self._debug else self._debug_pto_file
#         return PtoTools.cpfind(self._pto_file, output_pto_file, args)

#     """
#     > pto_var
#     Change image variables inside pto files.

#     --opt varlist           Change optimizer variables
#     --modify-opt            Modify the existing optimizer variables (without pto_var will start with an empty variables set)
#                             Examples:
#         --opt=y,p,r         Optimize yaw, pitch and roll of all images (special treatment for anchor image applies)
#         --opt=v0,b2         Optimize hfov of image 0 and barrel distortion of image 2
#         --opt=v,!v0         Optimize field of view for all images except for the first image
#         --opt=!a,!b,!c      Don't optimise distortion (works only with switch --modify-opt together)

#     --link varlist          Link given variables
#                             Example:
#         --link=v3           Link hfov of image 3
#         --link=a1,b1,c1     Link distortions parameter for image 1

#     --unlink varlist        Unlink given variables
#                             Examples:
#         --unlink=v5         Unlink hfov for image 5
#         --unlink=a2,b2,c2   Unlink distortions parameters for image 2

#     --set varlist           Sets variables to new values
#                             Examples:
#         --set=y0=0,r0=0,p0=0  Resets position of image 0
#         --set=Vx4=-10,Vy4=10  Sets vignetting offset for image 4
#         --set=v=20            Sets the field of view to 20 for all images
#         --set=y=val+20        Increase yaw by 20 deg for all images
#         --set=v=val*1.1       Increase fov by 10 % for all images
#         --set=y=i*20          Set yaw to 0, 20, 40, ...
#     --set-from-file filename  Sets variables to new values
#                             It reads the varlist from a file

#     --crop=left,right,top,bottom Set the crop for all images
#     --crop=width,height       Set the crop for all images and activate
#                             autocenter for crop
#                             relative values can be used with %
#     --crop=iNUM=left,right,top,bottom Set the crop for image NUM
#     --crop=iNUM=width,height  Set the crop for image NUM and
#                             activate autocenter for crop
#                             These switches can be used several times.

#     --anchor=NUM            Sets the image NUM as anchor for geometric
#                             optimisation.
#     --color-anchor=NUM      Sets the image NUM as anchor for photometric
#                             optimisation.

#     Run --help for more information.
#     """
#     def pto_var(pto_file, output_pto_file=None, args=[]):
#         if not output_pto_file:
#             output_pto_file = pto_file

#         print("Running pto_var with args:", args)
#         Console.wsl(["pto_var"] + args + [
#             "-o", output_pto_file,
#             pto_file
#         ])
#         return output_pto_file

#     def _pto_var(self, args=[]):
#         output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_pto_var.pto"
#         return PtoTools.pto_var(self._pto_file, output_pto_file, args)

#     """
#     > cpclean
#     Remove wrong control points by statistic method.
#     Step 1: Do image pair control point checking.
#     Step 2: Do whole panorama control point checking.

#     --max-distance|-n num       Distance factor for checking (default: 2) (cps with an error mean + this factor*sigma will be removed)
#     --pairwise-checking|-p      Do only images pairs cp checking (skip step 2)
#     --whole-pano-checking|-w    Do only whole panorama cp checking (skip step 1)
#     --dont-optimize|-s          Skip optimisation step when checking the whole panorama (only step 2)
#     --check-line-cp|-l          Also include line control points for calculation and filtering in step 2
#     """
#     @staticmethod
#     def cpclean(pto_file, output_pto_file=None, args=[]):
#         if not output_pto_file:
#             output_pto_file = pto_file

#         print("Running cpclean with args:", args)
#         Console.wsl(["cpclean"] + args + [
#             "-o", output_pto_file,
#             pto_file
#         ])
#         return output_pto_file

#     def _cpclean(self, args=[]):
#         output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_cpclean.pto"
#         return PtoTools.cpclean(self._pto_file, output_pto_file, args)

#     """
#     > autooptimiser
#     Optimize image positions.

#     -a  Auto align mode, includes various optimisation stages, depending on the amount and distribution of the control points
#     -p  Pairwise optimisation of yaw, pitch and roll, starting from first image
#     -m  Optimise photometric parameters
#     -n  Optimize parameters specified in script file (like PTOptimizer)

#     Run --help for more information.
#     """
#     @staticmethod
#     def autooptimiser(pto_file, output_pto_file=None, args=[]):
#         if not output_pto_file:
#             output_pto_file = pto_file
#         Console.wsl(["autooptimiser"] + args + [
#             "-o", output_pto_file,
#             pto_file
#         ])
#         return output_pto_file

#     def _autooptimiser(self, args=[]):
#         output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_autooptimiser.pto"
#         return PtoTools.autooptimiser(self._pto_file, output_pto_file, args)

#     """
#     > pano_modify
#     Change output parameters of project file.

#     -p, --projection=x                  Sets the output projection to number x
#     --projection-parameter=x            Sets the parameter of the projection
#                                         (Several parameters are separated by
#                                         space or comma)
#     --fov=AUTO|HFOV|HFOVxVFOV           Sets field of view
#                                         AUTO: calculates optimal fov
#                                         HFOV|HFOVxVFOV: set to given fov
#     -s, --straighten                    Straightens the panorama
#     -c, --center                        Centers the panorama
#     --canvas=AUTO|num%|WIDTHxHEIGHT     Sets the output canvas size
#                                         AUTO: calculate optimal canvas size
#                                         num%: scales the optimal size by given percent
#                                         WIDTHxHEIGHT: set to given size
#     --crop=AUTO|AUTOHDR|AUTOOUTSIDE|left,right,top,bottom|left,right,top,bottom%
#                                         Sets the crop rectangle
#                                         AUTO: autocrop panorama
#                                         AUTOHDR: autocrop HDR panorama
#                                         AUTOOUTSIDE: autocrop outside of all images
#                                         left,right,top,bottom: to given size
#                                         left,right,top,bottom%: to size relative to canvas
#     --output-type=str                   Sets the type of output
#                                         Valid items are
#                                         NORMAL|N: normal panorama
#                                         STACKSFUSEDBLENDED|BF: LDR panorama with
#                                             blended stacks
#                                         EXPOSURELAYERSFUSED|FB: LDR panorama with
#                                             fused exposure layers (any arrangement)
#                                         HDR: HDR panorama
#                                         REMAP: remapped images with corrected exposure
#                                         REMAPORIG: remapped images with
#                                             uncorrected exposure
#                                         HDRREMAP: remapped images in linear color space
#                                         FUSEDSTACKS: exposure fused stacks
#                                         HDRSTACKS: HDR stacks
#                                         EXPOSURELAYERS: blended exposure layers
#                                         and separated by a comma.
#     --rotate=yaw,pitch,roll             Rotates the whole panorama with the given angles
#     --translate=x,y,z                   Translate the whole panorama with the given values
#     --interpolation=int                 Sets the interpolation method

#     Run --help for more information.
#     """
#     @staticmethod
#     def pano_modify(pto_file, output_pto_file=None, args=[]):
#         if not output_pto_file:
#             output_pto_file = pto_file
#         Console.wsl(["pano_modify"] + args + [
#             "-o", output_pto_file,
#             pto_file
#         ])
#         return output_pto_file

#     def _pano_modify(self, args=[]):
#         output_pto_file = self._pto_file if not self._debug else f"{self._project_name}_pano_modify.pto"
#         return PtoTools.pano_modify(self._pto_file, output_pto_file, args)

#     """
#     > nona
#     Stitch a panorama image. It uses the transform function from PanoTools.

#     nona [options] -o output project_file (image files)

#     Run --help for more information.
#     """
#     @staticmethod
#     def nona(pto_file, output_folder=None, args=[]):
#         if not output_folder:
#             output_folder = f"{FileSystemUtils.get_filename_without_extension(pto_file)}_remapped"

#         print("Running nona...")
#         Console.wsl(["nona"] + args + [
#             "-o", output_folder,
#             pto_file
#         ])
#         print(f"Output folder: {output_folder}")
#         return output_folder

#     def _nona(self, args=[]):
#         if self._debug:
#             output_folder = f"{self._project_name}_nona"
#             os.makedirs(output_folder, exist_ok=True)
#         else:
#             output_folder = self._tmp_dir

#         self._remapped_folder = output_folder
#         return PtoTools.nona(self._pto_file, output_folder + os.sep + "remapped", args)

#     """
#     > enblend
#     Blend INPUT images into a single IMAGE.

#     enblend [options] [--output=IMAGE] INPUT...

#     Run --help for more information.
#     """
#     @staticmethod
#     def enblend(output=None, images=None, options=[]):
#         """
#         Run enblend stitching.

#         Supports:
#         - enblend(images: list)
#         - enblend(path: str)
#         - enblend(output: str, images: list or str, [options: list])
#         """
#         args = [arg for arg in [output, images, options] if arg]
#         args_len = len(args)
#         if args_len == 0:
#             print("Error: enblend requires at least one argument.", file=sys.stderr)
#             sys.exit(1)
#         elif args_len == 1:
#             if isinstance(args[0], list):
#                 images = args[0]
#                 output = f"output_{utils.current_unix_timestamp()}"
#             elif isinstance(args[0], str):
#                 if os.path.isdir(args[0]):
#                     images =    glob.glob(os.path.join(args[0], '*.tif')) + \
#                                 glob.glob(os.path.join(args[0], '*.tiff'))
#                 else:
#                     print("Error: enblend requires a folder or a set of images as input.", file=sys.stderr)
#                     sys.exit(1)
#                 output = FileSystemUtils.get_filename_without_extension_or_final_folder(args[0])
#         else:
#             output  = FileSystemUtils.get_filename_without_extension_or_final_folder(args[0])
#             if isinstance(args[1], str):
#                 images =    glob.glob(os.path.join(args[1], '*.tif')) + \
#                             glob.glob(os.path.join(args[1], '*.tiff'))
#             elif isinstance(args[1], list):
#                 images  = args[1]
#             else:
#                 print("Error: enblend requires a folder or a set of images as input.", file=sys.stderr)
#                 sys.exit(1)
#             options = args[2]

#         output += ".tif"
#         print("Running enblend...")
#         Console.wsl(["enblend"] + options + ["-o", output ] + images)
#         print(f"Output: {output}")
#         return output

#     def _enblend(self, options=[]):
#         image_folder = self._remapped_folder + os.sep + "remapped*"
#         return PtoTools.enblend(self._project_name, image_folder, options)

#     @staticmethod
#     def morph_images_to_fit_control_points(pto_file, input_files, tmp):
#         # Should be handled by Console class
#         import subprocess

#         img_ctrl_pts = ''
#         with open(pto_file) as input:
#             for line in input:
#                 if line[0] == 'c':
#                     img1 = line.split('n')[1].split()[0]
#                     img2 = line.split('N')[1].split()[0]
#                     x1 = line.split('x')[1].split()[0]
#                     x2 = line.split('X')[1].split()[0]
#                     y1 = line.split('y')[1].split()[0]
#                     y2 = line.split('Y')[1].split()[0]
#                     img_ctrl_pts += img1 + ' ' + x1 + ' ' + y1 + '\n' \
#                                 + img2 + ' ' + x2 + ' ' + y2 + '\n'
#         pipe = subprocess.Popen(['pano_trafo', pto_file], stdout=subprocess.PIPE,
#                                 stdin=subprocess.PIPE)
#         trafo_out = (pipe.communicate(input
#                                     = img_ctrl_pts.encode('utf-8'))[0]).decode('utf-8')
#         split_img_ctrl_pts = img_ctrl_pts.splitlines()
#         split_trafo_out = trafo_out.splitlines()
#         morphed_split_trafo_out = [''] * len(split_trafo_out)
#         for i in range(0, int(len(split_trafo_out) / 2)):
#             i1 = split_img_ctrl_pts[i*2].split()[0]
#             i2 = split_img_ctrl_pts[i*2+1].split()[0]
#             x = (float(split_trafo_out[i*2].split()[0]) \
#                 + float(split_trafo_out[i*2+1].split()[0])) / 2
#             y = (float(split_trafo_out[i*2].split()[1]) \
#                 + float(split_trafo_out[i*2+1].split()[1])) / 2
#             morphed_split_trafo_out[i*2] = i1 + ' ' + str(x) + ' ' + str(y)
#             morphed_split_trafo_out[i*2+1] = i2 + ' ' + str(x) + ' ' + str(y)
#         trafo_r_in = "\n".join(morphed_split_trafo_out)
#         pipe = subprocess.Popen(['pano_trafo', '-r', pto_file], stdout=subprocess.PIPE,
#                                 stdin=subprocess.PIPE)
#         trafo_r_out = (pipe.communicate(input
#                                     = trafo_r_in.encode('utf-8'))[0]).decode('utf-8')
#         split_trafo_r_out = trafo_r_out.splitlines()
#         ctrlPts = [''] * len(input_files)
#         for i in range(0, len(split_trafo_r_out)):
#             ctrlPts[int(split_img_ctrl_pts[i].split()[0])] \
#                 += split_img_ctrl_pts[i].split()[1] + ',' \
#                 + split_img_ctrl_pts[i].split()[2] \
#                 + ' ' + split_trafo_r_out[i].split()[0] + ',' \
#                 + split_trafo_r_out[i].split()[1] + ' '
#         pto_opt = open(pto_file, 'r', encoding='utf-8').read()
#         for i in range(0, len(input_files)):
#             print('morphing image: ' + str(i))
#             subprocess.call(['convert', input_files[i], '-compress', 'LZW', '-distort',
#                             'Shepards', ctrlPts[i],
#                             tmp + os.sep + 'm' + str(i) + '.tif'])
#             pto_opt = pto_opt.replace(input_files[i], tmp + '/m' + str(i) + '.tif')
#         open(pto_file, 'w', encoding='utf-8').write(pto_opt)

#     ##############
#     #### TODO ####
#     ##############
#     """
#     > linefind
#     Find vertical lines in images.
#     ...
#     """

#     """
#     > geocpset
#     Set geometric control points.

#      -e, --each-overlap         By default, geocpset will only work on the overlap of unconnected images. With this switch it will work on all overlaps without control points.
#      -m, --minimum-overlap=NUM  Take only these images into account where the overlap is bigger than NUM percent (default 10).
#     """

#     """
#     > pto_mask
#     Add mask to pto project.

#      --mask=filename@imgNr  Read the mask from the file and
#                             assign the mask to given image
#      --rotate=CLOCKWISE|90|COUNTERCLOCKWISE|-90
#                             Rotates the mask clock- or counterclockwise
#      --process==CLIP|SCALE|PROP_SCALE
#                             Specify how the mask should be modified
#                             if the mask is create for an image with
#                             different size.
#                             * CLIP: clipping (Default)
#                             * SCALE: Scaling width and height individually
#                             * PROP_SCALE: Proportional scale
#      --delete-mask=maskNr@imgNr|ALL@imgNr|ALL
#                             Removes the specified mask(s)
#     """

#     """
#     > pano_trafo
#     Transform images according to a pto file.
#     """

#     """
#     > pto_lensstack
#     Create a lensstack from a pto file.
#     """

