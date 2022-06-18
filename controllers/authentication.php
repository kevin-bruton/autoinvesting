<?php

declare(strict_types=1);

use Firebase\JWT\JWT;


function authenticate ($user) {
    $secretKey  = $_ENV['JWT_SECRET'];
    $tokenId    = base64_encode(random_bytes(16));
    $issuedAt   = new DateTimeImmutable();
    $expire     = $issuedAt->modify('+1440 minutes')->getTimestamp();      // Add 60 seconds
    $serverName = $_SERVER['SERVER_NAME'];

    // Create the token as an array
    $data = [
        'iat'  => $issuedAt->getTimestamp(),    // Issued at: time when the token was generated
        'jti'  => $tokenId,                     // Json Token Id: an unique identifier for the token
        'iss'  => $serverName,                  // Issuer
        'nbf'  => $issuedAt->getTimestamp(),    // Not before
        'exp'  => $expire,                      // Expire
        'data' => [                             // Data related to the signer user
            'username' => $user['username'],
            'firstname' => $user['firstname'],
            'lastname' => $user['lastname'],
            'accountType' => $user['accountType']       
        ]
    ];
    
    // Encode the array to a JWT string.
    $jwt = JWT::encode(
      $data,      //Data to be encoded in the JWT
      $secretKey, // The signing key
      'HS512'     // Algorithm used to sign the token, see https://tools.ietf.org/html/draft-ietf-jose-json-web-algorithms-40#section-3
    );
    $resp = ['t' => $jwt];
    echo json_encode($resp);
    exit;
}

function validate ($httpAuth) {
  if (! preg_match('/Bearer\s(\S+)/', $httpAuth, $matches)) {
      header('HTTP/1.1 401 Unautorized');
      echo 'Token not provided';
      exit;
  }
  
  $jwt = $matches[1];
  if (! $jwt || $jwt == 'null') { 
      // No token was able to be extracted from the authorization header
      header('HTTP/1.1 401 Unauthorized');
      echo 'Token not provided';
      exit;
  }
  
  $secretKey  = $_ENV['JWT_SECRET'];
  try {
    $token = JWT::decode($jwt, $secretKey, ['HS512']);
  } catch (Firebase\JWT\ExpiredException $e) {
    header('HTTP/1.1 401 Unauthorized');
    echo 'Session expired';
    exit;
  }
  $now = new DateTimeImmutable();
  $serverName = $_SERVER['SERVER_NAME'];
  
  //consoleLog($token->iss);
  if ($token->iss !== $serverName ||
      $token->nbf > $now->getTimestamp() ||
      $token->exp < $now->getTimestamp())
  {
      header('HTTP/1.1 401 Unauthorized');
      echo 'Invalid credentials';
      exit;
  }
}