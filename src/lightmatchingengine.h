#include <cstdlib>
#include <string>
#include <limits>
#include <tuple>
#include <map>
#include <unordered_map>
#include <deque>
#include <deque>
#include <algorithm>
#include <stdexcept>
#include <sstream>

using namespace std;

#define MIN_NPRICE LLONG_MIN
#define MAX_NPRICE LLONG_MAX
#define MIN_QUANTITY 1e-9
#define MIN_TICK_SIZE 1e-9
#define EPILSON 5e-10
#define NORMALIZE_PRICE( x ) static_cast<int>( x / MIN_TICK_SIZE + EPILSON )
#define DENORMALIZE_PRICE( x ) ( x * MIN_TICK_SIZE )
#define nprice_t long long
#define price_t double
#define qty_t double
#define id_t long long

enum class Side {
  BUY = 1,
  SELL = 2
};

struct Order {
  id_t order_id;
  string instmt;
  price_t price;
  qty_t qty;
  qty_t cum_qty;
  qty_t leaves_qty;
  Side side;

  /* Order() = default; */
  /* Order(const Order&) = default; */
  /* Order& operator=(Order&) = default; */
  /* Order(Order&&) = default; */
  /* Order& operator=(Order&&) = default; */

  Order(id_t order_id, const string& instmt, price_t price, qty_t qty, Side side): 
      order_id(order_id),
      instmt(instmt),
      price(price),
      qty(qty),
      cum_qty(0),
      leaves_qty(qty),
      side(side) {}
};

struct Trade {
  id_t order_id;
  const string& instmt;
  price_t trade_price;
  qty_t trade_qty;
  Side trade_side;
  id_t trade_id;

  Trade(id_t order_id, const string& instmt, price_t trade_price, qty_t trade_qty,
        Side trade_side, id_t trade_id):
      order_id(order_id),
      instmt(instmt),
      trade_price(trade_price),
      trade_qty(trade_qty),
      trade_side(trade_side),
      trade_id(trade_id) {}
};

struct OrderBook {
    map<nprice_t, deque<Order>> bids;
    map<nprice_t, deque<Order>> asks;
    unordered_map<id_t, Order> order_id_map;
};

class LightMatchingEngine {
  public:
    unordered_map<string, OrderBook>& order_books() {
        return __order_books;
    }

    int curr_order_id() {
        return __curr_order_id;
    }

    int curr_trade_id() {
        return __curr_trade_id;
    }

    tuple<Order, vector<Trade>> add_order(
        const string& instmt, price_t price, qty_t qty, Side side) 
    {
        vector<Trade> trades;
        id_t order_id = (__curr_order_id += 1);
        Order order = Order(order_id, instmt, price, qty, side);
        nprice_t nprice = NORMALIZE_PRICE(price);

        // Find the order book
        auto order_book_it = __order_books.find(instmt);
        if (order_book_it == __order_books.end()) {
            order_book_it = __order_books.emplace(instmt, OrderBook()).first;
        }

        auto order_book = order_book_it->second;

        if (side == Side::BUY) {
            nprice_t best_nprice = MAX_NPRICE;
            if (order_book.asks.size() > 0) {
                best_nprice = order_book.asks.begin()->first;
            }

            while (nprice >= best_nprice && order.leaves_qty > MIN_QUANTITY) {
                auto nbbo = order_book.asks.begin()->second;
                auto original_leaves_qty = order.leaves_qty;

                // Matching the ask queue
                while (nbbo.size() > 0) {
                    auto front_nbbo = nbbo.front();
                    qty_t matching_qty = min(order.leaves_qty, nbbo[0].leaves_qty);
                    order.leaves_qty -= matching_qty;
                    front_nbbo.leaves_qty -= matching_qty;

                    // Trades on the passive order
                    trades.push_back(Trade(
                        front_nbbo.order_id,
                        instmt,
                        best_nprice,
                        matching_qty,
                        front_nbbo.side,
                        ++__curr_trade_id));

                    // Remove the order if it is fully executed
                    if (front_nbbo.leaves_qty < MIN_QUANTITY) {
                        order_book.order_id_map.erase(front_nbbo.order_id);
                        nbbo.pop_front();
                    }
                }

                // Trades from the original order
                trades.push_back(Trade(
                    order.order_id,
                    instmt,
                    best_nprice,
                    original_leaves_qty - order.leaves_qty,
                    order.side,
                    ++__curr_trade_id));

                // Remove the ask queue if the size = 0
                if (nbbo.size() == 0) {
                    order_book.asks.erase(order_book.asks.begin());
                }

                // Update the ask best prices
                if (order_book.asks.size() > 0) {
                    best_nprice = order_book.asks.begin()->first;
                } else {
                    best_nprice = MAX_NPRICE;
                }
            }

            // After matching the order, place the leaving order to the end
            // of the order book queue, and create the order id mapping
            if (order.leaves_qty > MIN_QUANTITY) {
                auto nbbo_it = order_book.bids.find(nprice);
                if (nbbo_it == order_book.bids.end()){
                    nbbo_it = order_book.bids.emplace(nprice, deque<Order>()).first;
                }

                auto nbbo = nbbo_it->second;
                nbbo.emplace_back(order);
                order_book.order_id_map.emplace(order.order_id, order);
            }
        } else {
            nprice_t best_nprice = MIN_NPRICE;
            if (order_book.bids.size() > 0) {
                best_nprice = order_book.bids.begin()->first;
            }

            while (nprice <= best_nprice && order.leaves_qty > MIN_QUANTITY) {
                auto nbbo = order_book.bids.begin()->second;
                auto original_leaves_qty = order.leaves_qty;

                // Matching the ask queue
                while (nbbo.size() > 0) {
                    auto front_nbbo = nbbo.front();
                    qty_t matching_qty = min(order.leaves_qty, nbbo[0].leaves_qty);
                    order.leaves_qty -= matching_qty;
                    front_nbbo.leaves_qty -= matching_qty;

                    // Trades on the passive order
                    trades.push_back(Trade(
                        front_nbbo.order_id,
                        instmt,
                        best_nprice,
                        matching_qty,
                        front_nbbo.side,
                        ++__curr_trade_id));

                    // Remove the order if it is fully executed
                    if (front_nbbo.leaves_qty < MIN_QUANTITY) {
                        order_book.order_id_map.erase(front_nbbo.order_id);
                        nbbo.pop_front();
                    }
                }

                // Trades from the original order
                trades.push_back(Trade(
                    order.order_id,
                    instmt,
                    best_nprice,
                    original_leaves_qty - order.leaves_qty,
                    order.side,
                    ++__curr_trade_id));

                // Remove the bid queue if the size = 0
                if (nbbo.size() == 0) {
                    order_book.bids.erase(order_book.bids.begin());
                }

                // Update the bid best prices
                if (order_book.bids.size() > 0) {
                    best_nprice = order_book.bids.begin()->first;
                } else {
                    best_nprice = MIN_NPRICE;
                }
            }

            // After matching the order, place the leaving order to the end
            // of the order book queue, and create the order id mapping
            if (order.leaves_qty > MIN_QUANTITY) {
                auto nbbo_it = order_book.asks.find(nprice);
                if (nbbo_it == order_book.asks.end()){
                    nbbo_it = order_book.asks.emplace(nprice, deque<Order>()).first;
                }

                auto nbbo = nbbo_it->second;
                nbbo.emplace_back(order);
                order_book.order_id_map.emplace(order.order_id, order);
            }
        }

        return make_tuple(order, trades);
    }

    Order& cancel_order(id_t order_id, const string& instmt) {
        auto order_book_it = __order_books.find(instmt);
        if (order_book_it == __order_books.end()) {
            auto err_message = string("Order books do not have the instrument ") + instmt;
            throw runtime_error(err_message);
        }

        auto order_book = order_book_it->second;
        auto order_it = order_book.order_id_map.find(order_id);
        if (order_it == order_book.order_id_map.end()) {
            ostringstream sstream;
            sstream << "Cannot find order " << order_id << " from instrument " << instmt;
            throw runtime_error(sstream.str());
        }

        auto order = order_it->second;
        auto nprice = NORMALIZE_PRICE(order.price);
        
        if (order.side == Side::BUY) {
            auto order_queue_it = order_book.bids.find(nprice);
            assert(order_queue_it != order_book.bids.end());
            auto order_queue = order_queue_it->second;
            auto found_order = find_if(
                order_queue.begin(), order_queue.end(), [&order](auto o) { return o.order_id == order.order_id; });

            // Remove the order from the matching engine
            order_queue.erase(found_order);
        } else {
            auto order_queue_it = order_book.asks.find(nprice);
            assert(order_queue_it != order_book.asks.end());
            auto order_queue = order_queue_it->second;
            auto found_order = find_if(
                order_queue.begin(), order_queue.end(), [&order](auto o) { return o.order_id == order.order_id; });

            // Remove the order from the matching engine
            order_queue.erase(found_order);
        }

        // Finally set the leaves qty to 0
        order.leaves_qty = 0.0;
        order_book.order_id_map.erase(order_it);

        return order;
    }

  private:
    unordered_map<string, OrderBook> __order_books;
    int __curr_order_id;
    int __curr_trade_id;
};
