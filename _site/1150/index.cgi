#!/usr/bin/perl -w

# Description: Parses date entries and builds an HTML calendar

# Values are stored in two columns:
# 1) Lecture Date
# 2) Date entry
# Hyperlinks are stored in the input file as "(LINK|LAB|HWK|VIDEO): TITLE <URL>"

#use CGI qw/:standard/;
use strict;
use CGI::Carp 'fatalsToBrowser';
use diagnostics;

use DateTime;
use DateTime::Duration;

my $FALSE = 0;
my $TRUE = 1;

my $DEBUG = 1;

my $SHOW_AT_MOST_2_WEEKS = $TRUE;
#$SHOW_AT_MOST_2_WEEKS = $FALSE;

my @MONTHS = qw(January February March April May June July August September October November December);

my $DATETIME_MONDAY = 1;
my $DATETIME_FRIDAY = 5;
#my $DATETIME_SATURDAY = 6;
#my $DATETIME_SUNDAY = 7;

my $DAYS_IN_A_WEEK = 7;

my $DATE_INDEX = 0;
my $ENTRY_INDEX = $DATE_INDEX + 1;

my $OUTPUT_NEWLINE = '<br/>';

my $CALENDAR_HEADER = "<table border = 1 width='100%'>"; # style='float: left; text-align: left'>";
my $CALENDAR_FOOTER = "</table>\n";

# my $DAYS_OF_WEEK_ROW = '
#   <tr>
#     <th>Sunday</th>
#     <th>Monday</th>
#     <th>Tuesday</th>
#     <th>Wednesday</th>
#     <th>Thursday</th>
#     <th>Friday</th>
#     <th>Saturday</th>
#   </tr>
# ';
my $DAYS_OF_WEEK_ROW = '
  <tr>
    <th style="width:30%"><font size="+1">Monday</font></th>
    <th style="width:5%"><font size="+1">T</font></th>
    <th style="width:30%"><font size="+1">Wednesday</font></th>
    <th style="width:5%"><font size="+1">R</font></th>
    <th style="width:30%"><font size="+1">Friday</font></th>
  </tr>
';

my $ROW_START  = "  <tr valign='top'>\n";
my $ROW_END    = "  </tr>\n";
my $DAY_START  = '    <td>';
my $DAY_END    = "    </td>\n";


sub DEBUG{
    if( $DEBUG){
	print STDERR "DEBUG: @_\n";
    }
}

# Converts from month string to month number (e.g., Feb -> 2)
sub parseMonth{
    my ($monthStr) = @_;
    for( my $monthIndex = 0; $monthIndex <= $#MONTHS; $monthIndex++){
	my $appreviatedMonth = substr($MONTHS[$monthIndex],0,3);
	if( $monthStr =~ m/$appreviatedMonth/i){
	    return $monthIndex + 1;
	}
    }
    die( "parseMonth( $monthStr)");
}

sub fileToString{
    my $file_ = $_[0];
    
    my $msg = "Input file '" . $file_ . "' failed to open.\n" . "Died";

    my $terminator = $/;
    undef $/;
    open INPUT, "<$file_" or die $msg;
    my $str = <INPUT>; # terminator undefined : $str is the whole file.
    close INPUT;

    $/ = $terminator; # Restore for normal behavior later

    return $str;
}
    
sub MIN{
    return $_[0] <= $_[1] ? $_[0] : $_[1];
}
    
sub MAX{
    return $_[0] >= $_[1] ? $_[0] : $_[1];
}


sub monthStart{
    my $monthIndex = $_[0];
    my $monthStr = $MONTHS[ $monthIndex];
    my $currentIdStr = "";
    if( $monthIndex == DateTime->now->month - 1){
	# working on the current month
	$currentIdStr = " id=\"thisMonth\" ";
    }
    my $str;
    #$str .= $ROW_START;
    #$str .= "    <td colspan=$DAYS_IN_A_WEEK align=\"center\" id=\"$_[0]\">";
    #$str .= "<br/><b><font size='+2'>".$_[0]."</font></b><br/><br/>";
    $str.= "<center$currentIdStr>";
    $str .= "<br/><b><font size='+2' id=\"$monthStr\">$monthStr</font></b><br/>";
    $str.= "</center>\n";
    #$str .= $DAY_END;
    #$str .= $ROW_END;
    $str .= $CALENDAR_HEADER;
    $str .= $DAYS_OF_WEEK_ROW;
    #$str .= $ROW_START;  # handeled at the beginning of each week
    
    return $str;
}

sub formatDate{
    my $str = "";
    my ($day, $description) = @_;
    $str .= "<b>\n";
    if( defined( $description)){
	$str .= "<div class='dateDescription'>$description</div>\n";
	$str .= "<div class='date'>$day&nbsp;</div>\n";
    }else{
	$str .= "<div class='dayHeader'>$day&nbsp;</div>\n";

    }
    $str .= "</b>\n";
    #$str .= "<hr class='thin'/>\n";

    return $str;
}


sub makeCalendarTables{
    my $inputFile = $_[0];
    my $html = '';  # output
    
    # For each input line,
    #   Parse each column and store the entry in the appropriate cell in an array
    #   Use the date column to calculate the index in the array as the difference between that value and the first value found
    # 
    # To produce the output (HTML):
    # For each cell in the array:
    #   Get the month and day of the week for the date
    #   If date is in a different month than the previous date, close off the previous table (if not the first entry) and make a new table for this month
    #   If the date is a Monday, close out the previous row (if necessary) and start a new row
    #   Print the date and then the text (reformating any hyperlinks)

    my $inputFileContents = fileToString( $inputFile);

    # dos2unix
    $inputFileContents =~ s/\n?/\n/g;

    # postpone until later so that an a hwk tag without a link doesn't match past another tag
    ## re-format hyperlinks
    #$inputFileContents =~ s/((LINK|LAB|HWK|VIDEO):[^<]+?)\s*<([^>]*)>/<a href="$3">$1<\/a>/ig;
    #$inputFileContents =~ s/>LINK:?\s*/>/g; # remove "LINK"
    #DEBUG("inputFileContents: $inputFileContents");
    
    # replace
    #   "...\n..." with
    #   ...<br/>...
    my @quotedSections = split(/"/, $inputFileContents);
    # check for unpaired "s
    if( $#quotedSections % 2 == 1){
    	die( "ERROR: Found an odd number of \"s ($#quotedSections)!");
    }
    for( my $quoteI = 1; $quoteI <= $#quotedSections; $quoteI += 2){
    	$quotedSections[$quoteI] =~ s/;? *\n/$OUTPUT_NEWLINE/g; 
    }
    #DEBUG( "quotedSections: @quotedSections");
    $inputFileContents = join( '', @quotedSections);
    
    # remove header rows
    #DEBUG( "length(\$inputFileContents): ".length($inputFileContents));
    #$inputFileContents =~ s/^\#[^\n]+\n$//sg;
    $inputFileContents =~ s/^\#[^\n]*\n?//g;  # "?" For the last line
    #DEBUG( "length(\$inputFileContents): ".length($inputFileContents));

    my @inputLines = split(/\n/, $inputFileContents);
    DEBUG( "Found ".($#inputLines  + 1)." lines in $inputFile\n");

    my $firstDateObj;  # force it to start on a Monday
    my $lastIndexToDisplay = 9999;  # only used if SHOW_AT_MOST_2_WEEKS is set

    my @calendarItems;  # indices are dates, starting at the firstDateObj
    my @dateTimes;      # Array of DateTime objects
    my @dateDescriptions; # Array of data descriptions

    for( my $lineI = 0; $lineI <= $#inputLines; $lineI++){
	my @cells = split( /\t/, $inputLines[$lineI]);
	if( $#cells < $ENTRY_INDEX){
	    print STDERR "ALERT: Only found ".($#cells+1)." (instead of at least ".($ENTRY_INDEX+1).") on line index $lineI ($inputLines[$lineI])!  Skipping this line.";
	    next;
	}
	my $day;
	my $month;
	my $year;
	if( $cells[$DATE_INDEX] =~ m/(\d{1,2})\-(\w{3})/){
	    $day = $1;
	    $month = parseMonth( $2);
	    $year = DateTime->now->year;
	}elsif( $cells[$DATE_INDEX] =~ m/(\d{2,4})(\d{2})(\d{2})/){
	    # YYYYMMDD or YYMMDD format
	    $year = $1;
	    $month = $2;
	    $day = $3;
	}else{
	    die("Malformed date on line index $lineI: $cells[$DATE_INDEX] (line: $inputLines[$lineI])");
	}

	my $dateDescription;  # for example Classroom, Lab
	if( $cells[$DATE_INDEX] =~ m/;\s*(.+)/){
	    $dateDescription = $1;
	}
	
	my $dt = DateTime->new(
	    year       => $year,
	    month      => $month,
	    day        => $day
	    );
	
	if( $lineI == 0){
	    # first line
	    $firstDateObj = DateTime->new(
		year       => DateTime->now->year,
		month      => $month,
		day        => $day
		);
	    # make it firstDateObj be a Monday
	    my $dur = DateTime::Duration->new(
		days => ($firstDateObj->day_of_week - 1)
		);
	    $firstDateObj->subtract_duration( $dur);
	    DEBUG( "\$firstDateObj->datetime(): ".$firstDateObj->datetime());
	    
	    if( $SHOW_AT_MOST_2_WEEKS ){
		if( DateTime->now < $firstDateObj){
		    DEBUG("DateTime->now < \$firstDateObj");
		    $lastIndexToDisplay = $DAYS_IN_A_WEEK + ($DATETIME_FRIDAY - $DATETIME_MONDAY);
		}else{
		    $lastIndexToDisplay = DateTime->now->delta_days( $firstDateObj )->delta_days() + ($DAYS_IN_A_WEEK * 2);
		    DEBUG("lastIndexToDisplay (next 2 weeks): $lastIndexToDisplay");
		}
		DEBUG("lastIndexToDisplay: $lastIndexToDisplay");
		$lastIndexToDisplay += (4 + $DAYS_IN_A_WEEK - $lastIndexToDisplay) % $DAYS_IN_A_WEEK; # to make sure it ends on a Friday
		DEBUG("lastIndexToDisplay: $lastIndexToDisplay");
	    }
	}
	#DEBUG( "\$dt->datetime(): ".$dt->datetime());
	my $dur = $dt->delta_days( $firstDateObj);
	my $dateIndex = $dur->delta_days();    
	DEBUG( "dateIndex: $dateIndex");

	if( $dateIndex > $lastIndexToDisplay){
	    DEBUG("dateIndex > lastIndexToDisplay ($dateIndex > $lastIndexToDisplay)");
	    next;
	}

	$dateTimes[$dateIndex] = $dt;
	if( defined( $dateDescription)){
	    $dateDescriptions[$dateIndex] = $dateDescription;
	}
	
	if( $cells[$ENTRY_INDEX] !~ m/^\s*$/){
	    $calendarItems[$dateIndex] .= $cells[$ENTRY_INDEX] . "$OUTPUT_NEWLINE";
	}
    }

    $#dateTimes += $DAYS_IN_A_WEEK - 1 - ($#dateTimes % 7);


    if( $DEBUG){
	DEBUG("\@calendarItems:");
	for( my $i = 0; $i <= $#calendarItems; $i++){
	    if( defined( $calendarItems[$i])){
		DEBUG( "\t$i: $calendarItems[$i]");
	    }else{
		DEBUG( "\t$i");
	    }
	}
    }


    # To produce the output (HTML):#
    # For each cell in the array:
    #   Get the month and day of the week for the date
    #   If date is in a different month than the previous date, close off the previous table (if not the first entry) and make a new table for this month
    #   If the date is a Monday, close out the previous row (if necessary) and start a new row
    #   Print the date and then the text (reformating any hyperlinks)
    my $prevMonth = 0;
    for( my $dateI = 0; $dateI <= $#dateTimes; $dateI++){
	if( ! defined( $dateTimes[$dateI])){
	    # fill-in unused dates
	    my $dur = DateTime::Duration->new(
		days => $dateI
		);
	    $dateTimes[$dateI] = $firstDateObj + $dur;
	    DEBUG("Filling-in unused date for index $dateI: $dateTimes[$dateI]");
	}
	if( $dateTimes[$dateI]->month != $prevMonth){
	    if( $dateI != 0){
		$html .= $CALENDAR_FOOTER;
	    }

	    #my $monthStr = $MONTHS[$dateTimes[$dateI]->month - 1];
	    my $monthIndex = $dateTimes[$dateI]->month - 1;
	    # $html .= "<a name=\"$monthStr\"></a>\n"; # not supported in HTML 5, use id attribute instead
	    $html .= monthStart( $monthIndex);

	    # calculate the number of days from the beginning of the month to Monday
	    my $blankDaysAtBeginningOfMonth = $dateTimes[$dateI]->day_of_week - 1;
	    if( $blankDaysAtBeginningOfMonth > 0){
		# add in blank days
		$html .= "    <td colspan=$blankDaysAtBeginningOfMonth></td>\n";
	    }

	    $prevMonth = $dateTimes[$dateI]->month;
	}
	if( $dateTimes[$dateI]->day_of_week == $DATETIME_MONDAY){
	    # Monday marks the start of a new week
	    $html .= $ROW_START;
	}
	
	$html .= $DAY_START;
	#$html .= $dateTimes[$dateI] . "<br/>\n<hr/>\n";
	$html .= formatDate($dateTimes[$dateI]->day, $dateDescriptions[$dateI]);
	if( defined( $calendarItems[$dateI])){
	    # re-format hyperlinks (each on it's own line to limit a tagged label without a link matching a later tagged label with a label)
	    my @dateLines = split(/<br/, $calendarItems[$dateI]);
	    for( my $dateLineI = 0; $dateLineI <= $#dateLines; $dateLineI++){
		$dateLines[ $dateLineI] =~ s/((LINK|LAB|HWK|VIDEO)[^<]+?)\s*<([^>]*)>/<a href="$3">$1<\/a>/ig;
		$dateLines[ $dateLineI] =~ s/>LINK:?\s*/>/g; # remove "LINK"
		#DEBUG("inputFileContents: $inputFileContents");
	    }
	    $html .= join( '<br', @dateLines);
	}
	$html .= $DAY_END;

	if( $dateTimes[$dateI]->day_of_week == $DATETIME_FRIDAY){
	    # Friday marks the end of the week
	    $html .= $ROW_END;

	    # assert that Saturday and Sunday have empty entries
	    if( ($dateI + 1 < $#calendarItems && defined( $calendarItems[$dateI + 1])) ||
		($dateI + 2 < $#calendarItems && defined( $calendarItems[$dateI + 2]))){
		die("ERROR: Non-empty Saturday ($calendarItems[$dateI+1]) or Sunday ($calendarItems[$dateI+2])!");
	    }
	    $dateI += 2;
	}    
    }

    # Test that the last day is a Friday
    if( $#dateTimes % 7 != $DATETIME_FRIDAY ){
	DEBUG( "NOTE: The last day to display was ".($#dateTimes % 7)." instead of a Friday ($DATETIME_FRIDAY)\n");
	$html .= $ROW_END;
    }
    
    $html .= $CALENDAR_FOOTER;

    return $html;
} # END makeCalendarTables()    


# look for any command-line arguments
my $arg;
for( my $argvIndex = 0; $argvIndex <= $#ARGV; $argvIndex++){
    if( $ARGV[ $argvIndex] =~ m/^-(.+)/){
	$arg = lc($1);
	
	if( $arg =~ m/^(f|-full)/i){
	    $SHOW_AT_MOST_2_WEEKS = $FALSE;
	}elsif( $arg =~ m/^(s|-short)/i){
	    $SHOW_AT_MOST_2_WEEKS = $TRUE;
	}else{
	    die("Unknown arg: $arg\n");
	}
    }else{
	die("Mal-formed command-line arg: $arg\n");
    }
}

#if( $0 !~ m/(00\d)/){
#    end_in_error("ERROR: Unable to parse section number from script name \"$0\"!");
#}
#my $section = "$1";

print "Content-type: text/html\n\n";

my $html = fileToString("calendar-shell.html");

my $dynamicCalendar = makeCalendarTables( "calendar.tab");

# replace CALENDAR GOES HERE comment with dynamic calendar
$html =~ s/\<\!\-\-\s*CALENDAR GOES HERE\s*\-\-\>/$dynamicCalendar/s;

print $html;

exit( 0);
