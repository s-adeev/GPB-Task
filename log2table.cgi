#! /usr/bin/perl -w

use Data::Dumper; $Data::Dumper::Sortkeys = 1;
use CGI qw(:standard);
use Pm::cfg;	cfg->import;
use Pm::dbb;	dbb->import;

$| = 1;
our	$dbberr;

my 	%w; $w{$_} = param $_ for param;	# global %w <= GET,PUT parametrs

print "Content-type: text/html\n\n";
print <DATA>;

my	$cfg = getCfg();
my	$dbh = dbb_connect( $cfg->{'mysql'} );
my	$page = $cfg->{'mysql'}->{page_lines} || 100; # max размер страницы

print $dbberr and exit if !$dbh || $dbberr;
	
	$w{addr} =~ s/[^\w@.*-]//g; 	# срезать не адресные символы 
my	$find = $w{addr} =~ s/\*/%/gr;	# возможность поиска не полного адреса 
my	$message = dbb_getdb($dbh,"SELECT * FROM message WHERE str     LIKE ? ORDER BY int_id DESC, created DESC LIMIT 101",['<= '.$find]);
my	$log 	 = dbb_getdb($dbh,"SELECT * FROM log     WHERE address LIKE ? ORDER BY int_id DESC, created DESC LIMIT 101",[$find]);
# берем LIMIT 101 чтоб определить что их больше 100 хотябы в одной таблице

# вторичная сортировка после объединения данных
my	@log =  
	sort { $b->{int_id}  cmp $a->{int_id} || 
		   $b->{created} cmp $a->{created} } # date - string 
	(@$message, @$log);
my	$find_lines = @log;				# запомнить сколько было 
	$#log = $page-1 if @log > $page;# усекаем до 100
	

my	$plh = 'Find e-mail@address';
print "
<form action=log2table.cgi method=POST >
<input type=text id=addr name=addr placeholder='$plh' size=40 value='".$w{addr}."'>
<input type=submit name=Send value=Find><br><br>
<table border=0 class=tabin>
";
#my	@col = qw(created int_id str);
my	@col = qw(created str);	# колнки 
	print "<tr>\n";
	print "<th>$_</th>\n" for @col;
	print "</tr>\n";

for my $l (@log) {
	print "<tr>\n";
	print "<td>$l->{$_}</td>\n" for @col;
	print "</tr>\n";
}
print "</table>\n";
print "<script>dbout('Find $find_lines lines',10)</script>\n" if $find_lines <=  100 && $w{addr};
print "<script>dbout('Find more then 100 lines',15,'infowarning')</script>\n" if $find_lines > 100;
	
	
	
	
__DATA__ 	
<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.0 Transitional//EN'>
<HTML><HEAD>
<meta http-equiv='Content-type' content='text/html;'>
<script type='text/javascript' charset='utf8' src='js/jquery-1.12.0.min.js'></script>
<TITLE>Mail log</TITLE>
<STYLE>
td,A,pre {text-decoration:none; FONT-SIZE:14px; line-height:14px;}

.tabin 	  { 
	background: #ffffff; 
	font-family: helvetica,arial;
	font-size:	12px;
}
.tabin th 		{
	background:	#b4d1e5;
	border-right: 1px solid #aaa;
	border-bottom: 1px solid #aaa;
}
.tabin tr:hover { 	
	background: #e4eef5  !important;
}
.tabin tr:nth-child(even) { 
	background: #f5f5f5; 
}
.tabin tr td {   
	border-right: 1px solid #aaa;
	border-bottom: 1px solid #aaa;
	padding: 0px 5px;
	white-space:pre;
}


#info{
	background: #ddd;
	min-width:100px;
	max-width:600px;
	position: absolute;
    top: 0;
    right: 0;
	z-index: 2000;
}
#info > div{
	position: fixed;
	top: 20px;
    right: 20px;
}
#info > div > div{
    padding: 4px 10px;
	background: #ddf1ff;
    margin-bottom: 6px;
    border: 1px solid #a9a9a9;
    box-shadow: 4px 4px 20px -6px #000;
	display:none;
}
#info > div > div.infoalert{
	background: #ff6969;
}
#info > div > div.infowarning{
	background: #ec9c18;
}

</STYLE>
<script>
function dbout (txt,tmr,c) { 
	c = (typeof c === "undefined" ) ? 'info' : c	
let div = $('<div/>',{'class' : c, 'click': function(){ $(this).remove() }} ).html(txt);
	div.appendTo('#info > div').fadeIn('slow').delay(tmr * 1000).fadeOut('slow', function() { div.remove() });
}
</script>
</HEAD>
<BODY bgColor=#ffffff >
<div id=info><div></div></div>

