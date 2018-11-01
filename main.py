import argparse
import os
from examples import run_example

def build_arg_parser():
    parser = argparse.ArgumentParser(prog='snapshot-threads')
    # parser.add_argument('-e', '--example', choices=[1], default=1,
    #                     type=int, help='Example to run', metavar='num')
    parser.add_argument('-d', '--snapshot-dir', default='snapshots',
                        type=str, help='Save directory', metavar='path')

    # TODO: add num incrementors and send prop as command line args
    subparsers = parser.add_subparsers(title='example', dest='example')
    example_1_parser = subparsers.add_parser('1')
    example_1_parser.add_argument('-n', '--num-incs', default=2, type=int,
                                  help='Number of Incrementor actors',
                                  metavar='num')
    example_1_parser.add_argument('-p', '--send-probs', required=True,
                                  type=float, nargs='+', metavar='float',
                                  help='Probability of sending a message to a neighbor')
    
    return parser

def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    print(vars(args))

    if not os.path.exists(args.snapshot_dir):
        os.mkdir(args.snapshot_dir)

    with open('snapshotting/config/snapshotdir.txt', 'w') as f:
        f.write(os.path.abspath(args.snapshot_dir))

    run_example(vars(args))

if __name__ == '__main__':
    main()

