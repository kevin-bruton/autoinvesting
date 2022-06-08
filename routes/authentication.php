<?php

declare(strict_types=1);

use Firebase\JWT\JWT;


function authenticate () {
    $secretKey  = $_ENV['JWT_SECRET'];
    $tokenId    = base64_encode(random_bytes(16));
    $issuedAt   = new DateTimeImmutable();
    $expire     = $issuedAt->modify('+60 minutes')->getTimestamp();      // Add 60 seconds
    $serverName = $_SERVER['SERVER_NAME'];
    $username   = "username";                                           // Retrieved from filtered POST data

    // Create the token as an array
    $data = [
        'iat'  => $issuedAt->getTimestamp(),    // Issued at: time when the token was generated
        'jti'  => $tokenId,                     // Json Token Id: an unique identifier for the token
        'iss'  => $serverName,                  // Issuer
        'nbf'  => $issuedAt->getTimestamp(),    // Not before
        'exp'  => $expire,                      // Expire
        'data' => [                             // Data related to the signer user
            'userName' => $username,            // User name
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
      header('HTTP/1.0 400 Bad Request');
      echo 'Token not found in request';
      exit;
  }
  
  $jwt = $matches[1];
  if (! $jwt) {
      // No token was able to be extracted from the authorization header
      header('HTTP/1.0 400 Bad Request');
      exit;
  }
  
  $secretKey  = $_ENV['JWT_SECRET'];
  $token = JWT::decode($jwt, $secretKey, ['HS512']);
  $now = new DateTimeImmutable();
  $serverName = $_SERVER['SERVER_NAME'];
  
  //consoleLog($token->iss);
  if ($token->iss !== $serverName ||
      $token->nbf > $now->getTimestamp() ||
      $token->exp < $now->getTimestamp())
  {
      header('HTTP/1.1 401 Unauthorized');
      exit;
  }
}