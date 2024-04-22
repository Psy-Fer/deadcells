#!/usr/bin/env python3

import argparse
import sys
import os
import numpy as np
import pyslow5
import pod5

import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams['figure.figsize'] = [20.0, 12.0]

from ._version import __version__


def detector(sig, readID, args):
    '''
    detect signal feature
    '''

    mean = np.mean(sig)
    stdev = np.std(sig)
    # this sets the threshold for detection
    bot = mean - (stdev * args.std_scale)

    cands = []     # candidates [pos]
    for i in range(len(sig)):
        a = sig[i]
        if a > bot: # If datapoint is above threshold, continue
            continue
        # add to candidate list
        cands.append(i)

    print("{}\t{}".format(readID, ",".join(str(i) for i in cands)))
    if args.plot:
        view_segs(cands, mean, bot, sig, readID, args)
         


# changed from axvline to span
def view_segs(cands, mean, bot, sig, readID, args):
    '''
    View the points in signal
    '''
    # candidate padding around detected position for nice visualisation
    pad = args.padding
    # set up plot
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    plt.title(readID)

    # plot the signal
    plt.plot(sig, color='k')

    # Show candidate regions using padding
    for c in cands:
        # ax.axvline(x=c, color='blue')
        ax.axvspan(c-pad, c+pad, alpha=0.5, color='orange')

    # plot the mean and the bot threshold
    ax.axhline(y=mean, color='green')
    ax.axhline(y=bot, color='red')

    # show the plot
    plt.show()
    plt.clf()


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help(sys.stderr)
        sys.exit(2)

def main():

    VERSION = __version__

    parser = MyParser(description="Detecting signals that indicate a dead sample",
    epilog='''
           ''',
    formatter_class=argparse.RawTextHelpFormatter)
    # using raw text to allow for new lines on main help
    # formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # main program args
    parser.add_argument("-s", "--slow5",
                        help="slow5 file for input")
    parser.add_argument("-p", "--pod5",
                        help="pod5 file for input")
    parser.add_argument("-c", "--std_scale", type=float, default=3.0,
                        help="scale for std deviation")
    parser.add_argument("--padding", type=int, default=50,
                        help="padding around detected candidates")
    parser.add_argument("--plot", action="store_true",
                        help="live plotting")
    parser.add_argument("-V", "--version", action='version', version="deadcells version: {}".format(VERSION),
                        help="Prints version")

    args = parser.parse_args()

    # print help if no args given
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    print("args: {}", args, file=sys.stderr)
    
    if args.slow5:
        s5 = pyslow5.Open(args.slow5, 'r')
        reads = s5.seq_reads(pA=True, aux='all')
        for read in reads:
            readID = read['read_id']
            sig = read['signal']
            detector(sig, readID, args)

    elif args.pod5:
        print("Pod5 support not yet implemented, pleas use slow5 (can convert with blue-crab)", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        print("input file not give. Please provide a --slow5 or --pod5 arg with corresponding file", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    print("\n\nDone!", file=sys.stderr)




if __name__ == '__main__':
    main()
