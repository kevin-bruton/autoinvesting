<?php

declare(strict_types=1);

require_once('../vendor/autoload.php');

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__.'/..');
$dotenv->safeLoad();

header('Content-Type: application/json; charset=utf-8');

if (isset($_SERVER['HTTP_AUTHORIZATION']))
  $httpAuth = $_SERVER['HTTP_AUTHORIZATION'];
else
  $httpAuth = '';
$method = $_SERVER['REQUEST_METHOD'];
$path = array_values(array_filter(
  explode('/', str_replace('/api', '', explode('?', $_SERVER['REQUEST_URI'])[0])),
  function ($val) { return $val != ""; }
));
$params = $_REQUEST;
$payload = file_get_contents('php://input');

require_once('../api/authentication.php');
require_once('../api/time.php');

if ($path[0] == 'authenticate') {
  authenticate($payload);
}

validate($httpAuth);

switch($path[0]) {
  case 'time': getTime();
}
?>
