<?php

function errorToJson($e) {
  return json_encode(array(
    'success' => 0  ,
    'message' => $e->getMessage(),
    'code' => $e->getCode(),
    'file' => $e->getFile(),
    'line' => $e->getLine(),
    'trace' => $e->getTraceAsString()
  ));
}

function connect () {
  mysqli_report(MYSQLI_REPORT_ALL & ~MYSQLI_REPORT_INDEX);

  $servername = $_ENV['DB_SERVERNAME'];
  $username = $_ENV['DB_USERNAME'];
  $password = $_ENV['DB_PASSWORD'];
  $dbName = $_ENV['DB_NAME'];

  // Create connection
  try {
    $db = new mysqli($servername, $username, $password);
    
    $db->select_db($dbName);
    return $db;
  } catch (\msqli_sql_exception $e) {
    die(errorToJson($e));
  }
}

function validateUser ($username, $passwd) {
  global $db;
  $sql = 'SELECT userId, username, firstname, lastname, accountType FROM Users WHERE username=? AND passwd=?';
  try {
    $stmt = $db->stmt_init();
    /* Prepared statement, stage 1: prepare */
    $stmt = $db->prepare($sql);

    /* Prepared statement, stage 2: bind and execute */
    $stmt->bind_param("ss", $username, $passwd); // "is" means that $id is bound as an integer and $label as a string

    $stmt->execute();
    
    $result = $stmt->get_result();
    $user = $result->fetch_assoc();
    if ($user) {
      return $user;
    }
    return null;
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
}

function insertStrategy ($strategyDetails) {
  global $db;
  /* echo $strategyDetails->magic;
  exit; */
  $sql = 'INSERT INTO Strategies (strategyName, magic, symbols, timeframes, demoStart, mq4StrategyFile, sqxStrategyFile) VALUES (?,?,?,?,?,?,?)';
  try {
    /* Prepared statement, stage 1: prepare */
    $stmt = $db->prepare($sql);

    /* Prepared statement, stage 2: bind and execute */
    $stmt->bind_param(
      "sisssss",
      $strategyDetails->strategyName,
      $strategyDetails->magic,
      $strategyDetails->symbols,
      $strategyDetails->timeframes,
      $strategyDetails->demoStart,
      $strategyDetails->mt4StrategyFile,
      $strategyDetails->sqxStrategyFile
    ); // "is" means that $id is bound as an integer and $label as a string
    $stmt->execute();
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
  die('{"success": '.boolval($stmt->affected_rows).'}');
}

function updateStrategyWithBacktest ($strategyName, $btStart, $btEnd, $btDeposit, $btTrades, $btKpis) {
  // die('strategyName: '.$strategyName.'; start: '.$btStart.'; end: '.$btEnd.'; deposit: '.$btDeposit.'; trades: '.$btTrades.'; kpis: '.$btKpis);
  global $db;
  $sql = 'UPDATE Strategies SET btStart = ?, btEnd = ?, btDeposit = ?, btTrades = ?, btKpis = ? WHERE StrategyName = ?';
  try {
    $stmt = $db->prepare($sql);
    $stmt->bind_param(
      "ssdsss",
      $btStart, $btEnd, $btDeposit, $btTrades, $btKpis, $strategyName
    );
    $stmt->execute();
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
  return boolval($stmt->affected_rows);
  // die('Num rows: '.$stmt->affected_rows.'; error: '.$stmt->error);
  // return boolval($stmt->affected_rows);
  // die('{ "success": '.boolval($stmt->affected_rows).' }');
}

/* function insertTrade($strategyName, $magic, $symbol, $environment, $platform, $direction, $size, $profit, $openTime, $closeTime, $openPrice, $closePrice, $closeType, $comment) {
  // $openTime = "2020-04-05 06:00:00";
  // $closeTime = "2020-04-05 07:00:00";
  global $db;
  $sql = 'INSERT INTO Trades (strategyName, magic, symbol, environment, platform, direction, size, profit, openTime, closeTime, openPrice, closePrice, closeType, comment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)';
  try {
    $stmt = $db->prepare($sql);

    $stmt->bind_param(
      'sissssddssddss',
      $strategyName, $magic, $symbol, $environment, $platform, $direction, $size, $profit, $openTime, $closeTime, $openPrice, $closePrice, $closeType, $comment
    );
    $stmt->execute();
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
} */

function selectStrategies() {
  global $db;
  $sql = 'SELECT * FROM Strategies';
  try {
    $result = $db->query($sql);
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
  $strategies = array();
  while ($row = $result->fetch_assoc()) {
    array_push($strategies, $row);
  }
  $result->free();
  return $strategies;
}

function selectTrades() {
  global $db;
  $sql = 'SELECT * FROM Trades';
  try {
    $result = $db->query($sql);
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
  $trades = array();
  while ($row = $result->fetch_assoc()) {
    $row['profit'] = (float)$row['profit'];
    $row['tradeId'] = (float)$row['tradeId'];
    $row['size'] = (float)$row['size'];
    $row['openPrice'] = (float)$row['openPrice'];
    $row['closePrice'] = (float)$row['closePrice'];
    array_push($trades, $row);
  }
  $result->free();
  return $trades;
}
?>
