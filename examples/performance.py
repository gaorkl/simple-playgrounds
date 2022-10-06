import argparse
import time

from tqdm import tqdm

from spg.agent import HeadAgent
from spg.playground import Room
from spg.utils.position import UniformCoordinateSampler


def run_exp(args):

    playground = Room(size=(args.w, args.h))

    for _ in range(args.n):

        sampler = UniformCoordinateSampler(
            playground, center=playground.center, size=playground.size
        )

        other_agent = HeadAgent()
        playground.add(other_agent, sampler, allow_overlapping=False)

    time_start = time.time()
    for _ in tqdm(range(args.s)):
        commands = {agent: agent.random_commands for agent in playground.agents}
        playground.step(commands)
    time_end = time.time()

    print(args, time_start - time_end)


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()

    PARSER.add_argument(
        "-w",
        type=int,
        default=200,
        help="Environment width",
    )

    PARSER.add_argument(
        "-h",
        type=int,
        default=200,
        help="Environment heigh",
    )

    PARSER.add_argument(
        "-n",
        type=int,
        default=50,
        help="Number of agents",
    )
    PARSER.add_argument(
        "-s",
        type=int,
        default=1000,
        help="Environment steps",
    )

    ARGS = PARSER.parse_args()

    run_exp(ARGS)
