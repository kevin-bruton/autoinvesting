<?php

declare(strict_types=1);

require_once('./vendor/autoload.php');

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__.'.');
$dotenv->safeLoad();

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

/* echo json_encode([
  'httpAuth' => $httpAuth,
  'method' => $method,
  'requestUri' => $requestUri,
  'path' => $path,
  'params' => $params,
  'payload' => $payload
]);
exit; */

require_once('./db/base.php');
require_once('./routes/authentication.php');
require_once('./routes/time.php');

global $db;
$db = connect();

if ($path[0] == 'authenticate') {
  $payload = json_decode($payload);
  $user = validateUser($db, $payload->username, $payload->passwd);
  
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
    if ($method == 'POST') saveStrategy($payload);
    break;
  case 'file':
    if ($method == 'POST') saveFile($payload);
    break;
}
?>
