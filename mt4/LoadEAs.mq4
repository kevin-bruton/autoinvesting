//+------------------------------------------------------------------+
// This script expects the "EaTemplates" directory to exist in the Files directory
// directory in the MQL4 directory
// This directory should contain template files.
// The template files will be used to open a chart and to load an EA on that chart
// - one for each corresponding template file -
// The template files should have been generated previously
// by the "create_mt_templates.py" script
//+------------------------------------------------------------------+
void OnStart()
  {
   string templateDir = "EaTemplates/";
   string fileFilter = "EaTemplates\\*";
   string filename;
   int i = 1;  
   long search_handle = FileFindFirst(fileFilter, filename);
   Print("Filename: " + filename);
   if(search_handle!=INVALID_HANDLE)
     {
      //--- in a loop, check if the passed strings are the names of files or directories
      do
        {
         ResetLastError();
         //--- if it's a file, the function returns true, and if it's a directory, it returns error ERR_FILE_IS_DIRECTORY
         FileIsExist(templateDir+filename);
         PrintFormat("%d : %s name = %s",i,GetLastError()==ERR_FILE_IS_DIRECTORY ? "Directory" : "File",filename);
         i++;
         if (GetLastError() != ERR_FILE_IS_DIRECTORY)
         {
            OpenChartWithTemplate(filename);
            Sleep(1000);
         }
        }
      while(FileFindNext(search_handle,filename));
      //--- close the search handle
      FileFindClose(search_handle);
      Print("Finished loading EAs!!!");
     }
   else
      Print("Files not found!");
  }
//+------------------------------------------------------------------+

void OpenChartWithTemplate (string filename) 
{
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
      Print("Failed to apply template! Filename: " + filename + "; error code: " + (string)GetLastError());
   }
}
