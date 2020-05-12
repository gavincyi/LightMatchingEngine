#!/usr/bin/python3
import lightmatchingengine.lightmatchingengine as lme
import unittest

class TestBasicOrders(unittest.TestCase):
    instmt = "TestingInstrument"
    price = 100.0
    lot_size = 1.0

    def check_order(self, order, order_id, instmt, price, qty, side, cum_qty, leaves_qty):
        """
        Check the order information
        """
        self.assertTrue(order is not None)
        self.assertEqual(order_id, order.order_id)
        self.assertEqual(instmt, order.instmt)
        self.assertEqual(price, order.price)
        self.assertEqual(qty, order.qty)
        self.assertEqual(side, order.side)
        self.assertEqual(cum_qty, order.cum_qty)
        self.assertEqual(leaves_qty, order.leaves_qty)

    def check_trade(self, trade, order_id, instmt, trade_price, trade_qty, trade_side, trade_id):
        """
        Check the trade information
        """
        self.assertTrue(trade is not None)
        self.assertEqual(order_id, trade.order_id)
        self.assertEqual(instmt, trade.instmt)
        self.assertEqual(trade_price, trade.trade_price)
        self.assertEqual(trade_qty, trade.trade_qty)
        self.assertEqual(trade_side, trade.trade_side)
        self.assertEqual(trade_id, trade.trade_id)

    def check_order_book(self, me, instmt, num_bids_level, num_asks_level):
        """
        Check the order book depth
        """
        self.assertTrue(instmt in me.order_books.keys())
        self.assertEqual(num_bids_level, len(me.order_books[instmt].bids))
        self.assertEqual(num_asks_level, len(me.order_books[instmt].asks))

    def check_deleted_order(self, order, del_order):
        """
        Check if the deleted order is same as the original order
        """
        self.assertTrue(order is not None)
        self.assertTrue(del_order is not None)
        self.assertEqual(order, del_order)
        self.assertEqual(0, del_order.leaves_qty)

    def test_cancel_order(self):
        me = lme.LightMatchingEngine()

        # Place a buy order
        order, trades = me.add_order(TestBasicOrders.instmt, \
                                    TestBasicOrders.price, \
                                    TestBasicOrders.lot_size, \
                                    lme.Side.BUY)
        self.assertEqual(0, len(trades))
        self.check_order_book(me, TestBasicOrders.instmt, 1, 0)
        self.check_order(order, 1, TestBasicOrders.instmt, TestBasicOrders.price, \
                         TestBasicOrders.lot_size, lme.Side.BUY, 0, TestBasicOrders.lot_size)

        # Cancel a buy order
        del_order = me.cancel_order(order.order_id, TestBasicOrders.instmt)
        self.assertEqual(0, len(trades))
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.check_deleted_order(order, del_order)

        # Place a sell order
        order, trades = me.add_order(TestBasicOrders.instmt, \
                                    TestBasicOrders.price, \
                                    TestBasicOrders.lot_size, \
                                    lme.Side.SELL)
        self.assertEqual(0, len(trades))
        self.check_order_book(me, TestBasicOrders.instmt, 0, 1)
        self.check_order(order, 2, TestBasicOrders.instmt, TestBasicOrders.price, \
                         TestBasicOrders.lot_size, lme.Side.SELL, 0, TestBasicOrders.lot_size)

        # Cancel a sell order
        del_order = me.cancel_order(order.order_id, TestBasicOrders.instmt)
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.check_deleted_order(order, del_order)

    def test_fill_order(self):
        me = lme.LightMatchingEngine()

        # Place a buy order
        buy_order, trades = me.add_order(TestBasicOrders.instmt, \
                                    TestBasicOrders.price, \
                                    TestBasicOrders.lot_size, \
                                    lme.Side.BUY)
        self.assertEqual(0, len(trades))
        self.check_order_book(me, TestBasicOrders.instmt, 1, 0)
        self.check_order(buy_order, 1, TestBasicOrders.instmt, TestBasicOrders.price, \
                        TestBasicOrders.lot_size, lme.Side.BUY, 0, TestBasicOrders.lot_size)

        # Place a sell order
        sell_order, trades = me.add_order(TestBasicOrders.instmt, \
                            TestBasicOrders.price, \
                            TestBasicOrders.lot_size, \
                            lme.Side.SELL)
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.assertEqual(2, len(trades))
        self.check_order(buy_order, 1, TestBasicOrders.instmt, TestBasicOrders.price, \
                        TestBasicOrders.lot_size, lme.Side.BUY, TestBasicOrders.lot_size, 0)
        self.check_order(sell_order, 2, TestBasicOrders.instmt, TestBasicOrders.price, \
                        TestBasicOrders.lot_size, lme.Side.SELL, TestBasicOrders.lot_size, 0)

        # Check trades
        self.check_trade(trades[0], sell_order.order_id, sell_order.instmt, \
                         sell_order.price, sell_order.qty, sell_order.side, 1)
        self.check_trade(trades[1], buy_order.order_id, buy_order.instmt, \
                         buy_order.price, buy_order.qty, buy_order.side, 2)

    def test_fill_multiple_orders_same_level(self):
        me = lme.LightMatchingEngine()

        # Place buy orders
        for i in range(1, 11):
            buy_order, trades = me.add_order(TestBasicOrders.instmt, \
                                            TestBasicOrders.price, \
                                            TestBasicOrders.lot_size, \
                                            lme.Side.BUY)
            self.assertEqual(0, len(trades))
            self.check_order_book(me, TestBasicOrders.instmt, 1, 0)
            self.assertEqual(i, len(me.order_books[TestBasicOrders.instmt].bids[TestBasicOrders.price]))
            self.check_order(buy_order, i, TestBasicOrders.instmt, TestBasicOrders.price, \
                            TestBasicOrders.lot_size, lme.Side.BUY, 0, TestBasicOrders.lot_size)

        # Place sell orders
        sell_order, trades = me.add_order(TestBasicOrders.instmt, \
                            TestBasicOrders.price, \
                            10.0 * TestBasicOrders.lot_size, \
                            lme.Side.SELL)
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.assertEqual(11, len(trades))
        self.check_order(buy_order, 10, TestBasicOrders.instmt, TestBasicOrders.price, \
                        TestBasicOrders.lot_size, lme.Side.BUY, TestBasicOrders.lot_size, 0)
        self.check_order(sell_order, 11, TestBasicOrders.instmt, TestBasicOrders.price, \
                        10*TestBasicOrders.lot_size, lme.Side.SELL, 10*TestBasicOrders.lot_size, 0)

        # Check aggressive hit orders
        self.check_trade(trades[0], sell_order.order_id, sell_order.instmt, \
                         sell_order.price, sell_order.qty, sell_order.side, 1)

        # Check passive hit orders
        for i in range(1, 11):
            self.check_trade(trades[i], i, buy_order.instmt, \
                             buy_order.price, buy_order.qty, buy_order.side, i+1)

    def test_fill_multiple_orders_different_level(self):
        me = lme.LightMatchingEngine()

        # Place buy orders
        for i in range(1, 11):
            buy_order, trades = me.add_order(TestBasicOrders.instmt, \
                                            TestBasicOrders.price+i, \
                                            TestBasicOrders.lot_size, \
                                            lme.Side.BUY)
            self.assertEqual(0, len(trades))
            self.check_order_book(me, TestBasicOrders.instmt, i, 0)
            self.assertEqual(1, len(me.order_books[TestBasicOrders.instmt].bids[TestBasicOrders.price+i]))
            self.check_order(buy_order, i, TestBasicOrders.instmt, TestBasicOrders.price+i, \
                            TestBasicOrders.lot_size, lme.Side.BUY, 0, TestBasicOrders.lot_size)

        # Place sell orders
        sell_order, trades = me.add_order(TestBasicOrders.instmt, \
                            TestBasicOrders.price, \
                            10.0 * TestBasicOrders.lot_size, \
                            lme.Side.SELL)
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.assertEqual(20, len(trades))
        self.check_order(buy_order, 10, TestBasicOrders.instmt, TestBasicOrders.price+10, \
                        TestBasicOrders.lot_size, lme.Side.BUY, TestBasicOrders.lot_size, 0)
        self.check_order(sell_order, 11, TestBasicOrders.instmt, TestBasicOrders.price, \
                        10*TestBasicOrders.lot_size, lme.Side.SELL, 10*TestBasicOrders.lot_size, 0)

        for i in range(0, 10):
            match_price = sell_order.price+10-i
            self.check_trade(trades[2*i], sell_order.order_id, sell_order.instmt, \
                             match_price, TestBasicOrders.lot_size, sell_order.side, 2*i+1)
            self.check_trade(trades[2*i+1], 10-i, buy_order.instmt, \
                             match_price, TestBasicOrders.lot_size, buy_order.side, 2*i+2)

    def test_cancel_partial_fill_orders(self):
        me = lme.LightMatchingEngine()

        # Place a buy order
        buy1_order, trades = me.add_order(TestBasicOrders.instmt, \
                                    TestBasicOrders.price + 0.1, \
                                    TestBasicOrders.lot_size, \
                                    lme.Side.BUY)
        self.assertEqual(0, len(trades))
        self.check_order_book(me, TestBasicOrders.instmt, 1, 0)
        self.check_order(buy1_order, 1, TestBasicOrders.instmt, TestBasicOrders.price + 0.1, \
                        TestBasicOrders.lot_size, lme.Side.BUY, 0, TestBasicOrders.lot_size)

        # Place a buy order
        buy2_order, trades = me.add_order(TestBasicOrders.instmt, \
                                    TestBasicOrders.price, \
                                    2 * TestBasicOrders.lot_size, \
                                    lme.Side.BUY)
        self.assertEqual(0, len(trades))
        self.check_order_book(me, TestBasicOrders.instmt, 2, 0)
        self.check_order(buy2_order, 2, TestBasicOrders.instmt, TestBasicOrders.price, \
                        2 * TestBasicOrders.lot_size, lme.Side.BUY, 0, 2 * TestBasicOrders.lot_size)

        # Place a sell order
        sell_order, trades = me.add_order(TestBasicOrders.instmt, \
                            TestBasicOrders.price, \
                            2 * TestBasicOrders.lot_size, \
                            lme.Side.SELL)
        self.check_order_book(me, TestBasicOrders.instmt, 1, 0)
        self.assertEqual(4, len(trades))
        self.check_order(buy1_order, 1, TestBasicOrders.instmt, TestBasicOrders.price + 0.1, \
                        TestBasicOrders.lot_size, lme.Side.BUY, TestBasicOrders.lot_size, 0)
        self.check_order(buy2_order, 2, TestBasicOrders.instmt, TestBasicOrders.price, \
                        2*TestBasicOrders.lot_size, lme.Side.BUY, TestBasicOrders.lot_size, TestBasicOrders.lot_size)
        self.check_order(sell_order, 3, TestBasicOrders.instmt, TestBasicOrders.price, \
                        2*TestBasicOrders.lot_size, lme.Side.SELL, 2*TestBasicOrders.lot_size, 0)

        # Check trades
        self.check_trade(trades[0], sell_order.order_id, sell_order.instmt, \
                         TestBasicOrders.price + 0.1, TestBasicOrders.lot_size, sell_order.side, 1)
        self.check_trade(trades[1], buy1_order.order_id, buy1_order.instmt, \
                         TestBasicOrders.price + 0.1, TestBasicOrders.lot_size, buy1_order.side, 2)
        self.check_trade(trades[2], sell_order.order_id, sell_order.instmt, \
                         TestBasicOrders.price, TestBasicOrders.lot_size, sell_order.side, 3)
        self.check_trade(trades[3], buy2_order.order_id, buy1_order.instmt, \
                         TestBasicOrders.price, TestBasicOrders.lot_size, buy2_order.side, 4)

        # Cancel the second order
        del_order = me.cancel_order(buy2_order.order_id, TestBasicOrders.instmt)
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.check_deleted_order(buy2_order, del_order)

    def test_fill_multiple_orders_same_level_market_order(self):
        me = lme.LightMatchingEngine()

        # Place buy orders
        for i in range(1, 11):
            buy_order, trades = me.add_order(TestBasicOrders.instmt, \
                                            TestBasicOrders.price, \
                                            TestBasicOrders.lot_size, \
                                            lme.Side.BUY)
            self.assertEqual(0, len(trades))
            self.check_order_book(me, TestBasicOrders.instmt, 1, 0)
            self.assertEqual(i, len(me.order_books[TestBasicOrders.instmt].bids[TestBasicOrders.price]))
            self.check_order(buy_order, i, TestBasicOrders.instmt, TestBasicOrders.price, \
                            TestBasicOrders.lot_size, lme.Side.BUY, 0, TestBasicOrders.lot_size)

        # Place sell orders
        sell_order, trades = me.add_order(TestBasicOrders.instmt, \
                            0, \
                            10.0 * TestBasicOrders.lot_size, \
                            lme.Side.SELL)
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.assertEqual(11, len(trades))
        self.check_order(buy_order, 10, TestBasicOrders.instmt, TestBasicOrders.price, \
                        TestBasicOrders.lot_size, lme.Side.BUY, TestBasicOrders.lot_size, 0)
        self.check_order(sell_order, 11, TestBasicOrders.instmt, 0, \
                        10*TestBasicOrders.lot_size, lme.Side.SELL, 10*TestBasicOrders.lot_size, 0)

        # Check aggressive hit orders - Trade price is same as the passive hit limit price
        self.check_trade(trades[0], sell_order.order_id, sell_order.instmt, \
                         buy_order.price, sell_order.qty, sell_order.side, 1)

        # Check passive hit orders
        for i in range(1, 11):
            self.check_trade(trades[i], i, buy_order.instmt, \
                             buy_order.price, buy_order.qty, buy_order.side, i+1)

    def test_fill_multiple_orders_different_level_market_order(self):
        me = lme.LightMatchingEngine()

        # Place buy orders
        for i in range(1, 11):
            buy_order, trades = me.add_order(TestBasicOrders.instmt, \
                                            TestBasicOrders.price+i, \
                                            TestBasicOrders.lot_size, \
                                            lme.Side.BUY)
            self.assertEqual(0, len(trades))
            self.check_order_book(me, TestBasicOrders.instmt, i, 0)
            self.assertEqual(1, len(me.order_books[TestBasicOrders.instmt].bids[TestBasicOrders.price+i]))
            self.check_order(buy_order, i, TestBasicOrders.instmt, TestBasicOrders.price+i, \
                            TestBasicOrders.lot_size, lme.Side.BUY, 0, TestBasicOrders.lot_size)

        # Place sell orders
        sell_order, trades = me.add_order(TestBasicOrders.instmt, \
                            0, \
                            10.0 * TestBasicOrders.lot_size, \
                            lme.Side.SELL)
        self.check_order_book(me, TestBasicOrders.instmt, 0, 0)
        self.assertEqual(20, len(trades))
        self.check_order(buy_order, 10, TestBasicOrders.instmt, TestBasicOrders.price+10, \
                        TestBasicOrders.lot_size, lme.Side.BUY, TestBasicOrders.lot_size, 0)
        self.check_order(sell_order, 11, TestBasicOrders.instmt, 0, \
                        10*TestBasicOrders.lot_size, lme.Side.SELL, 10*TestBasicOrders.lot_size, 0)

        for i in range(0, 10):
            match_price = TestBasicOrders.price+10-i
            self.check_trade(trades[2*i], sell_order.order_id, sell_order.instmt, \
                             match_price, TestBasicOrders.lot_size, sell_order.side, 2*i+1)
            self.check_trade(trades[2*i+1], 10-i, buy_order.instmt, \
                             match_price, TestBasicOrders.lot_size, buy_order.side, 2*i+2)

    def test_amend_qty_down(self):
        me = lme.LightMatchingEngine()

        # Place a buy order
        order, trades = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price,
            qty=TestBasicOrders.lot_size * 3,
            side=lme.Side.BUY
        )

        # Place another buy order
        order2, trades2 = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price,
            qty=TestBasicOrders.lot_size,
            side=lme.Side.BUY
        )

        # Check the order book and trades
        self.assertEqual(0, len(trades))
        self.assertEqual(0, len(trades2))
        self.check_order_book(me, TestBasicOrders.instmt, 1, 0)
        self.check_order(
            order=order, order_id=1, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price, qty=TestBasicOrders.lot_size * 3,
            side=lme.Side.BUY, cum_qty=0, leaves_qty=TestBasicOrders.lot_size * 3)
        self.check_order(
            order=order2, order_id=2, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price, qty=TestBasicOrders.lot_size,
            side=lme.Side.BUY, cum_qty=0, leaves_qty=TestBasicOrders.lot_size)

        # Partial fill the first order
        order3, trades3 = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price,
            qty=TestBasicOrders.lot_size,
            side=lme.Side.SELL
        )
        self.assertEqual(2, len(trades3))
        self.check_trade(
            trade=trades3[0], order_id=3, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price,
            trade_qty=TestBasicOrders.lot_size, trade_side=lme.Side.SELL,
            trade_id=1)
        self.check_trade(
            trade=trades3[1], order_id=1, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price,
            trade_qty=TestBasicOrders.lot_size, trade_side=lme.Side.BUY,
            trade_id=2)
        self.check_order(
            order=order, order_id=1, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price, qty=TestBasicOrders.lot_size * 3,
            side=lme.Side.BUY, cum_qty=TestBasicOrders.lot_size,
            leaves_qty=TestBasicOrders.lot_size * 2)

        # Amend the quantity down
        order, trades = me.amend_order(
            order_id=order.order_id,
            instmt=TestBasicOrders.instmt,
            amended_price=TestBasicOrders.price,
            amended_qty=TestBasicOrders.lot_size * 2,
        )
        self.assertEqual(0, len(trades))
        self.check_order(
            order=order, order_id=1, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price, qty=TestBasicOrders.lot_size * 2,
            side=lme.Side.BUY, cum_qty=TestBasicOrders.lot_size,
            leaves_qty=TestBasicOrders.lot_size)

        # Fill the remaining orders
        order4, trades4 = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price,
            qty=TestBasicOrders.lot_size * 2,
            side=lme.Side.SELL
        )
        self.assertEqual(3, len(trades4))
        self.check_order(
            order=order4, order_id=4, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price, qty=TestBasicOrders.lot_size * 2,
            side=lme.Side.SELL, cum_qty=TestBasicOrders.lot_size * 2,
            leaves_qty=0.0)
        self.check_trade(
            trade=trades4[0], order_id=4, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price,
            trade_qty=TestBasicOrders.lot_size * 2, trade_side=lme.Side.SELL,
            trade_id=3)
        self.check_trade(
            trade=trades4[1], order_id=1, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price,
            trade_qty=TestBasicOrders.lot_size, trade_side=lme.Side.BUY,
            trade_id=4)
        self.check_trade(
            trade=trades4[2], order_id=2, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price,
            trade_qty=TestBasicOrders.lot_size, trade_side=lme.Side.BUY,
            trade_id=5)

    def test_amend_order_price_and_qty(self):
        """Test the amend order price and qty.

        1. Place two buy orders on the same price (id = 1 and id = 2)
        2. Place two sell orders of which one is 0.1 higher than another
           (id = 3 and id = 4).
        3. Amend on buy order (id = 2 => 5) price and the qty from the back
           to execute on the best ask (id = 3).
        4. Amend the buy order (id = 1 => 6) to the best bid price.
        5. Amend the front best bid order (id = 5 => 7) quantity up. The
           original order quantity is 2 * lot_size and the leaves qty is
           lot_size. Amending the volume up from 2 to 3 creates a new order
           with order quantity = 3.
        6. Amend the sell order (id = 4) to execute the best bid orders,
           the first matched buy order should be with id = 6 and then id = 7.
        """
        me = lme.LightMatchingEngine()

        # 1. Place two buy orders on the same price (id = 1 and id = 2)
        order, trades = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price,
            qty=TestBasicOrders.lot_size,
            side=lme.Side.BUY
        )

        # Place another buy order
        order2, trades2 = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price,
            qty=TestBasicOrders.lot_size,
            side=lme.Side.BUY
        )

        self.assertEqual(0, len(trades))
        self.assertEqual(0, len(trades2))

        # 2. Place two sell orders of which one is 0.1 higher than another
        #    (id = 3 and id = 4).
        order3, trades3 = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price + 0.1,
            qty=TestBasicOrders.lot_size,
            side=lme.Side.SELL
        )
        order4, trades4 = me.add_order(
            instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price + 0.2,
            qty=TestBasicOrders.lot_size,
            side=lme.Side.SELL
        )

        self.assertEqual(0, len(trades3))
        self.assertEqual(0, len(trades4))

        # 3. Amend on buy order (id = 2) price and the qty from the back
        #    to execute on the best ask (id = 3).
        order5, trades5 = me.amend_order(
            instmt=TestBasicOrders.instmt,
            order_id=order2.order_id,
            amended_price=TestBasicOrders.price + 0.1,
            amended_qty=TestBasicOrders.lot_size * 2,
        )

        # A new order id should be generated
        self.assertEqual(2, len(trades5))
        self.check_order(
            order=order5, order_id=5, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price + 0.1, qty=TestBasicOrders.lot_size * 2,
            side=lme.Side.BUY, cum_qty=TestBasicOrders.lot_size,
            leaves_qty=TestBasicOrders.lot_size)
        self.check_trade(
            trade=trades5[0], order_id=5, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price + 0.1,
            trade_qty=TestBasicOrders.lot_size, trade_side=lme.Side.BUY,
            trade_id=1)
        self.check_trade(
            trade=trades5[1], order_id=3, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price + 0.1,
            trade_qty=TestBasicOrders.lot_size, trade_side=lme.Side.SELL,
            trade_id=2)

        # 4. Amend the buy order (id = 1 => 6) to the best bid price.
        order6, trades6 = me.amend_order(
            instmt=TestBasicOrders.instmt,
            order_id=order.order_id,
            amended_price=TestBasicOrders.price + 0.1,
            amended_qty=TestBasicOrders.lot_size,
        )

        self.assertEqual(0, len(trades6))
        self.check_order(
            order=order6, order_id=6, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price + 0.1, qty=TestBasicOrders.lot_size,
            side=lme.Side.BUY, cum_qty=0.0,
            leaves_qty=TestBasicOrders.lot_size)

        # 5. Amend the front best bid order (id = 5 => 7) quantity up. The
        #    original order quantity is 2 * lot_size and the leaves qty is
        #    lot_size. Amending the volume up from 2 to 3 creates a new order
        #    with order quantity = 2 (new qty - original leaves qty = 3 - 1).
        order7, trades7 = me.amend_order(
            instmt=TestBasicOrders.instmt,
            order_id=order5.order_id,
            amended_price=TestBasicOrders.price + 0.1,
            amended_qty=TestBasicOrders.lot_size * 3,
        )

        self.assertEqual(0, len(trades7))
        self.check_order(
            order=order7, order_id=7, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price + 0.1, qty=TestBasicOrders.lot_size * 3,
            side=lme.Side.BUY, cum_qty=0.0,
            leaves_qty=TestBasicOrders.lot_size * 3
        )

        # 6. Amend the sell order (id = 4) to execute the best bid orders,
        #    the first matched buy order should be with id = 6 and then id = 7.
        order8, trades8 = me.amend_order(
            instmt=TestBasicOrders.instmt,
            order_id=order4.order_id,
            amended_price=TestBasicOrders.price + 0.1,
            amended_qty=TestBasicOrders.lot_size * 4,
        )

        self.assertEqual(3, len(trades8))
        self.check_order(
            order=order8, order_id=8, instmt=TestBasicOrders.instmt,
            price=TestBasicOrders.price + 0.1,
            qty=TestBasicOrders.lot_size * 4,
            side=lme.Side.SELL, cum_qty=TestBasicOrders.lot_size * 4,
            leaves_qty=0.0
        )
        self.check_trade(
            trade=trades8[0], order_id=8, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price + 0.1,
            trade_qty=TestBasicOrders.lot_size * 4, trade_side=lme.Side.SELL,
            trade_id=3
        )
        self.check_trade(
            trade=trades8[1], order_id=6, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price + 0.1,
            trade_qty=TestBasicOrders.lot_size, trade_side=lme.Side.BUY,
            trade_id=4
        )
        self.check_trade(
            trade=trades8[2], order_id=7, instmt=TestBasicOrders.instmt,
            trade_price=TestBasicOrders.price + 0.1,
            trade_qty=TestBasicOrders.lot_size * 3, trade_side=lme.Side.BUY,
            trade_id=5
        )


if __name__ == '__main__':
    unittest.main()
