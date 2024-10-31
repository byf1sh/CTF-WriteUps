<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Page</title>
</head>
<body>
    <h1>Welcome to the Admin Page</h1>

<?php 
error_reporting(0);

if (isset($_GET['pages']) && !empty($_GET['pages']))
{
	$page = "./pages/" . $_GET['pages'] . ".html";
    echo $page;
	include($page);
}
else
{
	echo '<a href="?pages=1"> Link </a>';
}
?>
</body>
</html>
