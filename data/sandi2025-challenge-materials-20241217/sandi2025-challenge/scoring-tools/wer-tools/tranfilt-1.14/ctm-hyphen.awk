function matchhyphen(hypword) {
    words=""
    n=index(hypword,"-");
    while ((n > 0) && (n < length(hypword))) {
        ew=substr(hypword,(n-1),1);
        sw=substr(hypword,(n+1),1);
        if (match(ew,/[[:alpha:]]/) && match(sw,/[[:alpha:]]/)) {
            # don't include hyphen
            tmp = substr(hypword,1,(n-1));            
            stg = sprintf("%s ",tmp);
	} else {
            # include hyphen
            stg = substr(hypword,1,n);
	}
        tmp = words;
        words = sprintf("%s%s", tmp, stg);
        stg = substr(hypword,(n+1));
        hypword = stg;
        n = index(hypword,"-");
    }
    tmp=words;
    words = sprintf("%s%s",tmp, hypword);
    return words;
}

{   
    n = index($5,"-");
    if ((n > 0) && (n < length($5))) {
        b = matchhyphen($5);
        m = split(b,w," ");
        if (m==1) {
            print $0;
	} else {
            st = $3;
            dur = $4;
            et = st + dur;
            durstep = dur/m;
            sst = st;
            for (j=1;j<m;j++) {
   		printf "%s %s %.2f %.2f %s", $1,$2,sst,durstep,w[j];
                if (NF==6) printf " %s", $6;
		printf "\n";
		sst += durstep;
	    }
            durstep = et - sst;
   	    printf "%s %s %.2f %.2f %s", $1,$2,sst,durstep,w[m];
            if (NF==6) printf " %s", $6;
	    printf "\n";
	}
    } else {
        print $0;
    }
}
