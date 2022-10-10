import argparse
import time

from tqdm import tqdm

from spg.agent import HeadAgent
from spg.element import Ball
from spg.playground import Room
from spg.utils.position import UniformCoordinateSampler


def run_exp(args):

    playground = Room(size=(args.width, args.height))

    for _ in range(args.number_agents):

        sampler = UniformCoordinateSampler(
            playground, center=playground.center, size=playground.size
        )

        other_agent = HeadAgent()
        playground.add(other_agent, sampler, allow_overlapping=False)

    for _ in range(args.number_balls):

        sampler = UniformCoordinateSampler(
            playground, center=playground.center, size=playground.size
        )

        ball = Ball()
        playground.add(ball, sampler, allow_overlapping=False)

    time_start = time.time()
    for _ in tqdm(range(args.steps)):
        commands = {agent: agent.get_random_commands() for agent in playground.agents}
        playground.step(commands)
    time_end = time.time()

    print(args, args.steps / (time_end - time_start))


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()

    PARSER.add_argument(
        "--width",
        type=int,
        default=200,
        help="Environment width",
    )

    PARSER.add_argument(
        "--height",
        type=int,
        default=200,
        help="Environment heigh",
    )

    PARSER.add_argument(
        "--number_agents",
        type=int,
        default=50,
        help="Number of agents",
    )

    PARSER.add_argument(
        "--number_balls",
        type=int,
        default=50,
        help="Number of balls",
    )

    PARSER.add_argument(
        "--steps",
        type=int,
        default=1000,
        help="Environment steps",
    )

    ARGS = PARSER.parse_args()

    run_exp(ARGS)
