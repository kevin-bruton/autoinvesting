<?php

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
  } catch (msqli_exception $e) {
    die($e->__toString());
  }
}

function validateUser ($db, $username, $passwd) {
  $sql = 'SELECT userId, username, accountType FROM Users WHERE username=? AND passwd=?';
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
      return $user['accountType'];
    }
    return null;
  } catch (mysqli_exception $e) {
    die($e->__toString());
  }
}
?>