#property strict

// --------------------------------------------------------------------
// Include socket library
// --------------------------------------------------------------------

#define SOCKET_LIBRARY_USE_EVENTS
#include <sockets.mqh>
// #include <stderror.mqh>
#include <stdlib.mqh>


// --------------------------------------------------------------------
// EA user inputs
// --------------------------------------------------------------------

input string   Hostname = "127.0.0.1";    // Server hostname or IP address
input ushort   ServerPort = 3000;        // Server port
input string   AuthKey = "GwD22oS3@KRp";              // Authentication Key

int connectionAttempt = 0;
int maxConnectionRetries = 100;
bool doneRetryingConnection = false;
bool isAuthorized = false;
bool isSubscribed = false;
int openOrders[];
int numSubscriptionLabels = 0;
int lastHeartBeatMin = 60;

// --------------------------------------------------------------------
// Global variables and constants
// --------------------------------------------------------------------

ClientSocket * glbClientSocket = NULL;

// --------------------------------------------------------------------
// Initialisation (no action required)
// --------------------------------------------------------------------

void OnInit() {
   ArrayResize(openOrders, 0);
   EventSetTimer(1);
//--- create application dialog
   //if(!dialog.Create(0,"Notification",0,300,0,450,110))
   //   return;
//--- run application
   // if(!dialog.Run())
   //   return;
   ObjectCreate(0,"Title", OBJ_RECTANGLE_LABEL, 0,0,0);
   ObjectSet("Title",OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("Title",OBJPROP_XDISTANCE,400);
   ObjectSet("Title",OBJPROP_YDISTANCE,0);
   // ObjectSet("Title",OBJPROP_BACK,true);
   ObjectSet("Title",OBJPROP_BORDER_TYPE,BORDER_RAISED);
   // ObjectSet("Title",OBJPROP_BGCOLOR,Blue);
   ObjectSet("Title",OBJPROP_XSIZE, 300);
   ObjectSet("Title", OBJPROP_YSIZE, 140);
   // ObjectSetText("Title","Auto Investing",20,"New Times Roman",Black);
   
   ObjectCreate(0,"Name",OBJ_LABEL,0,0,0);
   ObjectSet("Name",OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSet("Name",OBJPROP_XDISTANCE, 410);
   ObjectSet("Name",OBJPROP_YDISTANCE,5);
   ObjectSetText("Name","AUTO INVESTING",18,"Arial",Black);
   
   ObjectCreate(0,"ConnectedLabel",OBJ_LABEL,0,0,0);
   ObjectSet("ConnectedLabel",OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSet("ConnectedLabel",OBJPROP_XDISTANCE, 410);
   ObjectSet("ConnectedLabel",OBJPROP_YDISTANCE,40);
   ObjectSetText("ConnectedLabel","Connected:",14,"Arial",Black);
   
   ObjectCreate(0,"Connected", OBJ_RECTANGLE_LABEL, 0,0,0);
   ObjectSet("Connected",OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("Connected",OBJPROP_XDISTANCE,570);
   ObjectSet("Connected",OBJPROP_YDISTANCE,40);
   ObjectSet("Connected",OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSet("Connected",OBJPROP_BGCOLOR,White);
   ObjectSet("Connected",OBJPROP_XSIZE, 20);
   ObjectSet("Connected", OBJPROP_YSIZE, 20);
   
   ObjectCreate(0,"AuthorizedLabel",OBJ_LABEL,0,0,0);
   ObjectSet("AuthorizedLabel",OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSet("AuthorizedLabel",OBJPROP_XDISTANCE,410);
   ObjectSet("AuthorizedLabel",OBJPROP_YDISTANCE,70);
   ObjectSetText("AuthorizedLabel","Authorized:",14,"Arial",Black);
   
   ObjectCreate(0,"Authorized", OBJ_RECTANGLE_LABEL, 0,0,0);
   ObjectSet("Authorized",OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("Authorized",OBJPROP_XDISTANCE,570);
   ObjectSet("Authorized",OBJPROP_YDISTANCE,70);
   ObjectSet("Authorized",OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSet("Authorized",OBJPROP_BGCOLOR,White);
   ObjectSet("Authorized",OBJPROP_XSIZE, 20);
   ObjectSet("Authorized", OBJPROP_YSIZE, 20);
   
   ObjectCreate(0,"SubscribedLabel",OBJ_LABEL,0,0,0);
   ObjectSet("SubscribedLabel",OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSet("SubscribedLabel",OBJPROP_XDISTANCE,410);
   ObjectSet("SubscribedLabel",OBJPROP_YDISTANCE,100);
   ObjectSetText("SubscribedLabel","Subscribed:",14,"Arial",Black);
   
   ObjectCreate(0,"Subscribed", OBJ_RECTANGLE_LABEL, 0,0,0);
   ObjectSet("Subscribed",OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("Subscribed",OBJPROP_XDISTANCE,570);
   ObjectSet("Subscribed",OBJPROP_YDISTANCE,100);
   ObjectSet("Subscribed",OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSet("Subscribed",OBJPROP_BGCOLOR,White);
   ObjectSet("Subscribed",OBJPROP_XSIZE, 20);
   ObjectSet("Subscribed", OBJPROP_YSIZE, 20);
   
   /////////// Subscriptions ////////////////////////
   ObjectCreate(0,"SubscriptionsBox", OBJ_RECTANGLE_LABEL, 0,0,0);
   ObjectSet("SubscriptionsBox",OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("SubscriptionsBox",OBJPROP_XDISTANCE,400);
   ObjectSet("SubscriptionsBox",OBJPROP_YDISTANCE,130);
   ObjectSet("SubscriptionsBox",OBJPROP_BORDER_TYPE,BORDER_RAISED);
   ObjectSet("SubscriptionsBox",OBJPROP_XSIZE, 300);
   ObjectSet("SubscriptionsBox", OBJPROP_YSIZE, 40);
   
   ObjectCreate(0,"SubscriptionsTitle",OBJ_LABEL,0,0,0);
   ObjectSet("SubscriptionsTitle",OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSet("SubscriptionsTitle",OBJPROP_XDISTANCE, 410);
   ObjectSet("SubscriptionsTitle",OBJPROP_YDISTANCE,135);
   ObjectSetText("SubscriptionsTitle","SUBSCRIPTIONS",14,"Arial",Black);
   
   ObjectCreate(0,"GetSubscriptionsBtn", OBJ_BUTTON,0,0,0);
   ObjectSet("GetSubscriptionsBtn", OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("GetSubscriptionsBtn", OBJPROP_XDISTANCE, 635);
   ObjectSet("GetSubscriptionsBtn", OBJPROP_YDISTANCE, 137);
   ObjectSet("GetSubscriptionsBtn", OBJPROP_XSIZE, 60);
   ObjectSet("GetSubscriptionsBtn", OBJPROP_YSIZE, 25);
   ObjectSetText("GetSubscriptionsBtn", "Update", 10,"Arial", Black);
   ObjectSet("GetSubscriptionsBtn", OBJPROP_COLOR,clrBlack);
   // ObjectSetInteger(0,"GetSubscriptionsBtn",OBJPROP_BACK,false);
      
   ChartSetInteger(0, CHART_COLOR_BACKGROUND, White);
   ChartSetInteger(0, CHART_COLOR_FOREGROUND, Black);
   ChartSetInteger(0, CHART_COLOR_GRID, White);
   ChartSetInteger(0, CHART_COLOR_VOLUME, White);
   ChartSetInteger(0, CHART_COLOR_CHART_UP, White);
   ChartSetInteger(0, CHART_COLOR_CHART_DOWN, White);
   ChartSetInteger(0, CHART_COLOR_CHART_LINE, White);
   ChartSetInteger(0, CHART_COLOR_CANDLE_BEAR, White);
   ChartSetInteger(0, CHART_COLOR_CANDLE_BULL, White);
   ChartSetInteger(0, CHART_COLOR_BID, White);
   ChartSetInteger(0, CHART_COLOR_ASK, White);
   ChartSetInteger(0, CHART_COLOR_STOP_LEVEL, White);
   ChartSetInteger(0, CHART_FOREGROUND,0,false);
}

void setStatusConnected (bool isConnected) {
   ObjectSet("Connected",OBJPROP_BGCOLOR,isConnected ? Green : Red);
   if (!isConnected) {
      setAuthorized(false);
      setSubscribed(false);
   }
}

void setAuthorized (bool isAuth) {
   isAuthorized = isAuth;
   ObjectSet("Authorized",OBJPROP_BGCOLOR,isAuth ? Green : Red);
}

void setSubscribed (bool isSub) {
   isSubscribed = isSub;
   ObjectSet("Subscribed",OBJPROP_BGCOLOR,isSub ? Green : Red);
}

// --------------------------------------------------------------------
// Termination - free the client socket, if created
// --------------------------------------------------------------------

void OnDeinit(const int reason)
{
   Print("OnDeinit");
   EventKillTimer();
   if (glbClientSocket) {
      delete glbClientSocket;
      glbClientSocket = NULL;
   }
   setStatusConnected(false);
   ObjectDelete(0,"Title");
   ObjectDelete(0,"Name");
   ObjectDelete(0,"ConnectedLabel");
   ObjectDelete(0,"Connected");
   ObjectDelete(0,"AuthorizedLabel");
   ObjectDelete(0,"Authorized");
   ObjectDelete(0,"SubscribedLabel");
   ObjectDelete(0,"Subscribed");
   ObjectDelete(0,"SubscriptionsBox");
   ObjectDelete(0,"SubscriptionsTitle");
   ObjectDelete(0,"GetSubscriptionsBtn");
   for (int iLabel = 0; iLabel < numSubscriptionLabels; iLabel++) {
      ObjectDelete(0, "Subscription"+(string)iLabel);
   }
   ChartRedraw(0);
}

void OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)
{
   if (id == CHARTEVENT_OBJECT_CLICK) {
      if (sparam == "GetSubscriptionsBtn") {
         Print("Get Subscriptions");
         string msg = "{\"action\":\"get_subscriptions\"}";
         SendMsg(msg);
         if(ObjectGetInteger(0,"GetSubscriptionsBtn",OBJPROP_STATE)==true) {
            Sleep(300);
            ObjectSetInteger(0,"GetSubscriptionsBtn",OBJPROP_STATE,false);
         }
      }
   }
   if (id == CHARTEVENT_KEYDOWN) {
      // May be a real key press, or a dummy notification
      // resulting from socket activity. If lparam matches
      // any .GetSocketHandle() then it's from a socket.
      // If not, it's a real key press. (If lparam>256 then
      // it's also pretty reliably a socket message rather 
      // than a real key press.)
      
      if (lparam == glbClientSocket.GetSocketHandle()) {
         // Print("Caught activity on the socket");
         // ReadMessages();
      } else {
         // Doesn't match a socket. Assume real key pres
      }
   }
}

void OnTimer() {
   // Connect to socket server
   if (!glbClientSocket && connectionAttempt < maxConnectionRetries) {
      glbClientSocket = new ClientSocket(Hostname, ServerPort);
      if (glbClientSocket.IsSocketConnected()) {
         Print("Connected to server successfully");
         setStatusConnected(true);
      } else {
         // Print("Could NOT connect to server " + Hostname + ":" + (string)ServerPort);
      }
   }
   
   
   // If the socket is closed, destroy it, and attempt a new connection
   // on the next call to OnTick()
   if (glbClientSocket && !glbClientSocket.IsSocketConnected()) {
      // Destroy the server socket. A new connection
      // will be attempted on the next tick
      Print("Client disconnected. Will retry " + (string)(maxConnectionRetries - connectionAttempt) + " more times. Socket: " + (string)!!glbClientSocket + " Connected: " + (string)glbClientSocket.IsSocketConnected());
      connectionAttempt++;
      Sleep(5000);
      delete glbClientSocket;
      glbClientSocket = NULL;
      setStatusConnected(false);
   } else if (glbClientSocket && glbClientSocket.IsSocketConnected()) {
      connectionAttempt = 0;
      // 'Print("Client is connected");
      if (!isSubscribed) Subscribe();
      CheckOpenPositions();
      ReadMessages();
   } else if (!doneRetryingConnection) {
      Print("Client disconnected. Will NOT retry anymore!");
      doneRetryingConnection = true;
      setStatusConnected(false);
   }
   HearBeat();
}
// --------------------------------------------------------------------
// Tick handling - set up a connection, if none already active,
// and send the current price quote
// --------------------------------------------------------------------

void OnTick()
{
}

void CheckOpenPositions () {
   for (int i = 0; i < ArraySize(openOrders); i++) {
      int ticket = openOrders[i];
      bool isOrderSelected = OrderSelect(ticket,SELECT_BY_TICKET);
      bool isOrderOpen = isOrderSelected && OrderCloseTime() == 0;
      if (!isOrderOpen) {
         // SEND MESSAGE TO SERVER NOTIFYING THAT THE ORDER/POSITION HAS BEEN CLOSED
      }
   }
}

void HandleAuthorized (string & msgSeg[]) {
   Print("Client has been authorized");
   setAuthorized(true);
   Sleep(1000);
   HandleGotSubscriptions(msgSeg);
}

void HandleAuthorizationFailed(string & msgSeg[]) {
   Print("Could not authorize with token and account number. Disconnecting...");
   doneRetryingConnection = true;
   setStatusConnected(false);
   delete glbClientSocket;
   glbClientSocket = NULL;
}

void HandleGotSubscriptions (string & msgSeg[]) {
   string magics_str = msgSeg[1];
   Print("Retrieved subscriptions: ", magics_str);
   string magics[];
   StringSplit(magics_str, StringGetCharacter(",",0), magics);
   setSubscribed(ArraySize(magics) > 0);
   int yDistance = 165;
   for (int iLabel = 0; iLabel < numSubscriptionLabels; iLabel++) {
      ObjectDelete(0, "Subscription"+(string)iLabel);
   }
   numSubscriptionLabels = ArraySize(magics);
   for (int iMagic = 0; iMagic < numSubscriptionLabels; iMagic++) {
      ObjectSet("SubscriptionsBox", OBJPROP_YSIZE, 60 + (iMagic * 30));
      ObjectCreate(0,"Subscription"+(string)iMagic,OBJ_LABEL,0,0,0);
      ObjectSet("Subscription"+(string)iMagic,OBJPROP_CORNER,CORNER_LEFT_UPPER);
      ObjectSet("Subscription"+(string)iMagic,OBJPROP_XDISTANCE, 410);
      ObjectSet("Subscription"+(string)iMagic,OBJPROP_YDISTANCE,yDistance + (iMagic * 25));
      ObjectSetText("Subscription"+(string)iMagic,magics[iMagic],10,"Arial",Black);
      // ChartRedraw(0);
   }
}

void HandlePlaceOrder (string & msgSeg[]) {
   string order_type = msgSeg[1];
   string symbol= msgSeg[2];
   string volume = msgSeg[3];
   string orig_open_price = msgSeg[4];
   string sl = msgSeg[5];
   string tp = msgSeg[6];
   string comment = msgSeg[7];
   string magic = msgSeg[8];
   string masterOrderId = msgSeg[9];
   double current_open_price = (order_type == "Buy") ? Ask : Bid;
   Print("Placing order OrderSend: symbol: ", symbol, " Order type: ", OrderTypeStringToInt(order_type), " Volume: ", volume, " Open Price: ", current_open_price, " Slippage: ", 3, " TP: ", (double)sl, " TP: ", (double)tp, " Comment: ", comment, " Magic: ", (int)magic);
   int ticket = OrderSend(symbol, OrderTypeStringToInt(order_type), (double)volume, current_open_price, 3, (double)sl, (double)tp, comment, (int)magic, 0, Green);
   string msg;
   if (ticket == -1) {
      int error_code = GetLastError();
      string error_msg = "ERROR " + (string)error_code + ": " + ErrorDescription(error_code);
      Print("OrderSend failed. No ticket retrieved. ", error_msg);
      msg = StringFormat(
            "{\"action\":\"place_order\",\"status\":\"failed\",\"reason\":\"%s\",\"masterOrderId\":\"%s\",\"orderType\":\"%s\",\"symbol\":\"%s\",\"size\":\"%s\",\"openPrice\":\"%s\",\"sl\":\"%s\",\"tp\":\"%s\",\"comment\":\"%s\",\"magic\":\"%s\"}",
            error_msg, masterOrderId, order_type, symbol, volume, (string)current_open_price, sl, tp, comment, magic
         );
   } else {
      Print("OrderSend placed successfully");
      bool isSelected = OrderSelect(ticket, SELECT_BY_TICKET);
      if (isSelected) {
         string actual_open_price = (string)OrderOpenPrice();
         string actual_open_time = TimeToStr(OrderOpenTime(),TIME_DATE|TIME_SECONDS);
         string status = (order_type == "Buy" || order_type == "Sell") ? "open": "placed";
         msg = StringFormat(
            "{\"action\":\"place_order\",\"status\":\"%s\",\"orderId\":\"%s\",\"masterOrderId\":\"%s\",\"orderType\":\"%s\",\"symbol\":\"%s\",\"size\":\"%s\",\"openPrice\":\"%s\",\"openTime\":\"%s\",\"sl\":\"%s\",\"tp\":\"%s\",\"comment\":\"%s\",\"magic\":\"%s\"}",
            status, (string)ticket, masterOrderId, order_type, symbol, volume, actual_open_price, actual_open_time, sl, tp, comment, magic
         );
         int openOrderPosition = ArraySize(openOrders) + 1;
         ArrayResize(openOrders, openOrderPosition);
         openOrders[openOrderPosition - 1] = ticket;
      } else {
         string error_msg = "ERROR: Could not select order with orderId: " + (string)ticket;
         Print("OrderSend failed. ", error_msg);
         msg = StringFormat(
               "{\"action\":\"place_order\",\"status\":\"failed\",\"reason\":\"%s\",\"masterOrderId\":\"%s\",\"orderType\":\"%s\",\"symbol\":\"%s\",\"size\":\"%s\",\"openPrice\":\"%s\",\"sl\":\"%s\",\"tp\":\"%s\",\"comment\":\"%s\",\"magic\":\"%s\"}",
               error_msg, masterOrderId, order_type, symbol, volume, current_open_price, sl, tp, comment, magic
            );
      }
   }
   SendMsg(msg);
}

void HandleClosePosition (string & msgSegs[]) {
   string order_type = msgSegs[1];
   string symbol= msgSegs[2];
   string volume = msgSegs[3];
   string orig_open_price = msgSegs[4];
   string sl = msgSegs[5];
   string tp = msgSegs[6];
   string comment = msgSegs[7];
   string magic = msgSegs[8];
   string masterOrderId = msgSegs[9];
   string orderId = msgSegs[10];
   double close_at_price = order_type == "Buy" ? Bid : Ask;
   bool closed = OrderClose((int)orderId, (double)volume, close_at_price, 3, Red);
   string msg;
   if (closed) {
      Print("Position closed successfully");
      bool isSelected = OrderSelect((int)orderId, SELECT_BY_TICKET);
      if (isSelected) {
         string close_price = (string)OrderClosePrice();
         string close_time = TimeToStr(OrderCloseTime(),TIME_DATE|TIME_SECONDS);
         string profit = (string)OrderProfit();
         string commission = (string)OrderCommission();
         string balance = (string)AccountBalance();
         string order_comment = OrderComment();
         string swap = (string)OrderSwap();
         string close_type;
         if (StringFind(OrderComment(), "[sl]", 0) != -1) close_type = "SL";
         else if (StringFind(OrderComment(), "[tp]", 0) != -1) close_type = "TP";
         else close_type = OrderComment();
         msg = StringFormat(
            "{\"action\":\"close_position\",\"status\":\"closed\",\"orderId\":\"%s\",\"closePrice\":\"%s\",\"closeTime\":\"%s\",\"profit\":\"%s\",\"commission\":\"%s\",\"balance\":\"%s\",\"closeType\":\"%s\",\"comment\":\"%s\",\"swap\":\"%s\"}",
            orderId, close_price, close_time, profit, commission, balance, close_type, order_comment, swap
         );
      } else {
         string error_msg = "ERROR: Could not select order with orderId: " + orderId;
         Print("Failed to close position with id " + orderId);
         msg = StringFormat(
            "{\"action\":\"close_position\",\"status\":\"failed\",\"reason\":\"%s\",\"orderId\":\"%s\"}",
            error_msg, orderId
         );
      }
   } else {
      int error_code = GetLastError();
      string error_msg = "ERROR " + (string)error_code + ": " + ErrorDescription(error_code);
      Print("OrderClose failed ", error_msg);
      msg = StringFormat(
            "{\"action\":\"position_close\",\"status\":\"failed\",\"reason\":\"%s\",\"orderId\":\"%s\"}",
            error_msg, orderId
         );
   }
   SendMsg(msg);
}

void ReadMessages() {
   // Read any messages on the socket
   string strMessage;
   do {
      if (!glbClientSocket) {
         break;
      }
      strMessage = glbClientSocket.Receive("\n");
      // Print("ReceiveWithHeader: " + strMessage);
      if (strMessage != "") {
         strMessage = StringSubstr(strMessage,0,StringLen(strMessage)-1); // Remove end of line character
         Print("Received message: ", strMessage);
         string msgSegments[];
         StringSplit(strMessage,StringGetCharacter("|",0),msgSegments);
         if (ArraySize(msgSegments) > 0) {
            string action = msgSegments[0];
            if (action == "authorized")                  HandleAuthorized(msgSegments);
            else if (action == "authorization_failed")   HandleAuthorizationFailed(msgSegments);
            else if (action == "got_subscriptions")      HandleGotSubscriptions(msgSegments);
            else if (action == "place_order")            HandlePlaceOrder(msgSegments);
            else if (action == "close_position")         HandleClosePosition(msgSegments);
         }
      }
   } while (strMessage != "");
}

void SendMsg(const string& msg) {
   if (glbClientSocket && glbClientSocket.IsSocketConnected()) {
      glbClientSocket.Send(msg + "\n");
      Print("Sent message: ", msg);
   } else {
      Print("Could not send message: lost connection! ", msg);
   }   
}

void Subscribe() {
   string accountType = StringSubstr( EnumToString((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE)), 19);
   string msg = StringFormat(
         "{ \"action\": \"subscribe\",\"token\": \"%s\",\"account_name\": \"%s\", \"account_type\": \"%s\", \"account_number\": %d, \"company\": \"%s\", \"account_server\": \"%s\", \"currency\": \"%s\", \"leverage\": %d, \"free_margin\": %f, \"balance\": %f, \"equity\": %f}\n", 
         AuthKey, AccountName(), accountType, AccountNumber(), AccountCompany(), AccountServer(), AccountCurrency(), AccountLeverage(), AccountFreeMargin(), AccountBalance(), AccountEquity()
      );
   SendMsg(msg);
   isSubscribed = true;
}

int OrderTypeStringToInt(string strOrderType) {
   if (strOrderType == "Buy") return OP_BUY;
   if (strOrderType == "Sell") return OP_SELL;
   if (strOrderType == "Buylimit") return OP_BUYLIMIT;
   if (strOrderType == "Selllimit") return OP_SELLLIMIT;
   if (strOrderType == "Buystop") return OP_BUYSTOP;
   // if (strOrderType == "Sellstop")
   return OP_SELLSTOP;
}

void HearBeat() {
   int frequencyInMinutes = 30;
   int currentMinute = TimeMinute(TimeCurrent());
   if ((currentMinute % frequencyInMinutes) == 0) {
      string msg = "{ \"action\": \"heart_beat\" }";
      SendMsg(msg);
   }
}
