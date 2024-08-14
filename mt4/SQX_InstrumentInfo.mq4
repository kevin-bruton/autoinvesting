#property copyright "Copyright 2023, kev7777"
#property link      ""
#property version   "1.00"
#property description ""
#property strict

/**
* This is an EA that gets all the info needed for instruments in SQX
* Some data is retrieved directly from the web page of Darwinex (via WebRequest)
* and some is retrieved from MetaTrader
* 
* Requisites:
*   - In Tools -> Options, go to the tab "Expert Advisors"
      and add "https://www.darwinex.com/graphics/spreads" as an approved URL
**/
string broker = "Darwinex";

struct SymbolStruct {
   string name;
   string assetType;
};

SymbolStruct symbols[] = {
   { "EURUSD", "forex" },
   { "EURAUD", "forex" },
   { "GBPJPY", "forex" },
   { "AUDUSD", "forex" },
   { "USDCHF", "forex" },
   { "STOXX50E", "indices" },
   { "SP500", "indices" },
   { "NDX", "indices" },
   { "WS30", "indices" },
   { "XAUUSD", "commodities" },
   { "XAGUSD", "commodities" },
};
   
int drawX = 0;
int drawY = 50;
string brokerInfo;

void OnInit()
{
   SetupChart();
   brokerInfo = GetInfoFromBroker();
   PrintHeading();
   for (int i = 0; i < ArraySize(symbols); i++) {
    SymbolSelect(symbols[i].name,true);
    PrintSymbolInfo(symbols[i]);
   }
}

string GetInfoFromBroker () 
{ 
   string method = "GET";
   string url = "https://www.darwinex.com/graphics/spreads?dx_platform=DX";
   string cookies = NULL;
   string referer = NULL;
   int timeout = 5000, dataSize = 0;
   char postData[], response[];
   string responseHeaders;
   int status = WebRequest(method, url, cookies, referer, timeout, postData, dataSize, response, responseHeaders);
   
   if(status == -1) {
      Print("Error in WebRequest. Error code  =",GetLastError());
      //--- Perhaps the URL is not listed, display a message about the necessity to add the address
      MessageBox("Add the address '"+ url + "' in the list of allowed URLs in 'Tools' -> 'Options' in tab 'Expert Advisors'","Error",MB_ICONINFORMATION);
      return "";
   }
   string data = CharArrayToString(response);
   Print("Response from web request:", data);
   return data;
}

void PrintHeading () 
{
   string name = "Heading";
   PrintText(name, "Symbol", "Symbol", 9);
   PrintText(name, "PointValueInUsd", "Point value in $", 9);
   PrintText(name, "PipTickSize", "Pip/Tick Size", 9);
   PrintText(name, "PipTickStep", "Pip/Tick Step", 9);
   PrintText(name, "Spread", "Spread", 9);
   PrintText(name, "CommissionType", "Commission Type", 9);
   PrintText(name, "Commission", "Commission", 9);
   PrintText(name, "SwapLong", "Swap Long", 9);
   PrintText(name, "SwapShort", "Swap Short", 9);
   PrintText(name, "SwapTripleDay", "Triple Swap Day", 9); 
}

double ExchangeCurrency (string from, string to, double amount)
{
   MqlTick tick;
   if (SymbolSelect(from + to, SYMBOL_CURRENCY_BASE)) {
      SymbolInfoTick(from + to, tick);
      return tick.ask * amount;
   } else if (SymbolSelect(to + from, SYMBOL_CURRENCY_BASE)) {
      SymbolInfoTick(to + from, tick);
      if (tick.bid == 0) Print("Could not get exchange rate:", to+from);
      return 1 / tick.bid * amount;
   }
   Print("Could not get a symbol to exchange. From: ", from, "; To: ", to);
   return 0;
}
  
string GetPointValueInUsd (SymbolStruct &symbol) {
   double contractSize = MarketInfo(symbol.name, MODE_LOTSIZE);
   if (symbol.assetType == "forex") {
      string quoteCurrency = StringSubstr(symbol.name, 3);
      if (quoteCurrency == "USD")
         return DoubleToStr(contractSize, 2);
      else
         return DoubleToStr(ExchangeCurrency(quoteCurrency, "USD", contractSize), 0);
   } else if (symbol.assetType == "index") {
      string indexCurrency = SymbolInfoString(symbol.name, SYMBOL_CURRENCY_MARGIN);
      Print("Index Currency: '", indexCurrency, "'");
      if (indexCurrency == "USD")
         return DoubleToStr(contractSize, 2);
      else
         return DoubleToStr(ExchangeCurrency(indexCurrency, "USD", contractSize), 2);
   }
   // Not forex or index
   return DoubleToStr(contractSize, 2);
}

string GetPipTickSize (SymbolStruct &symbol)
{
   double contractSize = MarketInfo(symbol.name, MODE_LOTSIZE);
   int pipValue = 10;
   if (symbol.assetType == "forex")
   {
      string quoteCurrency = StringSubstr(symbol.name, 3);
      if (quoteCurrency == "JPY")
         pipValue = 1000;
      else
         pipValue = 10;
      return (string)(pipValue / contractSize);
   } else if (symbol.assetType == "index") {
      double dwxTickSize = (double)GetBrokerSymbolInfo(symbol, "tickSize");
      Print("dwxTickSize: ", dwxTickSize, "; contractSize: ", contractSize);
      return DoubleToStr(dwxTickSize * contractSize, 2);
   }
   return (string)(pipValue / contractSize);
}

string GetPipTickStep (SymbolStruct &symbol)
{
   long decimals = SymbolInfoInteger(symbol.name, SYMBOL_DIGITS);
   return DoubleToStr(1/MathPow(10, decimals), (int)decimals);
}

string GetSpread (SymbolStruct &symbol)
{
   MqlTick tick;
   SymbolInfoTick(symbol.name, tick);
   double rawSpread = MarketInfo(symbol.name, MODE_SPREAD); //(int)MathRound((tick.ask - tick.bid) * MarketInfo(symbol.name, MODE_LOTSIZE));
   string adjustedSpread = DoubleToStr(rawSpread * (double)GetPipTickStep(symbol) / (double)GetPipTickSize(symbol), 5);
   // Print(symbol.name, " Spread: ", tick.ask - tick.bid, " Raw Spread: ", rawSpread, " Adjusted Spread: ", adjustedSpread, " Direct: ", MarketInfo(symbol.name, MODE_SPREAD));
   return adjustedSpread;
}

string GetCommissionType (SymbolStruct &symbol) {
   if (symbol.assetType == "forex") {
      return "Size";
   } else if (symbol.assetType == "indices") {
      return "Size";
   } else if (symbol.assetType == "commodities") {
      return "Percentage";
   } else {
      return "Unknown";
   }
}

string GetBrokerSymbolInfo (SymbolStruct &symbol, string key)
{
   int startIdx = StringFind(brokerInfo, "\"asset\":\"" + symbol.name + "\"");
   string symbolInfo = StringSubstr(brokerInfo, startIdx);
   int keyIdx = StringFind(symbolInfo, key);
   string keyStr = StringSubstr(symbolInfo, keyIdx, 50);
   int valueIdx = StringFind(keyStr, ":");
   string keyValue = StringSubstr(keyStr,valueIdx);
   int endValueIdx = StringFind(keyValue, ",");
   string rawValue = StringSubstr(keyValue, 1, endValueIdx - 1);
   if (StringSubstr(rawValue, 0, 1) == "\"" && StringSubstr(rawValue, StringLen(rawValue) - 1, 1) == "\"") {
      return StringSubstr(rawValue, 1, StringLen(rawValue) - 2);
   } else {
      return rawValue;
   }
}

string GetCommission (SymbolStruct &symbol)
{
   double rawCommission = (double)GetBrokerSymbolInfo(symbol,"commission");
   string currency = (string)GetBrokerSymbolInfo(symbol, "currency");
   if (currency == "USD")
      return DoubleToStr(rawCommission * 2, 4); // Double commission for complete trades
   else
      return DoubleToStr(ExchangeCurrency(currency, "USD", rawCommission) * 2, 4); // Double commission for complete trades
}

string GetSwapLong (SymbolStruct &symbol)
{
   double swapLong = (double)GetBrokerSymbolInfo(symbol, "swapLong");
   Print(symbol.name, " raw swap long:", swapLong);
   string currency = "";
   if (symbol.assetType == "forex") {
      currency = StringSubstr(symbol.name, 3);
   } else if (symbol.assetType == "indices") {
      currency = (string)GetBrokerSymbolInfo(symbol, "currency");
   } else if (symbol.assetType == "commodities") {
      currency = (string)GetBrokerSymbolInfo(symbol, "currency");
   }
   if (currency == "USD")
      return DoubleToStr(swapLong, 2);
   else
      return DoubleToStr(ExchangeCurrency(currency, "USD", swapLong), 2);
}

string GetSwapShort (SymbolStruct &symbol)
{
   double swapShort = (double)GetBrokerSymbolInfo(symbol, "swapShort");
   string currency = "";
   if (symbol.assetType == "forex") {
      currency = StringSubstr(symbol.name, 3);
   } else if (symbol.assetType == "indices") {
      currency = (string)GetBrokerSymbolInfo(symbol, "currency");
   } else if (symbol.assetType == "commodities") {
      currency = (string)GetBrokerSymbolInfo(symbol, "currency");
   }
   if (currency == "USD")
      return DoubleToStr(swapShort, 2);
   else
      return DoubleToStr(ExchangeCurrency(currency, "USD", swapShort), 2);
}

string GetTripleSwapDay (SymbolStruct &symbol)
{
   long day = SymbolInfoInteger(symbol.name, SYMBOL_SWAP_ROLLOVER3DAYS);
   string swapDay;
   switch((int)day)
   {
      case 0 : swapDay = "Sun"; break;
      case 1 : swapDay = "Mon"; break;
      case 2 : swapDay = "Tue"; break;
      case 3 : swapDay = "Wed"; break;
      case 4 : swapDay = "Thu"; break;
      case 5 : swapDay = "Fri"; break;
      case 6 : swapDay = "Sat"; break;
      case 7 : swapDay = "Sun"; break;
   }
   return swapDay;
}
  
void PrintSymbolInfo(SymbolStruct &symbol)
  {
   PrintText(symbol.name,"Name", symbol.name, 12, true);
   PrintText(symbol.name, "PointValue", (string)GetPointValueInUsd(symbol));
   PrintText(symbol.name, "PipTickSize", GetPipTickSize(symbol));
   PrintText(symbol.name, "PipTickStep", GetPipTickStep(symbol));
   PrintText(symbol.name, "Spread", GetSpread(symbol));
   PrintText(symbol.name, "CommissionType", GetCommissionType(symbol));
   PrintText(symbol.name, "Commission", GetCommission(symbol));
   PrintText(symbol.name, "SwapLong", GetSwapLong(symbol));
   PrintText(symbol.name, "SwapShort", GetSwapShort(symbol));
   PrintText(symbol.name, "TripleSwapDay", GetTripleSwapDay(symbol));
}

void PrintText(string symbol, string field, string value, int fontSize = 12, bool onNewLine = false)
{
   string fontType = "Consolas";
   int fontColor = clrBlack;
   int lineSize = 20;
   int cellSize = 120;
   
   if (onNewLine) {
      drawX = cellSize;
      drawY += lineSize;
   } else {
      drawX += cellSize;
   }
   string name = symbol + "_" + field;
   ObjectDelete(name);
   ObjectCreate(name, OBJ_LABEL, 0,0,0);
   ObjectSet(name, OBJPROP_CORNER, 0);
   ObjectSet(name, OBJPROP_XDISTANCE, drawX);
   ObjectSet(name, OBJPROP_YDISTANCE, drawY);
   ObjectSet(name, OBJPROP_BACK, false);
   ObjectSetText(name, value, fontSize, fontType, fontColor);
}

void SetupChart () {
   ChartSetInteger(0, CHART_COLOR_BACKGROUND, White);
   ChartSetInteger(0, CHART_COLOR_FOREGROUND, White);
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
