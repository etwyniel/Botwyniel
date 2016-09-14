<?php
    $db_url = $_ENV['CLEARDB_DATABASE_URL'];
    $db_server = substr($db_url, strpos($db_url, "@"), strpos($db_url, "/h") - strpos($db_url, "@")) . "\n";
    $db_username = substr($db_url, strpos($db_url, "//"), strpos($db_url, ":1") - strpos($db_url, "//") - 1) . "\n";
    $db_server = substr($db_url, strpos($db_url, ":1") + 1, strpos($db_url, "@") - strpos($db_url, ":1") - 1);
    //TEMPORARY !!
    echo $db_server;
    echo $db_username;
    echo $db_password;
    $mysql = new mysqli($db_server, $db_username, $db_password, $db_username);
    $query = "SELECT * FROM twitch_follow";
    $r = $mysql->query($query);
    echo "{";
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
