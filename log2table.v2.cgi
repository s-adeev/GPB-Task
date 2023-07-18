#! /usr/bin/perl
#use warnings;	# => Name "Q::FILE_L" used only once: possible typo at ... 
use strict;

#~ use Data::Dumper; $Data::Dumper::Sortkeys = 1;
use CGI qw(:standard);
use Pm::cfg;	cfg->import;
use Pm::dbb;	dbb->import;

$| = 1;
our	$dbberr;
our	$query= new CGI;                                                                                                                   

my 	%w; $w{$_} = param $_ for param;	# global %w <= GET,PUT parametrs

load_file() and exit if $w{'FILE_L'} && !$w{'Send'}; # залить через web файл лога 


print "Content-type: text/html\n\n";
print <DATA>;

my 	$cfg = getCfg();
my 	$dbh = dbb_connect( $cfg->{'mysql'} );
my	$page = $cfg->{'mysql'}->{page_lines} || 100;  # max размер страницы

print $dbberr and exit if !$dbh || $dbberr;
	
	$w{addr} =~ s/[^\w@.*-]//g; 	# срезать не адресные символы 
my	$find = $w{addr} =~ s/\*/%/gr;	# возможность поиска не полного адреса   address* => LIKE 'address%'
my	@log  = dbb_getdb($dbh,"SELECT * FROM log_v2 WHERE address LIKE ? ORDER BY int_id DESC, created DESC LIMIT 101",[$find]);
# берем LIMIT 101 чтоб определить что их больше 100

# вторичная сортировка не нужна
#~ my	@log =  
#~ 	sort { $b->{int_id}  cmp $a->{int_id} || 
#~ 		   $b->{created} cmp $a->{created} } # date - string 
#~ 	@log;
my	$find_lines = @log;				# запомнить сколько было 
	$#log = $page-1 if @log > $page;# усекаем до 100
	

my	$plh = 'Find e-mail@address';
print "
<form ".		  "name=forma id=forma action=log2table.v2.cgi method=POST enctype='multipart/form-data'>
<div class=headcontainer>
<div id=div_find>
<input type=text   name=addr id=addr placeholder='$plh' size=40 value='".$w{addr}."'>
<input type=submit name=Send value=Find></div>
<div id=div_txt style='width:200px;padding:0px 0px 0px 20px'>Select FILEs or drag-and-drop file to button &#9654;
</div>	
<div id=div_file>
<INPUT type=file   name=FILE_L size=30 maxlength=30 multiple>
<input type=button name=btnSubmit id=btnSubmit value='Load File'></div>
</div><br>	
<table border=0 class=tabin>
";

my	@col = qw(created flag str);	# колонки таблицы 
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
	



sub load_file {
	print "Content-type: text/html\n\n// js\n/*\n";
	my	@files;
	my  $dir = './log';	# tmp папка 
	
	if (-d $dir && (!-w _ || !-x _)) {	# проверить права на запись файлов в директорию от имени apache 
		my  $dirmode = (stat($dir))[2]; 
		printf "*/\n alert('Can`t write to $dir:%04o');\n", $dirmode & 07777; 
		exit
	}
	
	$query->import_names(); 							# for MULTIPLE Files
	for my  $file (@Q::FILE_L) {						# <input file name	
		my  $tmpfile = $query->tmpFileName($file); 		# tmp file			
		my	$File = $dir ."/". $file=~s{^.*[/\\]}{}r; 	# destination file	
		if ($tmpfile) {
			
			open FTMP, $tmpfile; 
			my   $fh = *FTMP;
			if (!$fh && $query->cgi_error) { 
				print "ERROR UpLoad file:'$file'\n";
				print $query->header(-status=>$query->cgi_error);  
				close FTMP and next
			}
			
			my ($size,$mtime)=(stat($tmpfile))[7,9]; 
			print "UpLoad file:'$file' (size.$size)\n";
			
			open  OUTFILE, "> $File";	
			print OUTFILE while <FTMP>;	# cp to real file 
			close OUTFILE;
			push @files, $File;
		}
		print "*/\n alert('File $file not saved');\n" and exit if !-e $File || -z _; # проверим что файл все-таки записался 
	}
	for (@files) {
		my	$parcer = `./log2table.v2 $_`; # parce файл в базу 
		$parcer =~ s/'/"/sg;
		$parcer =~ s/[\r\n]+/<br>/sg;
		print "*/\n dbout('$parcer',15,'infoalert');\n" and exit if $parcer =~ /WARNING:/; # если ошибка с парсингом
	}
print "*/\n";
print "dbout('The file has been uploaded. <br>Please reload the page',20)\n"; # Ок перегрузите страницу поиска
}


	
__DATA__ 	
<!DOCTYPE HTML PUBLIC '-//W3C//DTD HTML 4.0 Transitional//EN'>
<HTML><HEAD>
<meta http-equiv='Content-type' content='text/html;'>
<script type='text/javascript' charset='utf8' src='js/jquery-1.12.0.min.js'></script>
<TITLE>Mail Log v2</TITLE>
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


input[type=file]::file-selector-button {
	border: 1px solid #555;
	padding: 5px 10px;
	border-radius: .2em;
	background-color: #efefef;
	transition: 1s;
	height: 50px;
}

input[type=file]::file-selector-button:hover {
	background-color: #fff;
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

.headcontainer {
  display: flex;
  flex-direction: row; 
  flex-wrap:wrap; 
}
.headcontainer > div {
	padding: 0px 20px 0px 0px;
}

</STYLE>
<script>
var myurl = 'log2table.v2.cgi';

function dbout (txt,tmr,c) { 
	c = (typeof c === "undefined" ) ? 'info' : c	
let div = $('<div/>',{'class' : c, 'click': function(){ $(this).remove() }} ).html(txt);
	div.appendTo('#info > div').fadeIn('slow').delay(tmr * 1000).fadeOut('slow', function() { div.remove() });
}

$(document).ready(
function () {
    $("#btnSubmit").click(function (event) {
        event.preventDefault();
		var	form = $('#forma')[0];
		var data = new FormData(form);  
        $("#btnSubmit").prop("disabled", true);

		$.ajax({
            type:        'POST',
            enctype:     'multipart/form-data',
            encoding:    'multipart/form-data',	// for IE11
            url:         myurl,
            data:        data,
            processData: false,
            contentType: false,
            cache:       false,
            timeout:     600000,
            success:     function (data) { eval(data) },
            error: 		 function (e)    { alert("ERROR : "+ e) },
        });
		$("#btnSubmit").prop("disabled", false);
    });
});

</script>
</HEAD>
<BODY bgColor=#ffffff >
<div id=info><div></div></div>

