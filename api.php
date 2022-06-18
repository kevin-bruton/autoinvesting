<?php

declare(strict_types=1);

require_once('./vendor/autoload.php');

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__);
$dotenv->load();

header('Content-Type: application/json; charset=utf-8');

if (isset($_SERVER['HTTP_AUTHORIZATION']))
  $httpAuth = $_SERVER['HTTP_AUTHORIZATION'];
else
  $httpAuth = '';
$method = $_SERVER['REQUEST_METHOD'];
$requestUri = $_SERVER['REQUEST_URI'];

$path = array_values(array_filter(
  explode('/', str_replace('/api', '', explode('?', $requestUri)[0])),
  function ($val) { return $val != ""; }
));
$params = $_REQUEST;
$payload = file_get_contents('php://input');
$file = isset($_FILES['file']) ? $_FILES['file'] : NULL;

/* echo json_encode([
  'httpAuth' => $httpAuth,
  'method' => $method,
  'requestUri' => $requestUri,
  'path' => $path,
  'params' => $params,
  'payload' => $payload
]);
exit; */

require_once('./db/db.php');
require_once('./controllers/authentication.php');
require_once('./controllers/time.php');
require_once('./controllers/strategy.php');
require_once('./controllers/file.php');
require_once('./controllers/trades.php');

global $db;
$db = connect();

if ($path[0] == 'authenticate') {
  $payload = json_decode($payload);
  $user = validateUser($payload->username, $payload->passwd);
  
  if ($user['accountType']) {
    authenticate($user);
  }
  header('HTTP/1.0 403 Forbidden');
  die('Invalid user credentials');
}

validate($httpAuth);

switch($path[0]) {
  case 'time': getTime(); break;
  case 'strategy':
    if ($method == 'POST') saveStrategy(json_decode($payload));
    break;
  case 'files':
    if ($method == 'POST') saveFile($file);
    break;
  case 'trades':
    if ($method === 'POST') saveTrades($file, $_POST);
    break;
}
?>
