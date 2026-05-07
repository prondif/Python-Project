# Warehouse Management System (Tier 2)

This program simulates an automated warehouse system using FIFO
(First In, First Out) batch handling together with ADS communication.

## Features
- Add stock in batches
- Remove stock using FIFO logic
- Automatic pallet movement
- Imaging and transfer operations
- Display current stock and quantity
- Return pallet to home position automatically

## How it works
Each stock batch is stored as an object.

When removing stock, the system always removes items from
the oldest batch first.

The simulator communicates with Python through ADS signals
to automate warehouse operations.

## Workflow
HOME -> IMAGING -> TRANSFER -> STORAGE -> HOME

## How to run
Run the file:

wms.py

Then follow the terminal instructions.