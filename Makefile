deploy:
	./deploy.sh push_docker_image $(aws_account_id) $(tag)
	./deploy.sh deploy_environment $(environment) $(tag) $(aws_account_id) $(database_url) $(stats_user) $(stats_pass)
