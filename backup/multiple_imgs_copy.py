import serial, sys, time, glob, struct
import optparse
import numpy as np
import os
if 'TESTENVIRONMENT' in os.environ:
	import mock
	sys.modules['FLI'] = mock.Mock()
else:
	import FLI
import logging
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.time import Time
from subprocess import check_output

import mlof_filter_wheel
import mlof_take_image

def parse_commandline():
    """
    Parse the options given on the command-line.
    """
    parser = optparse.OptionParser()

    parser.add_option("-o","--output_file")
    parser.add_option("-e","--exposure_time", type=int, help="exposure time, in ms", default=0)
    parser.add_option("-n","--name", type=str, help="name of target, as it will appear in Fits header")
    parser.add_option("-s","--shutter", type=int, help="should shutter act normally, opening during exposure (0), or stay closed at all times (1)", default=0)
    parser.add_option("-g","--gain", type=int, help="Define the gain.  It can be set to 0, 1, or 2, which correspond to low, medium, or high numbers of ADUs per electron, respectively. For the PIXIS 1024R, low = (4e-/ADU), medium =(2e-/ADU), and high = (1e-/ADU).", default=0)
    parser.add_option("-r","--readout_speed", type=int, help="the readout speed.  Can be faster and noiser (1) or slower and less noisy (0).", default=0)
    parser.add_option("-t","--time", type=str)

    parser.add_option("--doTemperatureLock", action="store_true",default=False)

    parser.add_option("-m","--mask",default=0,type=int)
    parser.add_option("-f","--filter",default=0,type=int)
    parser.add_option("--doPosition", action="store_true",default=False)
    parser.add_option("--doGetPosition", action="store_true",default=False)
    
    parser.add_option("--numImgs", default=1, type=int)

    opts, args = parser.parse_args()

    return opts

if __name__ == "__main__":

    # Parse command line
    opts = parse_commandline()
    args = parse_commandline()

    if opts.doPosition:
        mlof_filter_wheel.main(runtype="position", mask=opts.mask, filter=opts.filter)
    if opts.doGetPosition:
        mlof_filter_wheel.main(runtype="getposition")
    runs = opts.numImgs
    for n in range(runs):
        configure_sasha = mlof_take_image.check_output(["which", "configure_sasha"]).decode().replace("\n","")

        source_file = args.output_file.replace("fits","raw")
        exposure_file = args.output_file.replace("fits","txt")
        filename = args.output_file.replace(".fits","")

        outdir = "/".join(args.output_file.split("/")[:-1])
        if not outdir == "" and not os.path.isdir(outdir):
            os.makedirs(outdir)

        t0 = Time.now()
        if args.doTemperatureLock:
            system_command = f"{configure_sasha} {args.exposure_time} 1 {args.shutter} {args.gain} {args.readout_speed} {filename} {filename} lock"
        else:
            system_command = f"{configure_sasha} {args.exposure_time} 1 {args.shutter} {args.gain} {args.readout_speed} {filename} {filename}"
        os.system(system_command)

        header = mlof_take_image.BuildInitialHeader(args, t0=t0, exposure_parameter_file=exposure_file)
        mlof_take_image.convertRawToFits(source_file, args.output_file+"_"+str(n), header = header);


