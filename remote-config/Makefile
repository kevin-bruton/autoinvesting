deploy-front:
	$(info *************************** )
	$(info ***** DEPLOYING FRONT ***** )
	$(info *************************** )
	cd autoinvesting-ui && git pull && npm run build-pro
deploy-back:
	$(info ************************** )
	$(info ***** DEPLOYING BACK ***** )
	$(info ************************** )
	systemctl stop waitress.service
	cd autoinvesting && git pull
	systemctl start waitress.service
	systemctl status waitress.service
