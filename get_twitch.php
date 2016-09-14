<!DOCTYPE html>
<?php
    $db_url = $_ENV['CLEARDB_DATABASE_URL'];
    $db_server = substr($db_url, strpos($db_url, "@") + 1, strpos($db_url, "/h") - strpos($db_url, "@") - 1);
    $db_username = substr($db_url, strpos($db_url, "//") + 2, strpos($db_url, ":1") - strpos($db_url, "//") - 2);
    $db_password = substr($db_url, strpos($db_url, ":1") + 1, strpos($db_url, "@") - strpos($db_url, ":1") - 1);
    
    $mysql = new mysqli_conn($db_server, $db_username, $db_password, $db_username);
    
    $query = "CREATE TABLE IF NOT EXISTS botwyniel_data (key VARCHAR(32)) ";
    if ($mysql->query($query)) {
        echo "Table created successfully.<br>";
    } else {
        die("Failed to create table: " . $mysql->error);
    }
    $mysql->close();
    for ($a = 0; $a <= $r->num_rows - 2; $a++) {
        $user = $r->fetch_assoc();
        echo '"' . $user['id'] . '":{';
        echo '"discord_username":"' . $user['discord_username'];
        echo '","twitch_username":"' . $user['twitch_username'];
        echo '","id":' . $user['id'];
        echo ', "discriminator":"' . $user['discriminator'];
        echo '", "avatar":"' . $user['avatar'];
        echo '"},';
    }
    $user = $r->fetch_assoc();
    echo '"' . $user['id'] . '":{';
    echo '"discord_username":"' . $user['discord_username'];
    echo '","twitch_username":"' . $user['twitch_username'];
    echo '","id":' . $user['id'];
    echo ', "discriminator":"' . $user['discriminator'];
    echo '", "avatar":"' . $user['avatar'];
    echo '"}}';
?>
