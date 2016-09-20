<?php
    $db_url = $_ENV['CLEARDB_DATABASE_URL'];
    $db_server = substr($db_url, strpos($db_url, "@") + 1, strpos($db_url, "/h") - strpos($db_url, "@") - 1);
    $db_username = substr($db_url, strpos($db_url, "//") + 2, strpos($db_url, ":1") - strpos($db_url, "//") - 2);
    $db_password = substr($db_url, strpos($db_url, ":1") + 1, strpos($db_url, "@") - strpos($db_url, ":1") - 1);
    $db_database = substr($db_url, strpos($db_url, "/h") + 1, strpos($db_url, "?") - strpos($db_url, "/h") - 1);

    $key = $_POST['key'];
    $value = $_POST['value'];

    $mysql = new mysqli($db_server, $db_username, $db_password, $db_database);

    $query = "UPDATE botwyniel_data SET val= '" . $value . "' WHERE name='" . $key .  "';";
    if ($mysql->query($query)) {
        echo "Values updated successfully.<br>";
    } else {
        die("Failed to update values: " . $mysql->error);
    }
    $mysql->close();
?>
