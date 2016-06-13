<html>
<head>
    <meta http-equiv="Content-Type" content="text/html";charset="utf-8">
    <title>DB FOR WOOYUN</title></head>
<body>
<form action="index.php" method="post">
    <table border="0" align="center">
        <tr >
            <td align="center">关键字</td>
        </tr>
        <tr>
            <td align="center">
            <input type="text" name="keyword"  size="50" maxlength="100" />
            </td>
        </tr>
        <tr>
            <td colspan="2" align="center">
                <input type="submit" value="确认" />
            </td>
        </tr>
    </table>
</form>


<?php
    include_once ("wooyundb.php");

    header("Content-Type: text/html;charset=utf-8");
    $tmp = new wooyundb();
    $db = $tmp->connect();
    $sql = "select url,name from bugtest where name regexp ?";

    $stmt = $db->prepare($sql);

    $keyword='';
    $keyword = $_POST["keyword"];
    if ($keyword == NULL)
    {
        exit(0);
    }
    $url="";
    $name="";
    $stmt->bind_param("s",$keyword);
    $stmt->execute();
    $stmt->bind_result($url,$name);
?>


    <table align="center">
    <?php
    if ($keyword == NULL)
    {
        exit(0);
    }
    else
    {
        $document_root = $_SERVER['DOCUMENT_ROOT'];
        $filetime = time();
        $filename = "$document_root/export/$filetime.html";
        $fp = fopen("$filename","w+" );
        $context = "<meta charset='utf-8'>";
        while($stmt->fetch())
        {
            $oneline="";
            $url = "http://www.wooyun.org".$url;
            echo "<tr><td>".$url."</td><td>".$name."</td></tr>";
            $oneline = "<a href=".$url.">".$name."</a><br>";
            $context = $context.$oneline;

        }
        $stmt->close();
        fwrite($fp, $context);
        fclose($fp);
    }
    $zipfilename = "$document_root/export/$filetime.zip";
    $localname = "$filetime.html";
    $zip = new ZipArchive();
    $res =$zip->open($zipfilename,ZIPARCHIVE::CREATE);
    if ($res == TRUE){
        $zip->addFile($filename,$localname);
        echo "<tr><td><a href='./export/$filetime.zip'>下载</a></td></tr>";
        $zip->close();
    }
    else
    {
        echo "<tr>zip error</tr>";
        exit(0);
    }

?>
</table>
</body>
</html>

