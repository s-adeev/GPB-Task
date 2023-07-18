package cfg;

BEGIN {	push @main::INC, '..' }

use Exporter;
use SelfLoader;

@ISA    = qw( Exporter SelfLoader);
@EXPORT = qw(
    getCfg
    );

sub getCfg {
	my (%cfg,$blok);
	my $file = shift || '.cfg';
	my @cfg = `cat $file`;
	
	for (@cfg) {
		s/#.*$//; 		# comments
		s/\s+/ /g; 		# \r\n\t\v
		s/(^ | $)//g; 	# trim spaces
		$blok = $1 if /^\[(\S+)\]/;
		$cfg{$blok}->{$+{'key'}} = $+{'val'} if /^(?'key'\S+) ?= ?(?'val'\S+)/;
	}

\%cfg
}

1
