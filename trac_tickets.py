#!/usr/bin/python

import sys
import munin

class TracTickets(munin.Plugin):
    
    # Queries to perform. Syntax is (label, info, query)
    queries = [
        ('unreviewed', 'Unreviewed', 'status=new|assigned|reopened&stage=Unreviewed'),
        ('design', 'Design decision needed', 'status=new|assigned|reopened&stage=Design decision needed'),
        ('accepted', 'Accepted', 'status=new|assigned|reopened&stage=Accepted'),
        ('ready', 'Ready for checkin', 'status=new|assigned|reopened&stage=Ready for checkin'),
    ]
    
    def fetch(self):
        from trac.ticket.query import Query
        
        env = self._connect()
        cursor = env.get_db_cnx().cursor()
        
        for label, info, query in self.queries:
            q = Query.from_string(env, query)
            cursor.execute(*q.get_sql())
            yield ("%s.value" % label, len(list(cursor)))
    
    def config(self):
        yield ('graph_title', 'Trac tickets')
        yield ('graph_args', '-l 0 --base 1000')
        yield ('graph_vlabel', 'Tickets')
        yield ('graph_scale', 'no')
        yield ('graph_category', 'Trac')
        yield ('graph_info', 'Shows current Trac ticket counts')
        for label, info, query in self.queries:
            yield ("%s.label" % label, label)
            yield ("%s.info" % info, info)
            yield ("%s.type" % type, "GAUGE")

    def _connect(self):
        # Both of the below won't work if PYTHONPATH and TRAC_ENV aren't
        # set in the munin-node plugin conf.
        import trac.env
        return trac.env.open_environment()
        
    def autoconf(self):
        try:
            self._connect()
        except:
            return False
        return True

if __name__ == '__main__':
    munin.run(TracTickets)
