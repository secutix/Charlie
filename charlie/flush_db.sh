echo 'drop table test_manager_casts_sets; drop table test_manager_jira; drop table test_manager_tag; drop table test_manager_team; drop table test_manager_team_users; drop table test_manager_testcase; drop table test_manager_testcaserun; drop table test_manager_testcasestep; drop table test_manager_testcasestepabstract; drop table test_manager_testcasesteprun; drop table test_manager_testset; drop table test_manager_testsetrun; drop table test_manager_user;' | mysql -u charlie -p charlie
python manage.py syncdb
sudo service apache2 restart
