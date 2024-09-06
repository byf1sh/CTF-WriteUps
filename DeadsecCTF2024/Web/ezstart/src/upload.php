<?php

session_start();

function is_malware($file_path)
{
    $content = file_get_contents($file_path);
    
    if (strpos($content, '<?php') !== false) {
        return true; 
    }
    
    return false;
}

function is_image($path, $ext)
{
    // Define allowed extensions
    $allowed_extensions = ['png', 'jpg', 'jpeg', 'gif'];
    
    // Check if the extension is allowed
    if (!in_array(strtolower($ext), $allowed_extensions)) {
        return false;
    }
    
    // Check if the file is a valid image
    $image_info = getimagesize($path);
    if ($image_info === false) {
        return false;
    }
    
    return true;
}

if (isset($_FILES) && !empty($_FILES)) {

    $uploadpath = "tmp/";
    
    $ext = pathinfo($_FILES["files"]["name"], PATHINFO_EXTENSION);
    $filename = basename($_FILES["files"]["name"], "." . $ext);

    $timestamp = time();
    $new_name = $filename . '_' . $timestamp . '.' . $ext;
    $upload_dir = $uploadpath . $new_name;

    if ($_FILES['files']['size'] <= 10485760) {
        move_uploaded_file($_FILES["files"]["tmp_name"], $upload_dir);
    } else {
        echo $error2 = "File size exceeds 10MB";
    }

    if (is_image($upload_dir, $ext) && !is_malware($upload_dir)){
        $_SESSION['context'] = "Upload successful";
    } else {
        $_SESSION['context'] = "File is not a valid image or is potentially malicious";
    }
    
    echo $upload_dir;
    unlink($upload_dir);
}

?>
