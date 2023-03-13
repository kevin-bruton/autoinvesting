# Trade Copier

## Objective
The trade copier replicates the operations made from a master demo account in an investor's account who can subscribe to the specific strategies that he/she wants to.

## Trade Receiver

The Trade Receiver receives an event when some trade action has been performed by the Master. It takes the appropriate order tracking actions (saving to DB) for the Master, before adding that action to the trade queue to be processed by the Trade Publisher

The handling it does with respect to the Master's trade actions is the following:

Pending orders and open positions are saved in the `Orders` table with the status `pending`

If a pending order is cancelled, it's status is set to `cancelled`.

When creating the master's order:
accountId = `{magic}_D`  

Once a pending order is converted into an open position, it's entry's status in the `Orders` table is converted to `open`.

Once an open position is closed, it is removed from the `Orders` table and an new entry is included in the `Trades` table.

## Trade Publisher

Has a function called `handle_msgs_from_master` that receives the orders from the trades queue performed on the Master account:
  - It looks for all accounts that have subscribed to that strategy
  - If the subscribed client is connected, the message is sent to that client for it to be performed there
  - If the subscribed client is not connected, then an entry is added to the log to registered this event

It has a function called `handle_message` which receives messages from connected clients. After the initial authentication request, the rest of the messages that are going to be received are basically responses to orders being sent to those clients. Depending on the kind of trade response, different corresponding function will be called to handle these messages.

If the message informs that the order action was performed then this is registered in the DB and registered in the log.  
If not, then it is simply registered in the log.
