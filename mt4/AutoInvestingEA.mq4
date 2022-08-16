#property strict

// --------------------------------------------------------------------
// Include socket library
// --------------------------------------------------------------------

#define SOCKET_LIBRARY_USE_EVENTS
#include <sockets.mqh>


// --------------------------------------------------------------------
// EA user inputs
// --------------------------------------------------------------------

input string   Hostname = "127.0.0.1";    // Server hostname or IP address
input ushort   ServerPort = 5000;        // Server port
input string   AuthKey = "GwD22oS3@KRp";              // Authentication Key

int connectionFailedCount = 0;
int maxConnectionRetries = 5;
bool doneRetryingConnection = false;
bool subscribed = false;

// --------------------------------------------------------------------
// Global variables and constants
// --------------------------------------------------------------------

ClientSocket * glbClientSocket = NULL;

// --------------------------------------------------------------------
// Initialisation (no action required)
// --------------------------------------------------------------------

void OnInit() {
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
   
   ObjectCreate(0,"AuthorisedLabel",OBJ_LABEL,0,0,0);
   ObjectSet("AuthorisedLabel",OBJPROP_CORNER,CORNER_LEFT_UPPER);
   ObjectSet("AuthorisedLabel",OBJPROP_XDISTANCE,410);
   ObjectSet("AuthorisedLabel",OBJPROP_YDISTANCE,70);
   ObjectSetText("AuthorisedLabel","Authorized:",14,"Arial",Black);
   
   ObjectCreate(0,"Authorised", OBJ_RECTANGLE_LABEL, 0,0,0);
   ObjectSet("Authorised",OBJPROP_ANCHOR,ANCHOR_UPPER);
   ObjectSet("Authorised",OBJPROP_XDISTANCE,570);
   ObjectSet("Authorised",OBJPROP_YDISTANCE,70);
   ObjectSet("Authorised",OBJPROP_BORDER_TYPE,BORDER_FLAT);
   ObjectSet("Authorised",OBJPROP_BGCOLOR,White);
   ObjectSet("Authorised",OBJPROP_XSIZE, 20);
   ObjectSet("Authorised", OBJPROP_YSIZE, 20);
   
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
   
//---
}

void setStatusConnected (bool isConnected) {
   if (isConnected) {
      ObjectSet("Connected",OBJPROP_BGCOLOR,Green);
   } else {
      ObjectSet("Connected",OBJPROP_BGCOLOR,Red);
   }
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
         ReadMessages();
      } else {
         // Doesn't match a socket. Assume real key pres
      }
   }
}

void OnTimer() {
   // Connect to socket server
   if (!glbClientSocket && connectionFailedCount < maxConnectionRetries) {
      glbClientSocket = new ClientSocket(Hostname, ServerPort);
      if (glbClientSocket.IsSocketConnected()) {
         Print("Connected to server successfully");
         setStatusConnected(true);
      } else {
         Print("Could NOT connect to server " + Hostname + ":" + (string)ServerPort);
      }
   }
   
   if (!subscribed) Subscribe();
   
   // If the socket is closed, destroy it, and attempt a new connection
   // on the next call to OnTick()
   if (glbClientSocket && !glbClientSocket.IsSocketConnected()) {
      // Destroy the server socket. A new connection
      // will be attempted on the next tick
      Print("Client disconnected. Will retry " + (string)(maxConnectionRetries - connectionFailedCount) + " more times");
      connectionFailedCount++;
      delete glbClientSocket;
      glbClientSocket = NULL;
      setStatusConnected(false);
   } else if (glbClientSocket && glbClientSocket.IsSocketConnected()) {
      connectionFailedCount = 0;
      // 'Print("Client is connected");
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
         // Handle received message here
      }
   } while (strMessage != ""); 
}

void Subscribe() {
   // Send a message
   if (glbClientSocket && glbClientSocket.IsSocketConnected()) {
      string accountType = StringSubstr( EnumToString((ENUM_ACCOUNT_TRADE_MODE)AccountInfoInteger(ACCOUNT_TRADE_MODE)), 19);
      string msg = StringFormat(
         "{ \"action\": \"subscribe\",\"token\": \"%s\",\"account_name\": \"%s\", \"account_type\": \"%s\", \"account_number\": %d, \"currency\": \"%s\", \"leverage\": %d, \"free_margin\": %f, \"balance\": %f, \"equity\": %f}\n", 
         AuthKey, AccountName(), accountType, AccountNumber(), AccountCurrency(), AccountLeverage(), AccountFreeMargin(), AccountBalance(), AccountEquity()
      );
      glbClientSocket.Send(msg);
   }
   subscribed = true;
}
