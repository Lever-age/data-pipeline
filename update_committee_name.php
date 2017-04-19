#!/usr/bin/php
<?php



require_once('/var/www/classes/db_php7.class.php');

$db_conn = new database_connection( 'root', 'xxxx', 'pa_philly_campaign_finance', 'localhost' );

$sqlite = new SQLite3('leverage.sqlite');

// Get all candidates with committees assigned
$sql = "SELECT *, camp.id as campaign_id
FROM `sqllite_candidate` c, `sqllite_campaign` camp, `sqllite_candidate_to_committee` comm
WHERE camp.id = comm.sqllite_candidate_id AND comm.committee_id > 0 AND c.id = camp.candidate_id
ORDER BY c.id";

$candidates = $db_conn->returnObjectArrayFromQuery( $sql );

//print_r($candidates); die();

foreach ( $candidates as $candidate )
{

    $sqlite->exec("DELETE FROM campaign_summary WHERE campaign_id = {$candidate->campaign_id} AND summary_type = 'committee_name'");

    $sqlite->exec("INSERT INTO campaign_summary ('campaign_id', 'summary_value', 'summary_level', 'summary_type') 
            VALUES ( {$candidate->campaign_id}, '{$candidate->committee_name}', '0', 'committee_name')
        ");

}

?>