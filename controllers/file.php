<?php

declare(strict_types=1);


function saveFile($file) {
  global $db;
  $response = array();
  try {
    
    // Undefined | Multiple Files | $_FILES Corruption Attack
    // If this request falls under any of them, treat it invalid.
    if (!isset($file['error']) || is_array($file['error'])) {
      throw new RuntimeException('Invalid parameters.');
    }
  
    // Check $_FILES['upfile']['error'] value.
    switch ($file['error']) {
      case UPLOAD_ERR_OK:
        break;
      case UPLOAD_ERR_NO_FILE:
        throw new RuntimeException('No file sent.');
      case UPLOAD_ERR_INI_SIZE:
      case UPLOAD_ERR_FORM_SIZE:
        throw new RuntimeException('Exceeded filesize limit. Before manual check. Size:'.$file['size']);
      default:
        throw new RuntimeException('Unknown error');
    }
  
    // You should also check filesize here. 
    if ($file['size'] > 10000000) {
      throw new RuntimeException('Exceeded filesize limit. Size:'.$file['size']);
    }

    if (($file['name'] != "")) {
      // Where the file is going to be stored
      $filenameOnly = $file['name'];
      $path = pathinfo($filenameOnly);
      $filename = $path['filename'];
      $ext = $path['extension'];
      $temp_name = $file['tmp_name'];
      if ($ext == 'mq4')
        $target_dir = 'files/mt4/';
      else if ($ext == 'sqx')
        $target_dir = 'files/sqx/';
    } else {
      throw new RuntimeException('Not a valid file type');
    }
    $path_filename_ext = $target_dir.$filename.".".$ext;
       
    // Check if file already exists
    if (file_exists($path_filename_ext)) {
      throw new RuntimeException('File already exists');
    } else {
      if (move_uploaded_file($temp_name,$path_filename_ext)) {
        $response = array(
          "success" => true,
          "message" => "File uploaded successfully"
        );
      } else {
        throw new RuntimeException('Error saving file');
      }
    }
    echo json_encode($response);
  
  } catch (RuntimeException $e) {
    $response = array(
      "success" => false,
      "message" => $e->getMessage()
    );
    echo json_encode($response);
  }
  exit;
}

?>
