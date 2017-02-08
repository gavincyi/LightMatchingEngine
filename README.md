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
del_order = lme.cancel_order(order.order_id, order.instmt, order.side)
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
del_order = lme.cancel_order(9999, order.instmt, order.side)
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

## Contact

For any inquiries, please feel free to contact me by gavincyi at gmail dot com.