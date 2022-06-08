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

    // Check connection
    //if ($db->connect_error) {
      //die("Connection failed: " . $conn->connect_error);
    //}
    
    $db->select_db($dbName);
    return $db;
  } catch (msqli_exception $e) {
    die($e->__toString());
  }
}

function validateUser ($db, $username, $passwd) {
  $sql = 'SELECT userId FROM Users WHERE username=? AND passwd=?';
  try {
    $stmt = $db->stmt_init();
    /* Prepared statement, stage 1: prepare */
    $stmt = $db->prepare($sql);

    if (!$stmt) {
      // trigger_error('Error executing MySQL query: ' . $db->error);
      die('Error preparing sql statement: '. htmlspecialchars($db->error));
      exit;
    }

    /* Prepared statement, stage 2: bind and execute */
    $stmt->bind_param("ss", $username, $passwd); // "is" means that $id is bound as an integer and $label as a string

    if (!$stmt->execute()) {
      trigger_error('Error executing MySQL query: ' . $stmt->error);
    }
    $result = $stmt->get_result();
    $user = $result->fetch_assoc();
    return $user != null;
  } catch (mysqli_exception $e) {
    die($e->__toString());
  }
}
?>