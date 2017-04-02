-- phpMyAdmin SQL Dump
-- version 4.6.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 02, 2017 at 06:27 PM
-- Server version: 5.7.17-0ubuntu0.16.04.1
-- PHP Version: 7.0.15-0ubuntu0.16.04.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pa_philly_campaign_finance`
--

DELIMITER $$
--
-- Functions
--
CREATE DEFINER=`root`@`localhost` FUNCTION `slugify` (`dirty_string` VARCHAR(200)) RETURNS VARCHAR(200) CHARSET latin1 BEGIN
    DECLARE x, y , z Int;
    Declare temp_string, new_string VarChar(200);
    Declare is_allowed Bool;
    Declare c, check_char VarChar(1);

    set temp_string = LOWER(dirty_string);

    Set temp_string = replace(temp_string, '&', ' and ');

    Select temp_string Regexp('[^a-z0-9\-]+') into x;
    If x = 1 then
        set z = 1;
        While z <= Char_length(temp_string) Do
            Set c = Substring(temp_string, z, 1);
            Set is_allowed = False;
            If !((ascii(c) = 45) or (ascii(c) >= 48 and ascii(c) <= 57) or (ascii(c) >= 97 and ascii(c) <= 122)) Then
                Set temp_string = Replace(temp_string, c, '-');
            End If;
            set z = z + 1;
        End While;
    End If;

    Select temp_string Regexp("^-|-$|'") into x;
    If x = 1 Then
        Set temp_string = Replace(temp_string, "'", '');
        Set z = Char_length(temp_string);
        Set y = Char_length(temp_string);
        Dash_check: While z > 1 Do
            If Strcmp(SubString(temp_string, -1, 1), '-') = 0 Then
                Set temp_string = Substring(temp_string,1, y-1);
                Set y = y - 1;
            Else
                Leave Dash_check;
            End If;
            Set z = z - 1;
        End While;
    End If;

    Repeat
        Select temp_string Regexp("--") into x;
        If x = 1 Then
            Set temp_string = Replace(temp_string, "--", "-");
        End If;
    Until x <> 1 End Repeat;

    If LOCATE('-', temp_string) = 1 Then
        Set temp_string = SUBSTRING(temp_string, 2);
    End If;

    Return temp_string;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation`
--

CREATE TABLE `political_donation` (
  `id` int(4) UNSIGNED NOT NULL,
  `is_annonymous` tinyint(1) UNSIGNED NOT NULL DEFAULT '0',
  `contributor_id` int(4) UNSIGNED NOT NULL,
  `contributor_type_id` int(4) UNSIGNED NOT NULL,
  `contribution_type_id` int(4) UNSIGNED NOT NULL,
  `committee_id` int(4) UNSIGNED NOT NULL,
  `filing_period_id` int(4) UNSIGNED NOT NULL,
  `employer_name_id` int(4) UNSIGNED NOT NULL,
  `employer_occupation_id` int(4) UNSIGNED NOT NULL,
  `donation_date` datetime NOT NULL,
  `donation_amount` decimal(10,2) NOT NULL,
  `provided_name` varchar(128) NOT NULL,
  `provided_address` varchar(128) NOT NULL,
  `is_fixed_asset` smallint(1) UNSIGNED NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_committee`
--

CREATE TABLE `political_donation_committee` (
  `id` int(4) UNSIGNED NOT NULL,
  `candidate_id` int(4) UNSIGNED NOT NULL DEFAULT '0',
  `is_candidates` int(10) UNSIGNED NOT NULL DEFAULT '0',
  `committee_name` varchar(128) NOT NULL,
  `committee_slug` varchar(48) DEFAULT NULL,
  `committee_description` text,
  `donations_2015` decimal(10,2) DEFAULT '0.00',
  `donations_2016` decimal(10,2) DEFAULT '0.00'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_contribution_type`
--

CREATE TABLE `political_donation_contribution_type` (
  `id` int(4) UNSIGNED NOT NULL,
  `type_name` varchar(128) NOT NULL,
  `type_slug` varchar(32) NOT NULL DEFAULT '',
  `type_description` text
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_contributor`
--

CREATE TABLE `political_donation_contributor` (
  `id` int(4) UNSIGNED NOT NULL,
  `address_id` int(4) NOT NULL DEFAULT '0',
  `name_prefix` varchar(64) NOT NULL DEFAULT '',
  `name_first` varchar(64) NOT NULL DEFAULT '',
  `name_middle` varchar(64) NOT NULL DEFAULT '',
  `name_last` varchar(64) NOT NULL DEFAULT '',
  `name_suffix` varchar(64) NOT NULL DEFAULT '',
  `name_business` varchar(255) NOT NULL DEFAULT '',
  `slug` varchar(64) DEFAULT NULL,
  `is_person` smallint(1) NOT NULL DEFAULT '0',
  `is_business` smallint(1) NOT NULL DEFAULT '0',
  `num_contributions` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `num_committees_contrib_to` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `total_contributed_2015` decimal(10,2) UNSIGNED DEFAULT NULL,
  `total_contributed_2016` decimal(10,2) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_contributor_address`
--

CREATE TABLE `political_donation_contributor_address` (
  `id` int(4) UNSIGNED NOT NULL,
  `address_type` varchar(64) NOT NULL DEFAULT '',
  `addr1` varchar(128) NOT NULL DEFAULT '',
  `addr2` varchar(128) NOT NULL DEFAULT '',
  `po_box` varchar(16) NOT NULL DEFAULT '',
  `city` varchar(64) NOT NULL DEFAULT '',
  `state` varchar(32) NOT NULL DEFAULT '',
  `zipcode` varchar(16) NOT NULL DEFAULT '',
  `slug` varchar(64) DEFAULT NULL,
  `num_individual_contribs` mediumint(8) UNSIGNED NOT NULL DEFAULT '0',
  `num_non_individual_contribs` mediumint(8) UNSIGNED NOT NULL DEFAULT '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_contributor_type`
--

CREATE TABLE `political_donation_contributor_type` (
  `id` int(4) UNSIGNED NOT NULL,
  `type_name` varchar(64) NOT NULL,
  `type_slug` varchar(32) NOT NULL DEFAULT '',
  `type_description` text
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_employer_name`
--

CREATE TABLE `political_donation_employer_name` (
  `id` int(4) UNSIGNED NOT NULL,
  `employer_name` varchar(128) NOT NULL,
  `employer_slug` varchar(32) NOT NULL DEFAULT '',
  `employer_description` text
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_employer_occupation`
--

CREATE TABLE `political_donation_employer_occupation` (
  `id` int(4) UNSIGNED NOT NULL,
  `occupation_name` varchar(64) NOT NULL,
  `occupation_slug` varchar(32) NOT NULL DEFAULT '',
  `occupation_description` text
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `political_donation_filing_period`
--

CREATE TABLE `political_donation_filing_period` (
  `id` int(4) UNSIGNED NOT NULL,
  `period_name` varchar(64) NOT NULL,
  `period_slug` varchar(32) NOT NULL DEFAULT '',
  `period_description` text
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `raw_donations`
--

CREATE TABLE `raw_donations` (
  `id` mediumint(8) UNSIGNED NOT NULL,
  `FilerName` varchar(128) NOT NULL,
  `Year` varchar(32) NOT NULL,
  `Cycle` varchar(32) NOT NULL,
  `DocType` varchar(128) NOT NULL,
  `EntityName` varchar(128) NOT NULL,
  `EntityAddressLine1` varchar(64) NOT NULL,
  `EntityAddressLine2` varchar(64) NOT NULL,
  `EntityCity` varchar(64) NOT NULL,
  `EntityState` varchar(32) NOT NULL,
  `EntityZip` varchar(32) NOT NULL,
  `Occupation` varchar(64) NOT NULL,
  `EmployerName` varchar(128) NOT NULL,
  `EmployerAddressLine1` varchar(64) NOT NULL,
  `EmployerAddressLine2` varchar(64) NOT NULL,
  `EmployerCity` varchar(64) NOT NULL,
  `EmployerState` varchar(32) NOT NULL,
  `EmployerZip` varchar(32) NOT NULL,
  `Date` varchar(32) NOT NULL,
  `Amount` varchar(32) NOT NULL,
  `Description` varchar(255) NOT NULL,
  `Amended` varchar(64) NOT NULL,
  `SubDate` varchar(32) NOT NULL,
  `FiledBy` varchar(128) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `political_donation`
--
ALTER TABLE `political_donation`
  ADD PRIMARY KEY (`id`),
  ADD KEY `contributor_id` (`contributor_id`),
  ADD KEY `contributor_type_id` (`contributor_type_id`),
  ADD KEY `contribution_type_id` (`contribution_type_id`),
  ADD KEY `committee_id` (`committee_id`),
  ADD KEY `filing_period_id` (`filing_period_id`),
  ADD KEY `donation_date` (`donation_date`),
  ADD KEY `donation_amount` (`donation_amount`),
  ADD KEY `employer_name_id` (`employer_name_id`,`employer_occupation_id`);

--
-- Indexes for table `political_donation_committee`
--
ALTER TABLE `political_donation_committee`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `committee_name` (`committee_name`),
  ADD KEY `committee_slug` (`committee_slug`);

--
-- Indexes for table `political_donation_contribution_type`
--
ALTER TABLE `political_donation_contribution_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `type_name` (`type_name`),
  ADD KEY `type_slug` (`type_slug`);

--
-- Indexes for table `political_donation_contributor`
--
ALTER TABLE `political_donation_contributor`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `slug` (`slug`),
  ADD KEY `name_first` (`name_first`),
  ADD KEY `name_last` (`name_last`),
  ADD KEY `name_prefix` (`name_prefix`),
  ADD KEY `name_suffix` (`name_suffix`),
  ADD KEY `address_id` (`address_id`);

--
-- Indexes for table `political_donation_contributor_address`
--
ALTER TABLE `political_donation_contributor_address`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `slug` (`slug`),
  ADD KEY `city` (`city`,`state`),
  ADD KEY `zipcode` (`zipcode`),
  ADD KEY `addr1` (`addr1`);

--
-- Indexes for table `political_donation_contributor_type`
--
ALTER TABLE `political_donation_contributor_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `type_name` (`type_name`),
  ADD KEY `type_slug` (`type_slug`);

--
-- Indexes for table `political_donation_employer_name`
--
ALTER TABLE `political_donation_employer_name`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `employer_name` (`employer_name`),
  ADD KEY `employer_slug` (`employer_slug`);

--
-- Indexes for table `political_donation_employer_occupation`
--
ALTER TABLE `political_donation_employer_occupation`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `occupation_name` (`occupation_name`),
  ADD KEY `occupation_slug` (`occupation_slug`);

--
-- Indexes for table `political_donation_filing_period`
--
ALTER TABLE `political_donation_filing_period`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `period_name` (`period_name`),
  ADD KEY `period_slug` (`period_slug`);

--
-- Indexes for table `raw_donations`
--
ALTER TABLE `raw_donations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `Year` (`Year`),
  ADD KEY `Year_2` (`Year`),
  ADD KEY `Cycle` (`Cycle`),
  ADD KEY `DocType` (`DocType`),
  ADD KEY `FilerName` (`FilerName`),
  ADD KEY `EntityCity` (`EntityCity`),
  ADD KEY `EmployerName` (`EmployerName`),
  ADD KEY `Amended` (`Amended`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `political_donation`
--
ALTER TABLE `political_donation`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=368210;
--
-- AUTO_INCREMENT for table `political_donation_committee`
--
ALTER TABLE `political_donation_committee`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1090;
--
-- AUTO_INCREMENT for table `political_donation_contribution_type`
--
ALTER TABLE `political_donation_contribution_type`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;
--
-- AUTO_INCREMENT for table `political_donation_contributor`
--
ALTER TABLE `political_donation_contributor`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=78158;
--
-- AUTO_INCREMENT for table `political_donation_contributor_address`
--
ALTER TABLE `political_donation_contributor_address`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=52209;
--
-- AUTO_INCREMENT for table `political_donation_contributor_type`
--
ALTER TABLE `political_donation_contributor_type`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;
--
-- AUTO_INCREMENT for table `political_donation_employer_name`
--
ALTER TABLE `political_donation_employer_name`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7225;
--
-- AUTO_INCREMENT for table `political_donation_employer_occupation`
--
ALTER TABLE `political_donation_employer_occupation`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4846;
--
-- AUTO_INCREMENT for table `political_donation_filing_period`
--
ALTER TABLE `political_donation_filing_period`
  MODIFY `id` int(4) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=103;
--
-- AUTO_INCREMENT for table `raw_donations`
--
ALTER TABLE `raw_donations`
  MODIFY `id` mediumint(8) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=113039;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
