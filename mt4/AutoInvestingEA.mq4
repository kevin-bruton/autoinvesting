#property strict

#define SOCKET_LIBRARY_USE_EVENTS
#include <sockets.mqh>
#include <stdlib.mqh>

// --------------------------------------------------------------------
// EA user inputs
// --------------------------------------------------------------------

input string   Hostname = "127.0.0.1";    // Server hostname or IP address
input ushort   ServerPort = 3000;        // Server port
input string   AuthKey = "GwD22oS3@KRp";              // Authentication Key

int connectionAttempt = 0;
int maxConnectionRetries = 5;
bool doneRetryingConnection = false;
bool isAuthorized = false;
bool isSubscribed = false;

ClientSocket * glbClientSocket = NULL;

void OnInit() {
   EventSetTimer(1);

   ObjectCreate(0,"Title", OBJ_RECTANGLE_LABEL, 0,0,0);
   ObjectSet("Title",OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("Title",OBJPROP_XDISTANCE,400);
   ObjectSet("Title",OBJPROP_YDISTANCE,0);
   // ObjectSet("Title",OBJPROP_BACK,true);
   ObjectSet("Title",OBJPROP_BORDER_TYPE,BORDER_RAISED);
   // ObjectSet("Title",OBJPROP_BGCOLOR,Blue);
   ObjectSet("Title",OBJPROP_XSIZE, 215);
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
}

void setAuthorized (bool isAuth) {
   isAuthorized = isAuth;
   ObjectSet("Authorized",OBJPROP_BGCOLOR,isAuth ? Green : Red);
}

void setSubscribed (bool isSub) {
   isSubscribed = isSub;
   ObjectSet("Subscribed",OBJPROP_BGCOLOR,isSub ? Green : Red);
}

void OnDeinit(const int reason)
{
   Print("OnDeinit");
   EventKillTimer();
   if (glbClientSocket) {
      delete glbClientSocket;
      glbClientSocket = NULL;
   }
   setStatusConnected(false);
}

void OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)
{
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
         Print("Could NOT connect to server " + Hostname + ":" + (string)ServerPort);
      }
   }
   
   
   // If the socket is closed, destroy it, and attempt a new connection
   // on the next call to OnTick()
   if (glbClientSocket && !glbClientSocket.IsSocketConnected()) {
      // Destroy the server socket. A new connection
      // will be attempted on the next tick
      Print("Client disconnected. Will retry " + (string)(maxConnectionRetries - connectionAttempt) + " more times. Socket: " + (string)!!glbClientSocket + " Connected: " + (string)glbClientSocket.IsSocketConnected());
      connectionAttempt++;
      if (!glbClientSocket.IsSocketConnected() && connectionAttempt > maxConnectionRetries) {
         delete glbClientSocket;
         glbClientSocket = NULL;
         setStatusConnected(false);
      }
   } else if (glbClientSocket && glbClientSocket.IsSocketConnected()) {
      connectionAttempt = 0;
      // 'Print("Client is connected");
      if (!isSubscribed) Subscribe();
      ReadMessages();
   } else if (!doneRetryingConnection) {
      Print("Client disconnected. Will NOT retry anymore!");
      doneRetryingConnection = true;
      setStatusConnected(false);
   }
}
// --------------------------------------------------------------------
// Tick handling - set up a connection, if none already active,
// and send the current price quote
// --------------------------------------------------------------------

void OnTick()
{
}

void ReadMessages() {
   // Read any messages on the socket
   string strMessage;
   do {
      strMessage = glbClientSocket.Receive("\n");
      // Print("ReceiveWithHeader: " + strMessage);
      if (strMessage != "") {
         Print("Received message: ", strMessage);
         string msgSegments[];
         StringSplit(strMessage,StringGetCharacter("|",0),msgSegments);
         if (ArraySize(msgSegments) > 0) {
            string action = msgSegments[0];
            if (action == "authorized") {
               Print("Client has been authorized");
               string magics_str = msgSegments[1];
               setAuthorized(true);
               string magics[];
               StringSplit(magics_str, StringGetCharacter(",",0), magics);
               setSubscribed(ArraySize(magics) > 0);
               Comment("Subscribed to: " + magics_str);
            } else if (action == "authorization_failed") {
               Print("Could not authorize with token and account number. Disconnecting...");
               setAuthorized(false);
               setSubscribed(false);
               doneRetryingConnection = true;
               setStatusConnected(false);
               delete glbClientSocket;
               glbClientSocket = NULL;
            } else if (action == "create_order") {
               string order_type = msgSegments[1];
               string symbol= msgSegments[2];
               string volume = msgSegments[3];
               string orig_open_price = msgSegments[4];
               string sl = msgSegments[5];
               string tp = msgSegments[6];
               string comment = msgSegments[7];
               string magic = msgSegments[8];
               string masterOrderId = msgSegments[9];
               double current_open_price;
               if (order_type == "Buy") {
                  current_open_price = MarketInfo(symbol, MODE_ASK);
               } else if (order_type == "Sell") {
                  current_open_price = MarketInfo(symbol, MODE_BID);
               }
               Print("Placing order OrderSend: symbol: ", symbol, " Order type: ", OrderTypeStringToInt(order_type), " Volume: ", volume, " Open Price: ", current_open_price, " Slippage: ", 3, " TP: ", (double)sl, " TP: ", (double)tp, " Comment: ", comment, " Magic: ", (int)magic);
               int ticket = OrderSend(symbol, OrderTypeStringToInt(order_type), (double)volume, current_open_price, 3, (double)sl, (double)tp, comment, (int)magic);
               string msg;
               if (ticket == -1) {
                  string error_msg = "ERROR " + (string)GetLastError() + ": " + ErrorDescription(GetLastError());
                  Print("OrderSend failed. No ticket retrieved. ", error_msg);
                  msg = StringFormat(
                        "{\"action\":\"create_order\",\"status\":\"failed\",\"reason\":\"%s\",\"masterOrderId\":\"%s\",\"orderType\":\"%s\",\"symbol\":\"%s\",\"size\":\"%s\",\"openPrice\":\"%s\",\"sl\":\"%s\",\"tp\":\"%s\",\"comment\":\"%s\",\"magic\":\"%s\"}",
                        error_msg, masterOrderId, order_type, symbol, volume, (string)current_open_price, sl, tp, comment, magic
                     );
               } else {
                  Print("OrderSend placed successfully");
                  bool isSelected = OrderSelect(ticket, SELECT_BY_TICKET);
                  if (isSelected) {
                     string actual_open_price = (string)OrderOpenPrice();
                     string actual_open_time = TimeToStr(OrderOpenTime(),TIME_DATE|TIME_SECONDS);
                     string status;
                     if (order_type == "Buy" || order_type == "Sell") {
                        status = "position_opened";
                     } else {
                        status = "order_placed";
                     }
                     msg = StringFormat(
                        "{\"action\":\"create_order\",\"status\":\"%s\",\"orderId\":\"%s\",\"masterOrderId\":\"%s\",\"orderType\":\"%s\",\"symbol\":\"%s\",\"size\":\"%s\",\"openPrice\":\"%s\",\"openTime\":\"%s\",\"sl\":\"%s\",\"tp\":\"%s\",\"comment\":\"%s\",\"magic\":\"%s\"}",
                        status, (string)ticket, masterOrderId, order_type, symbol, volume, actual_open_price, actual_open_time, sl, tp, comment, magic
                     );
                  } else {
                     string error_msg = "ERROR: Could not select order with orderId: " + (string)ticket;
                     Print("OrderSend failed. ", error_msg);
                     msg = StringFormat(
                           "{\"action\":\"create_order\",\"status\":\"failed\",\"reason\":\"%s\",\"masterOrderId\":\"%s\",\"orderType\":\"%s\",\"symbol\":\"%s\",\"size\":\"%s\",\"openPrice\":\"%s\",\"sl\":\"%s\",\"tp\":\"%s\",\"comment\":\"%s\",\"magic\":\"%s\"}",
                           error_msg, masterOrderId, order_type, symbol, volume, current_open_price, sl, tp, comment, magic
                        );
                  }
               }
               SendMsg(msg);
               
            }
         }
      }
   } while (strMessage != "");
}

void SendMsg(const string& msg) {
   if (glbClientSocket && glbClientSocket.IsSocketConnected()) {
      glbClientSocket.Send(msg);
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

void CheckOrdersPerformed() {
  int i,hstTotal=OrdersHistoryTotal();
  for(i=0;i<hstTotal;i++)
    {
     //---- check selection result
     if(OrderSelect(i,SELECT_BY_POS,MODE_HISTORY)==false)
       {
        OrderPrint();
        Print("Access to history failed with error (",GetLastError(),")");
        break;
       }
    }
}