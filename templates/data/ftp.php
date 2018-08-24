<?php
/* Remote File Name and Path */
$remote_fileA = 'data/temperature/data.json';
$remote_fileB = 'data/pressure/data.json';
$remote_fileC = 'data/humidity/data.json';

/* FTP Account (Remote Server) */
$ftp_host = 'ftp.aslanistan.com'; /* host */
$ftp_user_name = 'aslanista'; /* username */
$ftp_user_pass = 'Texas_2017'; /* password */


/* File and path to send to remote FTP server */
$local_fileA = 'temperature/cleaned/0.json';
$local_fileB = 'pressure/cleaned/0.json';
$local_fileC = 'humidity/cleaned/0.json';

/* Connect using basic FTP */
$connect_it = ftp_connect( $ftp_host );

/* Login to FTP */
$login_result = ftp_login( $connect_it, $ftp_user_name, $ftp_user_pass );

/* Send $local_file to FTP */
if ( ftp_put( $connect_it, $remote_fileA, $local_fileA, FTP_BINARY ) ) {
    echo "WOOT! successfully transfered $local_fileA.";
    echo "<br>";
}
else {
    echo "Doh! there was a problem.";
    echo "<br>";
}
if ( ftp_put( $connect_it, $remote_fileB, $local_fileB, FTP_BINARY ) ) {
    echo "WOOT! successfully transfered $local_fileB.";
    echo "<br>";
}
else {
    echo "Doh! there was a problem.";
    echo "<br>";
}
if ( ftp_put( $connect_it, $remote_fileC, $local_fileC, FTP_BINARY ) ) {
    echo "WOOT! successfully transfered $local_fileC.";
    echo "<br>";
}
else {
    echo "Doh! there was a problem.";
    echo "<br>";
}

/* Close the connection */
ftp_close( $connect_it );
?>