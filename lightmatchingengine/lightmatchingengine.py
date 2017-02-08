#!/usr/bin/python3  
class Side:
    """
    Side
    """
    BUY = 1
    SELL = 2
    
class OrderBook(object):
    """
    Order book
    """
    def __init__(self):
        """
        Constructor
        """
        self.bids = {}
        self.asks = {}    
        self.order_id_map = {}


class Order(object):
    """
    Order
    """
    def __init__(self, order_id, instmt, price, qty, side):
        """
        Constructor
        """        
        self.order_id = order_id
        self.instmt = instmt
        self.price = price
        self.qty = qty
        self.cum_qty = 0
        self.leaves_qty = qty
        self.side = side


class Trade(object):
    """
    Trade
    """
    def __init__(self, order_id, instmt, trade_price, trade_qty, trade_side, trade_id):
        """
        Constructor
        """
        self.order_id = order_id
        self.instmt = instmt
        self.trade_price = trade_price
        self.trade_qty = trade_qty
        self.trade_side = trade_side
        self.trade_id = trade_id


class LightMatchingEngine(object):
    """
    Light matching engine
    """
    def __init__(self):
        """
        Constructor
        """
        self.order_books = {}
        self.curr_order_id = 0
        self.curr_trade_id = 0
        
    def add_order(self, instmt, price, qty, side):
        """
        Add an order
        :param instmt       Instrument name
        :param price        Price, defined as zero if market order
        :param qty          Order quantity
        :param side         1 for BUY, 2 for SELL. Defaulted as BUY.
        :return The order and the list of trades. 
                Empty list if there is no matching. 
        """
        assert side == Side.BUY or side == Side.SELL, \
                "Invalid side %s" % side
        
        # Locate the order book
        order_book = self.order_books.setdefault(instmt, OrderBook())
        
        # Initialization
        trades = []
        self.curr_order_id += 1
        order_id = self.curr_order_id
        order = Order(order_id, instmt, price, qty, side)
        
        if side == Side.BUY:
            # Buy
            best_price = min(order_book.asks.keys()) if len(order_book.asks) > 0 \
                            else None
            while best_price is not None and \
                  (price == 0.0 or price >= best_price ) and \
                  order.leaves_qty > 0:
                best_price_qty = sum([ask.qty for ask in order_book.asks[best_price]]) 
                match_qty = min(best_price_qty, order.leaves_qty)
                assert match_qty > 0, "Match quantity must be larger than zero"
                
                # Generate aggressive order trade first
                self.curr_trade_id += 1
                order.cum_qty += match_qty
                order.leaves_qty -= match_qty
                trades.append(Trade(order_id, instmt, best_price, match_qty, \
                                    Side.BUY, self.curr_trade_id))
                
                # Generate the passive executions
                index = 0
                while match_qty > 0:
                    # The order hit
                    hit_order = order_book.asks[best_price][0]
                    # The order quantity hit
                    order_match_qty = min(match_qty, hit_order.leaves_qty)  
                    self.curr_trade_id += 1
                    trades.append(Trade(hit_order.order_id, instmt, best_price, \
                                        order_match_qty, \
                                        Side.SELL, self.curr_trade_id))
                    hit_order.cum_qty += order_match_qty
                    hit_order.leaves_qty -= order_match_qty
                    match_qty -= order_match_qty
                    if hit_order.leaves_qty == 0:
                        del order_book.asks[best_price][0]
                
                # If the price does not have orders, delete the particular price depth
                if len(order_book.asks[best_price]) == 0:
                    del order_book.asks[best_price]
                    
                # Update the best price
                best_price = min(order_book.asks.keys()) if len(order_book.asks) > 0 \
                                else None
            
            # Add the remaining order into the depth
            if order.leaves_qty > 0:
                depth = order_book.bids.setdefault(price, [])
                depth.append(order)
                order_book.order_id_map[order_id] = order
        else:
            #Sell
            best_price = max(order_book.bids.keys()) if len(order_book.bids) > 0 \
                            else None
            while best_price is not None and \
                  (price == 0.0 or price <= best_price) and \
                  order.leaves_qty > 0:
                best_price_qty = sum([bid.qty for bid in order_book.bids[best_price]]) 
                match_qty = min(best_price_qty, order.leaves_qty)
                assert match_qty > 0, "Match quantity must be larger than zero"
                
                # Generate aggressive order trade first
                self.curr_trade_id += 1
                order.cum_qty += match_qty
                order.leaves_qty -= match_qty
                trades.append(Trade(order_id, instmt, best_price, match_qty, \
                                    Side.SELL, self.curr_trade_id))
                
                # Generate the passive executions
                index = 0
                while match_qty > 0:
                    # The order hit
                    hit_order = order_book.bids[best_price][0]
                    # The order quantity hit
                    order_match_qty = min(match_qty, hit_order.leaves_qty)  
                    self.curr_trade_id += 1
                    trades.append(Trade(hit_order.order_id, instmt, best_price, \
                                        order_match_qty, \
                                        Side.BUY, self.curr_trade_id))
                    hit_order.cum_qty += order_match_qty
                    hit_order.leaves_qty -= order_match_qty
                    match_qty -= order_match_qty
                    if hit_order.leaves_qty == 0:
                        del order_book.bids[best_price][0]
                
                # If the price does not have orders, delete the particular price depth
                if len(order_book.bids[best_price]) == 0:
                    del order_book.bids[best_price]
                    
                # Update the best price
                best_price = max(order_book.bids.keys()) if len(order_book.bids) > 0 \
                                else None
            
            # Add the remaining order into the depth
            if order.leaves_qty > 0:
                depth = order_book.asks.setdefault(price, [])
                depth.append(order)
                order_book.order_id_map[order_id] = order
        
        return order, trades
    
    def cancel_order(self, order_id, instmt):
        """
        Cancel order
        :param order_id     Order ID
        :param side         Side
        :return The order if the cancellation is successful
        """
        assert instmt in self.order_books.keys(), \
                "Instrument %s is not valid in the order book" % instmt
        order_book = self.order_books[instmt]
        
        if order_id not in order_book.order_id_map.keys():
            # Invalid order id
            return None
            
        order = order_book.order_id_map[order_id]
        order_price = order.price
        order_id = order.order_id
        side = order.side
        
        if side == Side.BUY:
            assert order_price in order_book.bids.keys(), \
                 "Order price %.6f is not in the bid price depth"
            price_level = order_book.bids[order_price]
        else:
            assert order_price in order_book.asks.keys(), \
                 "Order price %.6f is not in the ask price depth"
            price_level = order_book.asks[order_price]
            
        index = 0
        price_level_len = len(price_level)
        while index < price_level_len:
            if price_level[index].order_id == order_id:
                del price_level[index]
                break
        
        if index == price_level_len:
            # Cannot find the order ID. Incorrect side
            return None
            
        if side == Side.BUY and len(order_book.bids[order_price]) == 0:
            # Delete empty particular price level
            del order_book.bids[order_price]
        elif side == Side.SELL and len(order_book.asks[order_price]) == 0:
            # Delete empty particular price level
            del order_book.asks[order_price]          
        
        # Delete the order id from the map
        order_book.order_id_map[order_id]
        
        # Zero out leaves qty
        order.leaves_qty = 0
        
        return order
        
        
    