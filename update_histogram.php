#!/usr/bin/php
<?php



require_once('/var/www/classes/db_php7.class.php');

$db_conn = new database_connection( 'root', 'xxxx', 'pa_philly_campaign_finance', 'localhost' );

$sqlite = new SQLite3('leverage.sqlite');

// Get 2017 candidates
$sql = "SELECT *, camp.id as campaign_id
FROM `sqllite_candidate` c, `sqllite_campaign` camp, `sqllite_candidate_to_committee` comm
WHERE camp.id = comm.sqllite_candidate_id AND comm.committee_id > 0 AND c.id = camp.candidate_id AND camp.year = 2017
ORDER BY c.id";

$candidates = $db_conn->returnObjectArrayFromQuery( $sql );

//print_r($candidates); die();

foreach ( $candidates as $candidate )
{

    $sqlite->exec("DELETE FROM campaign_summary WHERE campaign_id = {$candidate->campaign_id} AND summary_type = 'donation_histogram'");

    $sql = "SELECT ROUND(d.donation_amount, -1) as rounded_amount, count(*) as num_d
FROM `political_donation` d, `political_donation_contribution_type` t
WHERE d.contribution_type_id = t.id AND t.is_donation = 1 AND d.committee_id = {$candidate->committee_id}
GROUP BY ROUND(d.donation_amount, -1)
ORDER BY rounded_amount";

//     AND d.donation_date > '2014-12-31' AND d.donation_date < '2016-01-01'

    $donations = $db_conn->returnObjectArrayFromQuery( $sql );

    foreach ( $donations as $donation )
    {

        $sqlite->exec("INSERT INTO campaign_summary ('campaign_id', 'summary_value', 'summary_level', 'summary_type') 
            VALUES ( {$candidate->campaign_id}, '{$donation->num_d}', '{$donation->rounded_amount}', 'donation_histogram')
        ");


    }


}

?>