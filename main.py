import argparse
import os
from examples import run_example

def build_arg_parser():
    parser = argparse.ArgumentParser(prog='snapshot-threads')
    parser.add_argument('-d', '--snapshot-dir', default='snapshots',
                        type=str, help='Save directory', metavar='path')

    subparsers = parser.add_subparsers(title='example', dest='example')
    example_1_parser = subparsers.add_parser('1')
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

