echo "drop table tmg_tag; drop table tmg_team; drop table tmg_testcase; drop table tmg_testcasestep; drop table tmg_tester;" | mysql -u charlie -p charlie
python manage.py syncdb
