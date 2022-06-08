<?php

declare(strict_types=1);

function getTime () {
  $timeStr =  (new \DateTimeImmutable())->getTimestamp();
  echo json_encode(['currentTime' => $timeStr]);
}
