<?php

class wooyundb
{
    private $db_host;
    private $db_name;
    private $db_passwd;
    private $db_database;


    function  __construct()
    {
        $this->db_host="localhost";
        $this->db_name="wooyun";
        $this->db_passwd="wooyun";
        $this->db_database="wooyun";

    }
    function connect()
    {
        $db =  new mysqli($this->db_host,$this->db_name,$this->db_passwd,$this->db_database);
        $db->select_db("wooyun");
        if(mysqli_connect_errno())
        {
            echo "db error";
            exit(0);
        }
        $db->query("set names 'utf8'");
        return $db;
    }

}
?>
