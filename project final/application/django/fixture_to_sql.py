import sys, os, re,json

def insert(fpo, table, *args):
    statement = "INSERT INTO " + table + " VALUES("
    values = []
    for arg in args:
        if isinstance(arg, basestring):
            #if re.match(r'\d{4}-\d{2}-\d{2}', arg):
            #    arg = "datetime(\"" + arg + "\")"
            #else:
            arg = "\"" + arg + "\""
        elif isinstance(arg, bool):
            if arg: arg = 1
            else: arg = 0
        elif arg is None:
            arg = "NULL"
        values.append(str(arg))
        
    statement += ", ".join(values) + ");\n"
    fpo.write(statement);
    
def member(fixture, fpo):
    for item in fixture:
        if item['model'] == "sportsrec.member":
            insert(fpo, "sportsrec_member", \
                item['pk'], item['fields']['first_name'], item['fields']['last_name'], \
                item['fields']['email'], \
                item['fields']['address'], item['fields']['facebook'], item['fields']['twitter'], \
                item['fields']['phone'], item['fields']['interests'], item['fields']['owner'] \
            )
    
def club_type(fixture, fpo):
    for item in fixture:
        if item['model'] == "sportsrec.clubtype":
            insert(fpo, "sportsrec_clubtype", \
                item['pk'], item['fields']['name'], item['fields']['description'], 0 \
            )
                
def club_tag(fixture, fpo):
    for item in fixture:
        if item['model'] == "sportsrec.clubtag":
            insert(fpo, "sportsrec_clubtag", item['pk'], item['fields']['name'])
 
def club(fixture, fpo):
    for item in fixture:
        if item['model'] == "sportsrec.club":
            insert(fpo, "sportsrec_club", \
                item['pk'], item['fields']['name'], item['fields']['address'], \
                item['fields']['latitude'], item['fields']['longitude'], \
                item['fields']['type'], 0, \
                item['fields']['created'], item['fields']['recruiting'], \
                item['fields']['contact'], item['fields']['description'], \
                item['fields']['facebook'], item['fields']['twitter'], \
                item['fields']['owner'] \
            )

def club_tags(fixture, fpo):
    i = 1
    for item in fixture:
        if item['model'] == "sportsrec.club":
            for tag in item['fields']['tags']:
                insert(fpo, "sportsrec_club_tags", \
                    i, item['pk'], tag\
                )
                i += 1
            
def membership_application(fixture, fpo):
    for item in fixture:
        if item['model'] == "sportsrec.membershipapplication":
            insert(fpo, "sportsrec_membershipapplication", \
                item['pk'], item['fields']['applied'], item['fields']['member'], \
                item['fields']['club'], item['fields']['rejected'] \
            )

def membership(fixture, fpo):
    for item in fixture:
        if item['model'] == "sportsrec.membership":
            insert(fpo, "sportsrec_membership", \
                item['pk'], item['fields']['joined'], item['fields']['last_paid'], \
                item['fields']['member'], item['fields']['club'] \
            )            
       
def to_sql(fixture, fpo):
    member(fixture, fpo)
    club_type(fixture, fpo)
    club_tag(fixture, fpo)
    club(fixture, fpo)
    club_tags(fixture, fpo)
    membership_application(fixture, fpo)
    membership(fixture, fpo)

def strip_fixture(fixture, fpo):
    fixtures = {}
    for fix in fixture:
        l = fixtures.get(fix['model'], [])
        l.append(fix)
        fixtures[fix['model']] = l
        
    #Reset count so triggers can do their job
    for fix in fixtures['sportsrec.clubtype']:
        fix['club_count'] = 0
    
    for fix in fixtures['sportsrec.club']:
        fix['member_count'] = 0

    out = fixtures['auth.group'] + fixtures['auth.user'] + \
          fixtures['sportsrec.member'] + \
          fixtures['sportsrec.membershipapplication'] + \
          fixtures['sportsrec.clubtype'] + \
          fixtures['sportsrec.clubtag']  + \
          fixtures['sportsrec.club'] + \
          fixtures['sportsrec.membership']
          
    fpo.write(json.dumps(out, indent=4))
    

for i in range(1, len(sys.argv)):
    with open(sys.argv[i]) as fp:
        fixture = json.load(fp)
        with open(sys.argv[i] + '.sql', 'w') as fpo:
            to_sql(fixture, fpo)

        with open(sys.argv[i] + '.stripped.json', 'w') as fpo:
            strip_fixture(fixture, fpo)
            
        with open(sys.argv[i] + '.users.json', 'w') as fpo:
            users = [user for user in fixture if user['model'] == "auth.user"]
            fpo.write(json.dumps(users, indent=4))
        
        
