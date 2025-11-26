# Christoph Lechner, 2025-11-20
# Code taken from simple_import.py and reworked to class

# Copy from git commit id c069fc5

# not needed because DB connection to be provided by AirFlow 3.1.3
# import psycopg

import json
# import argparse
import gzip
import datetime


class WikiLoader:
    data_table = 'wiki_change_events';
    stg_table_prefix = 'stg_tmp';
    do_debug = False

    def __init__(self):
        # make sure that names of temporary tables are pretty unique
        tnow = datetime.datetime.now()
        self.stg_table_prefix = self.stg_table_prefix+'_'+tnow.strftime('%Y%m%dT%H%M%S_%f')
        self.stg_table_load   = self.stg_table_prefix+'_1';
        self.stg_table_step2  = self.stg_table_prefix+'_2';
        self.stg_table_step3  = self.stg_table_prefix+'_3';

        # CREATE TEMPORARY TABLE -> table is automatically dropped at end of transaction
        # For debugging we don't want that...
        if self.do_debug:
            self.flag_temp = ''
        else:
            self.flag_temp = 'TEMPORARY'

    def data_load(self,cur,fn_in,do_gzip=False):
        # helper function so we can use "with ... as fin" for both modes
        def open_infile():
            print(f'Input file: {fn_in}')
            if do_gzip:
                return gzip.open(fn_in,'r')
            else:
                return open(fn_in,'rb')

        cur.execute(
        f"""
        CREATE {self.flag_temp} TABLE {self.stg_table_load}(
            event_meta_dt TEXT,
            event_meta_id TEXT,
            event_meta_domain TEXT,
            event_id BIGINT,
            event_type TEXT,
            event_wiki TEXT,
            event_user TEXT,
            event_bot BOOLEAN,
            event_title TEXT
        );
        """
        )

        linecntr=0
        with open_infile() as fin:
            for l_ in fin:
                l_ = l_.decode() # we use file in 'rb' mode now so we can switch transparently between gzip'd and standard files
                linecntr += 1
                if (linecntr%100000)==0:
                    print('.', end='', flush=True)
                #
                try:
                    event = json.loads(l_)
                except ValueError:
                    continue

                #print(event)
                if (not 'meta' in event):
                    print('skipping event: not all fields present')
                    continue

                # Extract information from event
                # See schema in directory schema/
                # Sometimes, not all fields are present
                # Missing elements in decoded JSON string are replaced by None,
                # resulting in NULL in DB
                def my_helper(dict,key):
                    if not key in dict:
                        # print(f'N for {key}')
                        return None
                    return dict[key]
                event_meta_dt     = my_helper(event['meta'],'dt')
                event_meta_id     = my_helper(event['meta'],'id')
                event_meta_domain = my_helper(event['meta'],'domain')
                event_id = my_helper(event,'id')
                event_wiki = my_helper(event,'wiki')
                event_title = my_helper(event,'title')
                event_user = my_helper(event,'user')
                event_bot = my_helper(event,'bot')
                event_type = my_helper(event,'type')

                # todo: check format string for int value (8-byte int in DB)
                cur.execute('INSERT INTO '+self.stg_table_load+' (event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (event_meta_dt, event_meta_id, event_meta_domain, event_id, event_type, event_wiki, event_user, event_bot, event_title))
                # break

        print('') # newline
        print(f'Loaded {linecntr} events')
        return linecntr

    # step 2
    def data_addhashes(self,cur):
        print('adding hashes to rows ...')
        cur.execute(
        f"""
        CREATE {self.flag_temp} TABLE {self.stg_table_step2} AS
        SELECT
            MD5(CONCAT(CONCAT(event_meta_id,'_'),'-',CONCAT(event_meta_dt,'_'),'-',CONCAT(CAST(event_id AS TEXT),'_'),'-',CONCAT(event_user,'_'))) AS _h,
            TO_TIMESTAMP(event_meta_dt, 'YYYY-MM-DD T HH24:MI:SS.FF3 TZ') AS ts_event_meta_dt,
            event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title
        FROM {self.stg_table_load};
        """
        )
        return cur.rowcount # no deduplication here, so it should correspond to number of loaded rows

    # step 3
    def data_dedupl(self,cur):
        print('deduplicate staged rows bashed on hashes (sometimes the same event is sent multiple times) + drop canary events ...')
        cur.execute(
        f"""
        -- de-duplicate based on MD5 hash
        CREATE {self.flag_temp} TABLE {self.stg_table_step3} AS
        WITH q AS (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY _h) AS _rn FROM {self.stg_table_step2}
        )
        SELECT
            _h,ts_event_meta_dt,event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title
        FROM q WHERE
            _rn=1
            -- discard 'canary' events (see https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service)
            AND event_meta_domain<>'canary';
        """
        )
        return cur.rowcount

    # step 4 (merge)
    def data_merge(self,cur):
        # finally MERGE only rows with unseen hash values
        # -> loading the same data twice does not harm as nothing gets inserted
        print('execute MERGE command (only events with new MD5 hash get stored)')
        cur.execute(
        f"""
        MERGE
        INTO
            {self.data_table} AS dst
        USING
            {self.stg_table_step3} AS src
        ON
            dst._h=src._h
        WHEN MATCHED THEN DO NOTHING
        WHEN NOT MATCHED THEN INSERT VALUES (_h,ts_event_meta_dt,event_meta_dt,event_meta_id,event_meta_domain,event_id,event_type,event_wiki,event_user,event_bot,event_title);
        """
        )
        return cur.rowcount



