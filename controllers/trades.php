<?php

declare(strict_types=1);

require_once('./db/db.php');

function noCom ($str) {
  return str_replace('"', '', $str);
}

function sanitDate ($str) {
  $newStr = str_replace('.', '-', $str);
  return noCom($newStr);
}

function toFloat ($str) {
  return floatval(noCom($str));
}

function saveTrades ($file, $payload) {
  global $db;
  $strategyName = $payload['strategyName'];
  $symbol = $payload['symbol'];
  $environment = $payload['environment'];
  $platform = $payload['platform'];

  $tempName = $file['tmp_name'];
  $filenameOnly = $file['name'];
  $path = pathinfo($filenameOnly);
  $filename = $path['filename'];
  $ext = $path['extension'];
  if ($ext == 'csv' && is_uploaded_file($tempName)) {
    $contents = file_get_contents($tempName);
    if ($platform === 'SQX') {
      $lines = explode("\n", $contents);
      array_shift($lines);
      foreach($lines as $line) {
        $data = explode(';', $line);
        if (count($data) == 16) {
          // ticket 0, symbol 1, type 2, open time 3, open price 4, size 5, close time 6, close price 7, profit 8, balance 9, sample type 10, close type 11, mae 12, mfe 13, time in trade 14, comment 15
          $direction = noCom($data[2]);
          $openTime = sanitDate($data[3]);
          $openPrice = toFloat($data[4]);
          $size = toFloat($data[5]);
          $closeTime = sanitDate($data[6]);
          $closePrice = toFloat($data[7]);
          $profit = toFloat($data[8]);
          $closeType = $data[11];
          $comment = $data[15];
          insertTrade($strategyName, $symbol, $environment, $platform, $direction, $size, $profit, $openTime, $closeTime, $openPrice, $closePrice, $closeType, $comment);
        }
      }
    }
    echo '{ "success": true }';
    exit;
  }
}
?>
