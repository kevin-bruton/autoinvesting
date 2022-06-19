<?php

declare(strict_types=1);

require_once('./db/db.php');

function saveStrategy ($strategyDetails) {
  insertStrategy($strategyDetails);
}

function getStrategies () {
  $strategies = selectStrategies();
  echo '{ "success": true, "data": '.json_encode($strategies).' }';
  exit;
}

function getStrategy ($strategyName) {
  $strategy = selectStrategy(str_replace('-', ' ', $strategyName));
  var_dump($strategy);
  exit;
}

?>
