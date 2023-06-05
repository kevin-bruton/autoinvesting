//+------------------------------------------------------------------+
//|                                                   CloseAlEas.mq4 |
//|                                  Copyright 2023, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
void OnStart()
  {
   long chartId = ChartFirst();
   for (int i = 0; i < 100; i++)
   {
      Print("Trying to close chart with index: ", i);
      if (chartId < 0)
      {
         Print("chartId less than zero");
         break;
      }
      if (chartId != ChartID())
         ChartClose(chartId);
      chartId = ChartNext(chartId);
   }
  }
//+------------------------------------------------------------------+
