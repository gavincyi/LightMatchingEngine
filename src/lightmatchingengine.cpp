#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include "lightmatchingengine.h"

namespace py = pybind11;

PYBIND11_MODULE(lightmatchingengine, m) {
    // Enum Side
    py::enum_<Side>(m, "Side")
        .value("BUY", Side::BUY)
        .value("SELL", Side::SELL)
        .export_values();

    // Struct Order
    py::class_<Order>(m, "Order")
        .def_readwrite("order_id", &Order::order_id)
        .def_readwrite("instmt", &Order::instmt)
        .def_readwrite("price", &Order::price)
        .def_readwrite("qty", &Order::qty)
        .def_readwrite("cum_qty", &Order::cum_qty)
        .def_readwrite("leaves_qty", &Order::leaves_qty)
        .def_readwrite("side", &Order::side)
        .def(py::init<
            int,
            string&,
            double,
            double,
            Side>());

    // Struct Trade
    py::class_<Trade>(m, "Trade")
        .def_readwrite("order_id", &Trade::order_id)
        .def_readwrite("instmt", &Trade::instmt)
        .def_readwrite("trade_price", &Trade::trade_price)
        .def_readwrite("trade_qty", &Trade::trade_qty)
        .def_readwrite("trade_side", &Trade::trade_side)
        .def_readwrite("trade_id", &Trade::trade_id)
        .def(py::init<
            int,
            const string&,
            double,
            double,
            Side,
            int>());

    // Late binding
    // py::bind_vector<deque<Order>>(m, "DequeOrder");
    py::bind_map<map<nprice_t, deque<Order>>>(m, "MapDoubleVectorOrder");
    py::bind_map<unordered_map<id_t, Order>>(m, "UnorderedMapIntOrder");

    // Class OrderBook
    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init())
        .def_readwrite("bids", &OrderBook::bids)
        .def_readwrite("asks", &OrderBook::asks)
        .def_readwrite("order_id_map", &OrderBook::order_id_map);


    // Class LightMatchingEngine
    py::bind_map<unordered_map<string, OrderBook>>(m, "UnorderedMapStringOrderBook");
    py::class_<LightMatchingEngine>(m, "LightMatchingEngine")
        .def(py::init())
        .def("add_order", &LightMatchingEngine::add_order)
        .def("cancel_order", &LightMatchingEngine::cancel_order)
        .def_property_readonly("order_books", &LightMatchingEngine::order_books, py::return_value_policy::reference)
        .def_property_readonly("curr_order_id", &LightMatchingEngine::curr_order_id)
        .def_property_readonly("curr_trade_id", &LightMatchingEngine::curr_trade_id);
}
