<?php
/**
 * CI CURL PHP installer 
 * @author Tomáš Molinari <tomie.molinari@gmail.com>
 */

// -------------------------------------- CONFIG -------------------------------------- 
$Access_keys = array("A3fa4ef6aDFt1v36742573Qe");
$Allowed_folders = array("/var/www/dev/", "/var/www/pyweb/", "/var/www/toomeenoo/");
define("CLEAR_UPLOADS", 0);
define("LIST_MATCHING", 0);
ini_set("display_errors", 0);



// -------------------------------------- FUNCTIONS -------------------------------------- 
function deleteDirectory($dir) {
    if (!file_exists($dir))
        return true;
    if (!is_dir($dir)) 
        return unlink($dir);
    foreach (scandir($dir) as $item) {
        if ($item == '.' || $item == '..') 
            continue;
        if (!deleteDirectory($dir . DIRECTORY_SEPARATOR . $item))
            return false;
    }
    return rmdir($dir);
}

function folder_is_allowed($folder, $allowed_list){
    foreach($allowed_list as $prefix){
        if(strpos($folder, $prefix) === 0){
            return true;
        }
    }
    return false;
}

function files_are_equal($a, $b)
{
  // Check if filesize is different
  if(filesize($a) !== filesize($b))
      return false;

  // Check if content is different
  $ah = fopen($a, 'rb');
  $bh = fopen($b, 'rb');

  $result = true;
  while(!feof($ah))
  {
    if(fread($ah, 8192) != fread($bh, 8192))
    {
      $result = false;
      break;
    }
  }

  fclose($ah);
  fclose($bh);

  return $result;
}

function mirror_files($f, $t, $b, &$overriden_files_array) {
    $replace_prefix = (isset($_POST["usefile-prefix"]) &&  strlen($_POST["usefile-prefix"])>0)? $_POST["usefile-prefix"]."" : false;
    if (!file_exists($f))
        return 0;
    if (!is_dir($f)){
        if(in_array($t, $overriden_files_array))
            return 0;
        if($replace_prefix && substr(pathinfo($f, PATHINFO_BASENAME),0, strlen($replace_prefix )) === $replace_prefix ){
            echo "[DEPLOY SPECIFIC FILE]".PHP_EOL;
            $t = str_replace($replace_prefix ,"", $t);
            $overriden_files_array[] = $t;
        }
        if(file_exists($t)){
            if(files_are_equal($f, $t)){
                if(LIST_MATCHING)
                    echo "=   ".pathinfo($f, PATHINFO_BASENAME).PHP_EOL;
            }else{
                echo "~   ".pathinfo($f, PATHINFO_BASENAME).PHP_EOL;
                if(!LIST_MATCHING)
                    echo "    (".pathinfo($t, PATHINFO_DIRNAME).")".PHP_EOL;
                @mkdir(pathinfo($b, PATHINFO_DIRNAME), 0777, true);
                @copy($t, $b);
                unlink($t);
                return copy($f, $t)? 1 : 0;
            }
        }else{
            echo "+   ".pathinfo($f, PATHINFO_BASENAME).PHP_EOL;
            if(!LIST_MATCHING)
                echo "    (".pathinfo($t, PATHINFO_DIRNAME).")".PHP_EOL;
            return copy($f, $t);
        }
        return 0;
    }elseif(!file_exists($t)){
        echo "++> ".$t.PHP_EOL;
        mkdir($t, 0777);
    }else{
        if(LIST_MATCHING)
            echo ">>> ".$t.PHP_EOL;
    }
    $count = 0;
    foreach (scandir($f) as $item) {
        if ($item == '.' || $item == '..') 
            continue;
        $count += mirror_files($f.DIRECTORY_SEPARATOR.$item, $t.DIRECTORY_SEPARATOR.$item, $b.DIRECTORY_SEPARATOR.$item, $overriden_files_array);
    }
    return $count;
}



// -------------------------------------- CODE -------------------------------------- 
echo "Init...".PHP_EOL;

if(!isset($_POST) || !in_array($_POST["key"], $Access_keys)){
    echo "Key not match; FAIL"; die();
}
if(!isset($_POST["path"])){
    echo "Install 'path' not defined; FAIL"; die();
}
if(!folder_is_allowed($_POST["path"], $Allowed_folders)){
    echo "Install 'path' is not allowed; FAIL"; die();
}
$update_tmp_dir = __DIR__.DIRECTORY_SEPARATOR."__update/";
if(!file_exists($update_tmp_dir) || !is_dir($update_tmp_dir))
    mkdir($update_tmp_dir, 0777);

if(CLEAR_UPLOADS){
    echo "Clear uploads set!".PHP_EOL;
    die("Status: ".deleteDirectory($update_tmp_dir) ."; FAIL");
}

echo "Compute names...".PHP_EOL;
$hashname = md5(pathinfo($_FILES["file"]["name"], PATHINFO_FILENAME).date("-Y-z-His"));
$target_file = $update_tmp_dir . $hashname . ".zip";

echo "Upload handle...".PHP_EOL;
if (move_uploaded_file($_FILES["file"]["tmp_name"], $target_file)) {
    echo "The zip file has been uploaded...";
    $zip = new ZipArchive;
    $res = $zip->open($target_file);
    if ($res === TRUE) {
        echo "Temp dir and extract...";
        mkdir($update_tmp_dir.$hashname, 0777);
        $bkp_dir = $update_tmp_dir.str_replace("/", "-", trim($_POST["path"], "/")."[backup] ".date("Y-m-d H-i-s"));
        mkdir($bkp_dir, 0777);
        $zip->extractTo($update_tmp_dir.$hashname.'/');
        $zip->close();
        echo "Remove zip...".PHP_EOL;
        unlink($target_file);

        echo "Moving files...".PHP_EOL;
        $overriden_files = array();
        echo "== Moved ".mirror_files($update_tmp_dir.$hashname, rtrim($_POST["path"], "/"), $bkp_dir, $overriden_files)." files".PHP_EOL;

        echo "Remove temp dir...".PHP_EOL;
        deleteDirectory($update_tmp_dir.$hashname);

        echo "Fix permissions dir...".PHP_EOL;
        shell_exec("chmod 777 ".rtrim($_POST["path"], "/")."/ -R");
        shell_exec("chmod 777 ".__DIR__."/ -R");

        die("Finished; OK");
    }else{
        die("Zip open resource not successfull; FAIL"); 
    }
}else{
    die("Move uploaded file was not successfull; FAIL"); 
}