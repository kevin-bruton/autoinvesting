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
  $sql = 'INSERT INTO Strategies (strategyName, magic, symbols, timeframes, generationDate, demoDate, liveDate, mq4StrategyFile, sqxStrategyFile) VALUES (?,?,?,?,?,?,?,?,?)';
  try {
    /* Prepared statement, stage 1: prepare */
    $stmt = $db->prepare($sql);

    /* Prepared statement, stage 2: bind and execute */
    $stmt->bind_param(
      "sisssssss",
      $strategyDetails->strategyName,
      $strategyDetails->magic,
      $strategyDetails->symbols,
      $strategyDetails->timeframes,
      $strategyDetails->generationDate,
      $strategyDetails->demoDate,
      $strategyDetails->liveDate,
      $strategyDetails->mt4StrategyFile,
      $strategyDetails->sqxStrategyFile
    ); // "is" means that $id is bound as an integer and $label as a string
    $stmt->execute();
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
  die('{"success": '.boolval($stmt->affected_rows).'}');
}

function insertTrade($strategyName, $symbol, $environment, $platform, $direction, $size, $profit, $openTime, $closeTime, $openPrice, $closePrice, $closeType, $comment) {
  // $openTime = "2020-04-05 06:00:00";
  // $closeTime = "2020-04-05 07:00:00";
  global $db;
  $sql = 'INSERT INTO Trades (strategyName, symbol, environment, platform, direction, size, profit, openTime, closeTime, openPrice, closePrice, closeType, comment) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)';
  try {
    $stmt = $db->prepare($sql);

    $stmt->bind_param(
      'sssssddssddss',
      $strategyName, $symbol, $environment, $platform, $direction, $size, $profit, $openTime, $closeTime, $openPrice, $closePrice, $closeType, $comment
    );
    $stmt->execute();
  } catch (\mysqli_sql_exception $e) {
    die(errorToJson($e));
  }
}
?>
