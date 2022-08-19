#property strict

#define SOCKET_LIBRARY_USE_EVENTS
#include <sockets.mqh>

input string AuthKey = "GwD22oS3@KRp";

string Hostname = "127.0.0.1";
ushort ServerPort = 5000;
bool isAuthorized = false;
bool isSubscribed = false;
ClientSocket * sock = NULL;

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
   if (sock) {
      delete sock;
      sock = NULL;
   }
   setStatusConnected(false);
}

void OnTimer() {
   if (!sock) {
      initSock();
   }
   if (sock) {
      if (!sock.IsSocketConnected()) {
         deleteSock();
      } else {
         setStatusConnected(true);
         ReadMessages();
      }
   }
}

void initSock() {
   sock = new ClientSocket(Hostname, ServerPort);
   if (sock && sock.IsSocketConnected()) {
      Subscribe();
   }
}

void deleteSock() {
   delete sock;
   sock = NULL;
   setStatusConnected(false);
   setAuthorized(false);
   setSubscribed(false);
}

int getOrderType(string type) {
   if (type == "buylimit") return OP_BUYLIMIT;
   if (type == "selllimit") return OP_SELLLIMIT;
   if (type == "buystop") return OP_BUYSTOP;
   if (type == "sellstop") return OP_SELLSTOP ;
   return 6;
}

void ReadMessages() {
   // Read any messages on the socket
   string strMessage;
   do {
      strMessage = sock.Receive("\n");
      // Print("ReceiveWithHeader: " + strMessage);
      if (strMessage != "") {
         Print("Received message: ", strMessage);
         string msgSegments[];
         StringSplit(strMessage,StringGetCharacter("|",0),msgSegments);
         if (ArraySize(msgSegments) > 0) {
            string keyVal[];
            StringSplit(msgSegments[0],StringGetCharacter(":",0),keyVal);
            if (keyVal[0] == "authorized") {                   // Handle authorization/subscription response
               setAuthorized(keyVal[1] == "true");
               StringSplit(msgSegments[1],StringGetCharacter(":",0),keyVal);
               string magics[];
               StringSplit(keyVal[1],StringGetCharacter(",",0),magics);
               setSubscribed(ArraySize(magics) > 0 && isAuthorized);
               Comment("Subscribed to: " + StringTrimRight(keyVal[1]));
            } else if (keyVal[0] == "place_order") {           // Handle place_order
               int order_type = getOrderType(msgSegments[1]);
               string symbol = msgSegments[2];
               double volume = (double)msgSegments[3];
               double open_price = (double)msgSegments[4];
               double sl = (double)msgSegments[5];
               double tp = (double)msgSegments[6];
               string comment = msgSegments[7];
               bool result = OrderSend(symbol, order_type, volume, open_price, 1000, sl, tp, comment);
               Print("Order sent ", result ? "successfully" : "with errors");
            }
         }
      }
   } while (strMessage != "");
}

void Subscribe() {
   // Send a message
   if (sock && sock.IsSocketConnected()) {
      string accountType = StringSubstr( EnumToString((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE)), 19);
      string msg = StringFormat(
         "{ \"action\": \"subscribe\",\"token\": \"%s\",\"account_name\": \"%s\", \"account_type\": \"%s\", \"account_number\": %d, \"company\": \"%s\", \"account_server\": \"%s\", \"currency\": \"%s\", \"leverage\": %d, \"free_margin\": %f, \"balance\": %f, \"equity\": %f}\n", 
         AuthKey, AccountName(), accountType, AccountNumber(), AccountCompany(), AccountServer(), AccountCurrency(), AccountLeverage(), AccountFreeMargin(), AccountBalance(), AccountEquity()
      );
      sock.Send(msg);
   }
   isSubscribed = true;
}
