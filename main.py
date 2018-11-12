import argparse
import os
from examples import run_example

def build_arg_parser():
    parser = argparse.ArgumentParser(prog='snapshot-threads')
    parser.add_argument('-d', '--snapshot-dir', default='snapshots',
                        type=str, help='Save directory', metavar='path')
    parser.add_argument('-r', '--reload', help='Reload a snapshot', action='store_true')

    subparsers = parser.add_subparsers(title='example', dest='example')
    example_1_parser = subparsers.add_parser('1')
    example_1_parser.add_argument('-p', '--send-probs', required=True,
                                  type=float, nargs='+', metavar='float',
                                  help='Probability of sending a message to a neighbor')
    
    return parser

def is_int(i):
    try:
        int(i)
        return True
    except:
        return False

def show_snapshots(snapshot_dir):
    dirs = os.listdir(snapshot_dir)
    for i, d in enumerate(dirs):
        print('[{}]:\t'.format(i), d, sep='')
        with open(snapshot_dir + '/' + d + '/info.txt', 'r') as f:
            print('\t' + f.read().replace('\n', '\n\t'))

    num = input('Choose a snapshot number: ')
    while not is_int(num) or int(num) < 0 or int(num) >= len(dirs):
        num = input('Enter a displayed integer: ')

    return snapshot_dir + '/' + dirs[int(num)]

def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    print(vars(args))

    if not os.path.exists(args.snapshot_dir):
        os.mkdir(args.snapshot_dir)

    with open('snapshotting/config/snapshotdir.txt', 'w') as f:
        f.write(os.path.abspath(args.snapshot_dir))

    if args.reload:
        reload_dir = show_snapshots(args.snapshot_dir)
        print(reload_dir)
    else:
        run_example(vars(args))

if __name__ == '__main__':
    main()

