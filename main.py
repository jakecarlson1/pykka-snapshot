import argparse
from examples import run_example

def build_arg_parser():
    parser = argparse.ArgumentParser(prog='snapshot-threads')
    parser.add_argument('-e', '--example', choices=[1], default=1,
                        help='Example to run', metavar='num')

    # TODO: add num incrementors and send prop as command line args
    
    return parser

def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    run_example(vars(args)['example'])

if __name__ == '__main__':
    main()

