# LightMatchingEngine

A light matching engine written in Python. 

The engine is a trivial object to support

* Add order - Returns the order and filled trades
* Cancel order - Returns the original order

The objective is to provide a easy interface for users on the standard
price-time priority matching algorithm among different instruments.

## Supported version

Python 2.x and 3.x are both supported.

## Order

The order object contains the following information:

* Exchange order ID
* Instrument name
* Price
* Quantity
* Side (Buy/Sell)
* Cumulated filled quantity
* Leaves quantity

## Trade

The trade object contains the following information:

* Trade ID
* Instrument name
* Exchange order ID
* Trade price
* Trade quantity
* Trade side

## Contact

For any inquiries, please feel free to contact me by gavincyi at gmail dot com.