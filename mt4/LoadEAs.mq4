
   string separator = "_";
   ushort separator_ch = StringGetCharacter(separator, 0);
   string filenameParts[];
   int k = StringSplit(filename, separator_ch, filenameParts);
   string symbol = filenameParts[0];
   string period = filenameParts[1];
   string magic = filenameParts[2];
   
   ENUM_TIMEFRAMES timeframe = PERIOD_H1;
   if (period == "M30") timeframe = PERIOD_M30;
   if (period == "H1") timeframe = PERIOD_H1;
   if (period == "H4") timeframe = PERIOD_H4;
   if (period == "D1") timeframe = PERIOD_D1;
   
   long chartId = ChartOpen(symbol, timeframe);
   if(ChartApplyTemplate(chartId, "\\Files\\EaTemplates\\" + filename))
   {
      Print("Applied template successfully! Filename: " + filename);
   } else
   {
      Print("Failed to apply template! Filename: " + filename + "; error code: " + GetLastError());
   }
