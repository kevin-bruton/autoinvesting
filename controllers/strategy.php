<?php

declare(strict_types=1);

require_once('./db/db.php');

function saveStrategy ($strategyDetails) {
  insertStrategy($strategyDetails);
}

?>
