# LightMatchingEngine

A light matching engine written in Python. 

The engine is a trivial object to support

* Add order - Returns the order and filled trades
* Cancel order - Returns the original order

The objective is to provide a easy interface for users on the standard
price-time priority matching algorithm among different instruments.

## Installation

The package can be installed by:

```
pip install lightmatchingengine
```

## Usage

Create a matching engine instance. 

```
from lightmatchingengine.lightmatchingengine import LightMatchingEngine, Side

lme = LightMatchingEngine()
```

Place an order.

```
order, trades = lme.add_order("EUR/USD", 1.10, 1000, Side.BUY)
```

Cancel an order.

```
del_order = lme.cancel_order(order.order_id, order.instmt)
```

Fill an order.

```
buy_order, trades = lme.add_order("EUR/USD", 1.10, 1000, Side.BUY)
print("Number of trades = %d" % len(trades))                # Number of trades = 0
print("Buy order quantity = %d" % buy_order.qty)            # Buy order quantity = 1000
print("Buy order filled = %d" % buy_order.cum_qty)          # Buy order filled = 0
print("Buy order leaves = %d" % buy_order.leaves_qty)       # Buy order leaves = 1000

sell_order, trades = lme.add_order("EUR/USD", 1.10, 1000, Side.SELL)
print("Number of trades = %d" % len(trades))                # Number of trades = 2
print("Buy order quantity = %d" % buy_order.qty)            # Buy order quantity = 1000
print("Buy order filled = %d" % buy_order.cum_qty)          # Buy order filled = 1000
print("Buy order leaves = %d" % buy_order.leaves_qty)       # Buy order leaves = 0
print("Trade price = %.2f" % trades[0].trade_price)         # Trade price = 1.10
print("Trade quantity = %d" % trades[0].trade_qty)          # Trade quantity = 1000
print("Trade side = %d" % trades[0].trade_side)             # Trade side = 2

```

Failing to delete an order returns a None value.

```
del_order = lme.cancel_order(9999, order.instmt)
print("Is order deleted = %d" % (del_order is not None))    # Is order deleted = 0
```

## Supported version

Python 2.x and 3.x are both supported.

## Order

The order object contains the following information:

* Exchange order ID (order_id)
* Instrument name (instmt)
* Price (price)
* Quantity (qty)
* Side (Buy/Sell) (side)
* Cumulated filled quantity (cum_qty)
* Leaves quantity (leaves_qty)

## Trade

The trade object contains the following information:

* Trade ID (trade_id)
* Instrument name (instmt)
* Exchange order ID (order_id)
* Trade price (trade_price)
* Trade quantity (trade_qty)
* Trade side (trade_side)

## Performance

To run the performance test, run the commands

```
pip install lightmatchingengine[performance]
python tests/performance/performance_test.py --freq 20
```

It returns the latency in nanosecond like below

|       |      add |   cancel |   add (trade > 0) |   add (trade > 2.0) |
|:------|---------:|---------:|------------------:|--------------------:|
| count | 100      |  61      |           27      |               6     |
| mean  | 107.954  |  50.3532 |          164.412  |             205.437 |
| std   |  58.1438 |  16.3396 |           36.412  |              24.176 |
| min   |  17.1661 |  11.4441 |           74.1482 |             183.105 |
| 25%   |  81.3007 |  51.9753 |          141.382  |             188.47  |
| 50%   |  92.5064 |  58.4126 |          152.349  |             200.748 |
| 75%   | 140.19   |  59.3662 |          190.496  |             211.239 |
| max   | 445.604  |  71.0487 |          248.909  |             248.909 |


## Contact

For any inquiries, please feel free to contact me by gavincyi at gmail dot com.
