export DJANGO_SETTINGS_MODULE=settings
echo "# Remaking database..."
echo 'drop table test_manager_availability; drop table test_manager_cases_sets; drop table test_manager_jira; drop table test_manager_tag; drop table test_manager_testcase; drop table test_manager_testcaserun; drop table test_manager_testcasestep; drop table test_manager_testcasestepabstract; drop table test_manager_testcasesteprun; drop table test_manager_testset; drop table test_manager_testsetrun; drop table test_manager_config' | python manage.py dbshell
python manage.py syncdb
echo -e "\n# Entering sample data..."
python ./sample_db.py
echo -e "\n# Restarting apache..."
sudo service apache2 restart
