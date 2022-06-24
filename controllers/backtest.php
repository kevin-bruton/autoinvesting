<?php

declare(strict_types=1);

require_once('./db/db.php');

function saveBacktest ($payload) {
  global $db;
  $strategyName = $payload->strategyName;
  $startDate = $payload->startDate;
  $endDate = $payload->endDate;
  $deposit = $payload->deposit;
  $trades = $payload->trades;
  $kpis = $payload->kpis;
  $changed = updateStrategyWithBacktest($strategyName, $startDate, $endDate, $deposit, json_encode($trades), json_encode($kpis));
  // $changed = updateStrategyWithBacktest($strategyName, null, null, null, null, null);
  die('{ "success": true, "message": "Backtest changed='.($changed ? 'true' : 'false').'" }');
}
/* 
function noCom ($str) {
  return str_replace('"', '', $str);
}

function sanitDate ($str) {
  $newStr = str_replace('.', '-', $str);
  return $newStr;
}

function saveBacktest ($file, $payload) {
  global $db;
  $strategyName = $payload['strategyName'];
  $btStart = $payload['btStart'];
  $btEnd = $payload['btEnd'];
  $btDeposit = $payload['btDeposit'];

  $tempName = $file['tmp_name'];
  $filenameOnly = $file['name'];
  $path = pathinfo($filenameOnly);
  $filename = $path['filename'];
  $ext = $path['extension'];
  if ($ext == 'csv' && is_uploaded_file($tempName)) {
    $btTrades = array();
    $contents = file_get_contents($tempName);
    $lines = explode("\n", $contents);
    array_shift($lines);
    foreach($lines as $line) {
      $data = explode(';', $line);
      if (count($data) == 16) {
        // ticket 0, symbol 1, type 2, open time 3, open price 4, size 5, close time 6, close price 7, profit 8, balance 9, sample type 10, close type 11, mae 12, mfe 13, time in trade 14, comment 15
        $data = array_map(fn($value) => noCom($value), $data);
        $trade = array();
        $trade['symbol'] = $data[1];
        $trade['direction'] = $data[2];
        $trade['openTime'] = sanitDate($data[3]);
        $trade['openPrice'] = floatval($data[4]);
        $trade['size'] = floatval($data[5]);
        $trade['closeTime'] = sanitDate($data[6]);
        $trade['closePrice'] = floatval($data[7]);
        $trade['profit'] = floatval($data[8]);
        $trade['balance'] = floatval($data[9]);
        $trade['closeType'] = $data[11];
        $trade['comment'] = $data[15];
        array_push($btTrades, $trade);
      }
    }
    $btKpis = calcKpis($btTrades);
    updateStrategy($strategyName, $btStart, $btEnd, $btDeposit, json_encode($btTrades), $btKpis);
    echo '{ "success": true, "message": "Backtest saved" }';
    exit;
    echo '{ "success": false, "message": "Not a valid backtest file" }';
    exit;
  }
} */

function getBacktest () {
  $trades = selectTrades();
  echo '{ "success": true, "data": '.json_encode($trades).' }';
  exit;
}

function calcKpis ($trades) {
  $grossProfit = 0;
  $grossLoss = 0;
  foreach($trades as $trade) {
    if ($trade['profit'] > 0) {
      $grossProfit += $trade['profit'];
    } else if ($trade['profit'] < 0) {
      $grossLoss -= $trade['profit'];
    }
  }
  $kpis = array();
  $kpis['profitFactor'] = $grossProfit / $grossLoss;
  return json_encode($kpis);
}
?>
