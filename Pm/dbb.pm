package dbb;

BEGIN {
}

use Exporter;
use SelfLoader;
use DBI;  
use Data::Dumper;

@ISA    = qw( Exporter SelfLoader);
@EXPORT = qw(
    dbb_connect 
    dbb_disconnect 
    dbb_getdb 
    dbb_setdb 
	dbb_setdb_over_file 
    );

DBI->install_driver("mysql");

sub dbb_connect {
    $::dbberr = undef;
    my	$DBH;
    my  $cfg = shift;
	my  $db	  = $cfg->{db}    ? 'database='.$cfg->{db} : undef;
	my	$host = $cfg->{host}  ? 'host='.$cfg->{host}   : undef;
	my	$login= $cfg->{login} ? $cfg->{login} : undef;
	my	$pass = $cfg->{pass}  ? $cfg->{pass}  : undef;

    eval {
        local $SIG{ALRM} = sub { print "timeout occurred\n" }; # сократить timeout на connect 
        my $TO  = alarm;
        alarm 3; 
        $DBH = DBI->connect('DBI:mysql:'.$db.';'.$host, $login,$pass); 
        alarm $TO;
    };

    if ($@ && $@=~/timeout/) {    # timeout коннекта
        $::dbberr = "DB-Connect Timeout";
        print $::dbberr,"\n";
        return
    }
    if ($DBI::err) {    # ошибка коннекта 
        $::dbberr = "$DBI::err = $DBI::errstr = state:$DBI::state";
        print $::dbberr,"\n";
		return
    }
$DBH
}




sub dbb_disconnect {
	$_[0]->disconnect()
}



sub dbb_getdb {
    $::dbberr = undef;
    my ($DBH,$sql,$exec) = @_;
    my (@out,@exec);
    
	@exec = @$exec if $exec && ref $exec eq 'ARRAY';
    
    my  $sth=$DBH->prepare($sql); 
        $sth->execute(@exec);    # ?,?,?

    if ($DBI::err) {
        $::dbberr = "$DBI::err = $DBI::errstr = state:$DBI::state";
        print $::dbberr,"\n";
        return
    }
    while ( my $ref = $sth->fetchrow_hashref ) { 
    	push @out, \%{$ref} # убрать ссылку на ref 
	}
    $sth->finish;

return @out if wantarray;	# возвращаем Array  
\@out						# возвращаем ссылку 
}


sub dbb_setdb {
    $::dbberr = undef;
	my ($DBH,$sql,$exec) = @_;
	my ($rv);

    if ($exec && ref $exec eq 'ARRAY') {
    my  $sth = $DBH->prepare($sql);
	my	$rv  = $sth->execute(@$exec);
		$rv  = 0 if $rv eq '0E0'; 	# кол-во измененных 
		$::dbberr =$DBH->errstr;
    }
    else {        
		$rv = $DBH->do($sql);   
        $rv = 0 if $rv eq '0E0'; 
        $::dbberr= $DBH->errstr;
    }
	$rv = undef if $DBH->errstr;
$rv
}

sub dbb_setdb_over_file {	# для LOAD DATA LOCAL нужен полный путь 
	my 	$DBH  = shift;
	my	$tab  = shift;  # table name
	my	$keys = shift;  # столбцы
	my	$data = shift;  # данные
	
	my	$pwd = `pwd`; $pwd =~ s/[\r\n]+$//;
	my	$file = $pwd.'/log/'.$$.'_'.int(rand(100)).'.tmp';			
	open  OF, "> $file";
	print OF join("\t",@$_)."\n" for @$data; # генерим файл с данными сразделиелем \t
	close OF;
	
	my	$sql = "LOAD DATA LOCAL INFILE '$file' INTO TABLE $tab (`".join('`,`',@$keys)."`)"; #print "sql: $sql\n";
	my	$rv = $DBH->do($sql);
        $::dbberr= $DBH->errstr;
	unlink $file;
	
$rv
}












#~ $sql = $dbh->quote($string)
my %q2qq = ('"' => "'", "'" => '"' );
sub dbb_cropSQL { 				# срезать попытки инжекторов в тексте '...'
        my $str = $_[0];
        my $q   = $_[1] || "'"; # внешние кавычки 		
        my $sm  = $_[2] || 1;	# срезать все правее ';'

        $q = $q2qq[$q];
        $str =~ s/[$q ](UNION|GROUP|OR|SELECT|DELETE|DROP|TRUNCATE|--)[$q ].*$//i;
        $str =~ s/;.*$// if $sm;    # ;... => ''

return  $str if defined wantarray;	# возвращаем $str 
$_[0] = $str;						# или заменяем первый аргумент 
}











1;

