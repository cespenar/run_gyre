#!python

import argparse
import glob
import os
import shutil
import sys
from contextlib import contextmanager


@contextmanager
def cd(work_dir):
    original_dir = os.getcwd()
    os.chdir(os.path.expanduser(work_dir))
    try:
        yield
    finally:
        os.chdir(original_dir)


parser = argparse.ArgumentParser(conflict_handler="resolve", \
    description="Run gyre for mupltiple selected models in a directory.")
parser.add_argument("-w", "--work-dir", type=str, required=True, \
    help="Set the working directory")
parser.add_argument("-i", "--gyre-input", type=str, required=True, \
    help="The location of the gyre input script.")
parser.add_argument("-g", "--gyre-location", type=str, \
    help="The path to the gyre executable.")
parser.add_argument("-p", "--pattern", type=str, default="*.GYRE", \
    help="The pattern for glob to select the models for calcualtions.")
parser.add_argument("-o", "--out-suffix", type=str, default="_summary.txt", \
    help="The suffix of the gyre summary files.")
args = parser.parse_args()

name_pattern = args.pattern
gyre_summary_ad = "summary.txt"

gyre_env = "GYRE_DIR"
if args.gyre_location:
    gyre_exec = args.gyre_location
else:
    try:
        gyre_exec = os.environ[gyre_env] + "/bin/gyre"
    except KeyError as e:
        print(f"Environment variable GYRE_DIR is not defined! {e:s}")
        exit(1)
if not os.path.isfile(gyre_exec):
    raise FileNotFoundError(f"{gyre_exec} is not a gyre executable!")

if os.path.isfile(args.gyre_input):
     gyre_script = args.gyre_input
else:
    raise FileNotFoundError(f"{args.gyre_input} does not exist!")

with cd(args.work_dir):
    current_model = "current_model.GYRE"
    for model in sorted(glob.glob(args.pattern)):
        try:
            shutil.copyfile(model, current_model)
        except OSError as e:
            print(f"Unable to copy file. {e:s}")
            exit(1)
        except:
            print(f"Unexpected error: {sys.exc_info():s}")
            exit(1)
        
        print(f"{model:s} prepared for calculations!")

        try:
            os.system(gyre_exec + " " + gyre_script)
        except:
            print(f"Unexpected error: {sys.exc_info():s}")
            exit(1)

        gyre_result_ad = os.path.splitext(os.path.splitext(os.path.basename(model))[0])[0] \
            + args.out_suffix
        
        try:
            shutil.move(gyre_summary_ad, os.path.join(args.work_dir, gyre_result_ad))
        except:
            print(f"Unexpected error: {sys.exc_info():s}")
            exit(1)
        
        print("Model calculated\n")

    if os.path.isfile(current_model):
        os.remove(current_model)

    print("Calculations are done!")
