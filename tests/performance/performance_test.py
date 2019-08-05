"""Performance test for light matching engine.

Usage:
    perf-test-light-matching-engine --freq <freq> [options]

Options:
    -h --help                   Show help.
    --freq=<freq>               Order frequency per second. [Default: 10]
    --num-orders=<num_orders>    Number of orders. [Default: 100]
    --add-order-prob=<prob>     Add order probability. [Default: 0.6]
    --mean-price=<mean-price>   Mean price in the standard normal distribution.
                                [Default: 100]
    --std-price=<std-price>     Standard derivation of the price in the standing
                                derivation. [Default: 0.5]
    --tick-size=<tick-size>     Tick size. [Default: 0.1]
    --gamma-quantity=<gamma>    Gamma value in the gamma distribution for the
                                order quantity. [Default: 2]
"""
from docopt import docopt
import logging
from math import log
from random import uniform, seed
from time import sleep, time

from tabulate import tabulate
from tqdm import tqdm

import numpy as np
import pandas as pd

from lightmatchingengine.lightmatchingengine import (
    LightMatchingEngine, Side)

LOGGER = logging.getLogger(__name__)


class Timer:
    def __enter__(self):
        self.start = time()
        return self

    def __exit__(self, *args):
        self.end = time()
        self.interval = self.end - self.start


def run(args):
    engine = LightMatchingEngine()

    symbol = "EUR/USD"
    add_order_prob = float(args['--add-order-prob'])
    num_of_orders = int(args['--num-orders'])
    gamma_quantity = float(args['--gamma-quantity'])
    mean_price = float(args['--mean-price'])
    std_price = float(args['--std-price'])
    tick_size = float(args['--tick-size'])
    freq = float(args['--freq'])
    orders = {}
    add_statistics = []
    cancel_statistics = []

    # Initialize random seed
    seed(42)

    progress_bar = tqdm(num_of_orders)
    while num_of_orders > 0:
        if uniform(0, 1) <= add_order_prob or len(orders) == 0:
            price = np.random.standard_normal() * std_price + mean_price
            price = int(price / tick_size) * tick_size
            quantity = np.random.gamma(gamma_quantity) + 1
            side = Side.BUY if uniform(0, 1) <= 0.5 else Side.SELL

            # Add the order
            with Timer() as timer:
                order, trades = engine.add_order(symbol, price, quantity, side)

            LOGGER.debug('Order %s is added at side %s, price %s '
                         'and quantity %s',
                         order.order_id, order.side, order.price, order.qty)

            # Save the order if there is any quantity left
            if order.leaves_qty > 0:
                orders[order.order_id] = order

            # Remove the trades
            for trade in trades:
                if (trade.order_id != order.order_id and
                    orders[trade.order_id].leaves_qty == 0.0):
                    del orders[trade.order_id]

            # Save the statistics
            add_statistics.append((order, len(trades), timer))

            num_of_orders -= 1
            progress_bar.update(1)
        else:
            index = int(uniform(0, 1) * len(orders))
            if index == len(orders):
                index -= 1

            order_id = list(orders.keys())[index]

            with Timer() as timer:
                engine.cancel_order(order_id, order.instmt)

            LOGGER.debug('Order %s is deleted', order_id)
            del orders[order_id]

            # Save the statistics
            cancel_statistics.append((order, timer))

        # Next time = -ln(U) / lambda
        sleep(-log(uniform(0, 1)) / freq)

    return add_statistics, cancel_statistics


def describe_statistics(add_statistics, cancel_statistics):
    add_statistics = pd.DataFrame([
        (trade_num, timer.interval * 1e6)
        for _, trade_num, timer in add_statistics],
        columns=['trade_num', 'interval'])

    # Trade statistics
    trade_statistics = add_statistics['trade_num'].describe()
    LOGGER.info('Trade statistics:\n%s',
                tabulate(trade_statistics.to_frame(name='trade'),
                         tablefmt='pipe'))

    cancel_statistics = pd.Series([
        timer.interval * 1e6 for _, timer in cancel_statistics],
        name='interval')

    statistics = pd.concat([
        add_statistics['interval'].describe(),
        cancel_statistics.describe()],
        keys=['add', 'cancel'],
        axis=1)

    statistics['add (trade > 0)'] = (
        add_statistics.loc[
            add_statistics['trade_num'] > 0, 'interval'].describe())

    percentile_75 = trade_statistics['75%']
    statistics['add (trade > %s)' % percentile_75] = (
        add_statistics.loc[add_statistics['trade_num'] > percentile_75,
                           'interval'].describe())

    LOGGER.info('Matching engine latency (nanoseconds):\n%s',
                tabulate(statistics,
                         headers=statistics.columns,
                         tablefmt='pipe'))

if __name__ == '__main__':
    args = docopt(__doc__, version='1.0.0')
    logging.basicConfig(level=logging.INFO)

    LOGGER.info('Running the performance benchmark')
    add_statistics, cancel_statistics = run(args)
    describe_statistics(add_statistics, cancel_statistics)
