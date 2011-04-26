echo "drop table test_manager_jira; drop table test_manager_tag; drop table test_manager_team; drop table test_manager_team_testers; drop table test_manager_testcase; drop table test_manager_testcaseset; drop table test_manager_testcaseset_testcases; drop table test_manager_testcasestep; drop table test_manager_tester;" | mysql -u charlie -p charlie
python manage.py syncdb
sudo service apache2 restart
