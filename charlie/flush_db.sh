echo "Remaking database, enter charlie's password for mysql :"
echo 'drop table test_manager_availability; drop table test_manager_cases_sets; drop table test_manager_jira; drop table test_manager_tag; drop table test_manager_testcase; drop table test_manager_testcaserun; drop table test_manager_testcasestep; drop table test_manager_testcasestepabstract; drop table test_manager_testcasesteprun; drop table test_manager_testset; drop table test_manager_testsetrun;' | mysql -u charlie -p charlie
python manage.py syncdb
echo -e "\nrestarting apache :"
sudo service apache2 restart
